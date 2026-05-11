"""
Robust Serial Executor for ComfyUI-UnlimitAI

Provides serial execution with smart delay, auto-retry, and error isolation.
Designed for API relay station constraints - NO parallel execution.
"""

import time
import traceback
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .delay import SmartDelay, RateLimiter, ExponentialBackoff
from .logger import get_logger
from .exceptions import APIError, APIRateLimitError, APITimeoutError, APIConnectionError

logger = get_logger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    attempts: int = 0
    total_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskConfig:
    task_id: str
    func: Callable
    args: tuple = ()
    kwargs: Dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    timeout: float = 300.0
    skip_on_error: bool = False
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RobustExecutor:
    """
    Serial executor with robust error handling for API relay station.
    
    Features:
    - Serial execution only (no parallel/concurrent)
    - Smart delay between tasks to avoid rate limits
    - Auto-retry with exponential backoff
    - Error isolation (one failure doesn't stop others)
    - Progress tracking integration
    """
    
    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        smart_delay: Optional[SmartDelay] = None,
        default_max_retries: int = 3,
        default_timeout: float = 300.0,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        enable_progress: bool = True,
    ):
        self.rate_limiter = rate_limiter or RateLimiter(max_calls=60, period=60.0)
        self.smart_delay = smart_delay or SmartDelay(initial_delay=base_delay)
        self.default_max_retries = default_max_retries
        self.default_timeout = default_timeout
        self.backoff = ExponentialBackoff(base_delay=base_delay, max_delay=max_delay)
        self.enable_progress = enable_progress
        
        self.results: List[TaskResult] = []
        self.total_tasks = 0
        self.completed_tasks = 0
        
    def execute_task(self, task: TaskConfig) -> TaskResult:
        result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.PENDING
        )
        
        max_retries = task.max_retries if task.max_retries is not None else self.default_max_retries
        timeout = task.timeout if task.timeout is not None else self.default_timeout
        start_time = time.time()
        
        for attempt in range(max_retries + 1):
            result.attempts = attempt + 1
            result.status = TaskStatus.RETRYING if attempt > 0 else TaskStatus.RUNNING
            
            try:
                logger.info(f"Executing task {task.task_id} (attempt {attempt + 1}/{max_retries + 1})")
                
                if not self.rate_limiter.acquire(timeout=timeout):
                    raise APITimeoutError(timeout=int(timeout), url=f"task:{task.task_id}")
                
                task_result = task.func(*task.args, **task.kwargs)
                
                result.status = TaskStatus.SUCCESS
                result.result = task_result
                result.total_time = time.time() - start_time
                
                logger.info(f"Task {task.task_id} completed successfully in {result.total_time:.2f}s")
                
                self.smart_delay.on_success()
                self._apply_smart_delay(task)
                
                return result
                
            except APIRateLimitError as e:
                logger.warning(f"Rate limit hit for task {task.task_id}: {e}")
                self.smart_delay.on_failure(is_rate_limit=True)
                
                if attempt < max_retries:
                    delay = self.backoff.get_delay(attempt)
                    logger.info(f"Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                else:
                    result.status = TaskStatus.FAILED
                    result.error = f"Rate limit exceeded after {max_retries + 1} attempts"
                    result.total_time = time.time() - start_time
                    logger.error(result.error)
                    
            except APIConnectionError as e:
                logger.warning(f"Network error for task {task.task_id}: {e}")
                self.smart_delay.on_failure()
                
                if attempt < max_retries:
                    delay = self.backoff.get_delay(attempt)
                    logger.info(f"Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                else:
                    result.status = TaskStatus.FAILED
                    result.error = f"Network error after {max_retries + 1} attempts: {str(e)}"
                    result.total_time = time.time() - start_time
                    logger.error(result.error)
                    
            except APITimeoutError as e:
                logger.warning(f"Timeout for task {task.task_id}: {e}")
                self.smart_delay.on_failure()
                
                if attempt < max_retries:
                    delay = self.backoff.get_delay(attempt)
                    logger.info(f"Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                else:
                    result.status = TaskStatus.FAILED
                    result.error = f"Timeout after {max_retries + 1} attempts"
                    result.total_time = time.time() - start_time
                    logger.error(result.error)
                    
            except APIError as e:
                logger.error(f"API error for task {task.task_id}: {e}")
                
                status_code = getattr(e, 'status_code', 0) or 0
                is_retryable = status_code in (408, 429, 500, 502, 503, 504)
                
                if is_retryable and attempt < max_retries:
                    delay = self.backoff.get_delay(attempt)
                    logger.info(f"Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                else:
                    result.status = TaskStatus.FAILED
                    result.error = f"API error: {str(e)}"
                    result.total_time = time.time() - start_time
                    logger.error(result.error)
                    break
                    
            except (TypeError, AttributeError, KeyError, ValueError, ImportError) as e:
                logger.error(f"Programming error for task {task.task_id}: {e}")
                result.status = TaskStatus.FAILED
                result.error = f"Programming error: {str(e)}"
                result.total_time = time.time() - start_time
                break
                    
            except Exception as e:
                logger.error(f"Unexpected error for task {task.task_id}: {e}\n{traceback.format_exc()}")
                result.status = TaskStatus.FAILED
                result.error = f"Unexpected error: {str(e)}"
                result.total_time = time.time() - start_time
                
                if attempt < max_retries:
                    delay = self.backoff.get_delay(attempt)
                    logger.info(f"Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                else:
                    break
        
        return result
    
    def execute_serial(
        self,
        tasks: List[TaskConfig],
        stop_on_failure: bool = False,
        progress_callback: Optional[Callable[[int, int, TaskResult], None]] = None,
    ) -> List[TaskResult]:
        self.total_tasks = len(tasks)
        self.completed_tasks = 0
        self.results = []
        
        logger.info(f"Starting serial execution of {self.total_tasks} tasks")
        
        for idx, task in enumerate(tasks):
            logger.info(f"Processing task {idx + 1}/{self.total_tasks}: {task.task_id}")
            
            result = self.execute_task(task)
            self.results.append(result)
            self.completed_tasks += 1
            
            if progress_callback:
                progress_callback(self.completed_tasks, self.total_tasks, result)
            
            if result.status == TaskStatus.FAILED and stop_on_failure:
                logger.error(f"Stopping execution due to task failure: {task.task_id}")
                break
        
        self._log_summary()
        return self.results
    
    def _apply_smart_delay(self, task: TaskConfig):
        self.smart_delay.wait(operation=task.metadata.get("task_type", "operation"))
    
    def _log_summary(self):
        success_count = sum(1 for r in self.results if r.status == TaskStatus.SUCCESS)
        failed_count = sum(1 for r in self.results if r.status == TaskStatus.FAILED)
        skipped_count = sum(1 for r in self.results if r.status == TaskStatus.SKIPPED)
        total_time = sum(r.total_time for r in self.results)
        
        logger.info("=" * 60)
        logger.info("Execution Summary:")
        logger.info(f"  Total tasks: {self.total_tasks}")
        logger.info(f"  Successful: {success_count}")
        logger.info(f"  Failed: {failed_count}")
        logger.info(f"  Skipped: {skipped_count}")
        logger.info(f"  Total time: {total_time:.2f}s")
        logger.info(f"  Average time per task: {total_time / max(1, self.total_tasks):.2f}s")
        logger.info("=" * 60)
    
    def get_success_rate(self) -> float:
        if not self.results:
            return 0.0
        success_count = sum(1 for r in self.results if r.status == TaskStatus.SUCCESS)
        return success_count / len(self.results)
    
    def get_results_by_status(self, status: TaskStatus) -> List[TaskResult]:
        return [r for r in self.results if r.status == status]


class WorkflowExecutor(RobustExecutor):
    """
    Specialized executor for ComfyUI workflows.
    
    Extends RobustExecutor with workflow-specific features:
    - Batch task creation from workflow nodes
    - Scene-based execution
    - Integration with smart skip and deduplication
    """
    
    def __init__(
        self,
        smart_skip=None,
        content_dedup=None,
        progress_tracker=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.smart_skip = smart_skip
        self.content_dedup = content_dedup
        self.progress_tracker = progress_tracker
    
    def _should_skip_task(self, task: TaskConfig) -> Optional[str]:
        if not self.smart_skip:
            return None
        
        task_type = task.metadata.get("task_type", "default")
        scene = task.metadata
        
        should_gen = True
        reason = ""
        
        if task_type == "image":
            should_gen, reason = self.smart_skip.should_generate_image(scene)
        elif task_type == "video":
            should_gen, reason = self.smart_skip.should_generate_video(scene)
        elif task_type == "audio":
            should_gen, reason = self.smart_skip.should_generate_audio(scene)
        elif task_type == "music":
            should_gen, reason = self.smart_skip.should_generate_music(scene)
        else:
            return None
        
        if not should_gen:
            return reason
        return None
    
    def create_image_task(
        self,
        task_id: str,
        func: Callable,
        prompt: str,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
        **task_kwargs
    ) -> TaskConfig:
        return TaskConfig(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs or {},
            metadata={
                "task_type": "image",
                "prompt": prompt,
                **{k: v for k, v in task_kwargs.items() if k not in ('max_retries', 'timeout', 'priority')}
            },
            **{k: v for k, v in task_kwargs.items() if k in ('max_retries', 'timeout', 'priority')}
        )
    
    def create_video_task(
        self,
        task_id: str,
        func: Callable,
        prompt: str,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
        **task_kwargs
    ) -> TaskConfig:
        return TaskConfig(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs or {},
            metadata={
                "task_type": "video",
                "prompt": prompt,
                **{k: v for k, v in task_kwargs.items() if k not in ('max_retries', 'timeout', 'priority')}
            },
            **{k: v for k, v in task_kwargs.items() if k in ('max_retries', 'timeout', 'priority')}
        )
    
    def execute_with_skip_check(
        self,
        tasks: List[TaskConfig],
        stop_on_failure: bool = False,
        progress_callback: Optional[Callable[[int, int, TaskResult], None]] = None,
    ) -> List[TaskResult]:
        if not self.smart_skip:
            return self.execute_serial(tasks, stop_on_failure, progress_callback)
        
        skipped_map: Dict[str, TaskResult] = {}
        filtered_tasks = []
        
        for task in tasks:
            skip_reason = self._should_skip_task(task)
            
            if skip_reason:
                result = TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.SKIPPED,
                    metadata={"skip_reason": skip_reason}
                )
                skipped_map[task.task_id] = result
                logger.info(f"Task {task.task_id} skipped by smart skip: {skip_reason}")
            else:
                filtered_tasks.append(task)
        
        executed_results = self.execute_serial(filtered_tasks, stop_on_failure, progress_callback)
        executed_map = {r.task_id: r for r in executed_results}
        
        all_results = []
        for task in tasks:
            if task.task_id in skipped_map:
                all_results.append(skipped_map[task.task_id])
            elif task.task_id in executed_map:
                all_results.append(executed_map[task.task_id])
        
        return all_results


def create_executor_from_config(config: Dict[str, Any]) -> RobustExecutor:
    rate_limit_config = config.get("rate_limit", {})
    rpm = rate_limit_config.get("requests_per_minute", 60)
    rate_limiter = RateLimiter(
        max_calls=rpm,
        period=60.0
    )
    
    delay_config = config.get("delay", {})
    smart_delay = SmartDelay(
        initial_delay=delay_config.get("base_delay", 1.0),
        max_delay=delay_config.get("max_delay", 30.0)
    )
    
    executor_config = config.get("executor", {})
    
    return RobustExecutor(
        rate_limiter=rate_limiter,
        smart_delay=smart_delay,
        default_max_retries=executor_config.get("max_retries", 3),
        default_timeout=executor_config.get("timeout", 300.0),
        base_delay=delay_config.get("base_delay", 1.0),
        max_delay=delay_config.get("max_delay", 60.0),
        enable_progress=executor_config.get("enable_progress", True)
    )
