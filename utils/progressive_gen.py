"""
Progressive Generation Module for ComfyUI-UnlimitAI

Implements progressive/batch generation with serial execution constraints.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .logger import get_logger
from .robust_executor import RobustExecutor, TaskConfig, TaskResult, TaskStatus
from .progress_tracker import ProgressTracker

logger = get_logger(__name__)


class GenerationType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"


class BatchStrategy(Enum):
    SEQUENTIAL = "sequential"
    PRIORITY = "priority"
    SCENE_BASED = "scene_based"


@dataclass
class GenerationTask:
    task_type: GenerationType
    prompt: str
    params: Dict[str, Any]
    task_id: Optional[str] = None
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchResult:
    total_tasks: int
    successful: int
    failed: int
    skipped: int
    results: List[TaskResult]
    total_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProgressiveGenerator:
    """
    Progressive generation manager with serial execution.
    
    Features:
    - Scene-based generation (image -> video -> audio)
    - Batch processing with progress tracking
    - Priority-based execution
    - Integration with smart skip and deduplication
    """
    
    def __init__(
        self,
        executor: Optional[RobustExecutor] = None,
        smart_skip=None,
        content_dedup=None,
        progress_tracker=None,
        enable_dedup: bool = True,
    ):
        self.executor = executor or RobustExecutor()
        self.smart_skip = smart_skip
        self.content_dedup = content_dedup
        self.progress_tracker = progress_tracker
        self.enable_dedup = enable_dedup
        
        self._task_factories: Dict[GenerationType, Callable] = {}
    
    def _get_or_create_tracker(self, total: int, name: str = "batch_generation") -> Tuple[ProgressTracker, bool]:
        """Get or create a progress tracker.
        
        Returns (tracker, owns_tracker) where owns_tracker indicates
        whether the caller should manage start/finish lifecycle.
        """
        if self.progress_tracker:
            return self.progress_tracker, False
        return ProgressTracker(total_tasks=total, stage_name=name), True
    
    def register_task_factory(
        self,
        generation_type: GenerationType,
        factory: Callable[[GenerationTask], TaskConfig]
    ):
        self._task_factories[generation_type] = factory
        logger.info(f"Registered task factory for {generation_type.value}")
    
    def _check_smart_skip(self, task: GenerationTask) -> Optional[str]:
        if not self.smart_skip:
            return None
        
        scene = {"prompt": task.prompt, **task.params, **task.metadata}
        
        should_gen = True
        reason = ""
        
        if task.task_type == GenerationType.IMAGE:
            should_gen, reason = self.smart_skip.should_generate_image(scene)
        elif task.task_type == GenerationType.VIDEO:
            should_gen, reason = self.smart_skip.should_generate_video(scene)
        elif task.task_type == GenerationType.AUDIO:
            should_gen, reason = self.smart_skip.should_generate_audio(scene)
        elif task.task_type == GenerationType.MUSIC:
            should_gen, reason = self.smart_skip.should_generate_music(scene)
        
        if not should_gen:
            return reason
        return None
    
    def _check_dedup(self, task: GenerationTask) -> Optional[Any]:
        if not self.enable_dedup or not self.content_dedup:
            return None
        
        content = f"{task.task_type.value}:{task.prompt}:{sorted(task.params.items())}"
        
        try:
            cached = self.content_dedup.check_exists(content, content_type=task.task_type.value)
            if cached:
                return cached
        except Exception:
            pass
        
        return None
    
    def _store_dedup(self, task: GenerationTask, generated_result: Any):
        if not self.enable_dedup or not self.content_dedup:
            return
        
        content = f"{task.task_type.value}:{task.prompt}:{sorted(task.params.items())}"
        
        try:
            self.content_dedup.store(content, result={"data": generated_result}, content_type=task.task_type.value)
        except Exception:
            pass
    
    def generate_single(
        self,
        task: GenerationTask,
        skip_check: bool = True,
    ) -> TaskResult:
        if skip_check:
            skip_reason = self._check_smart_skip(task)
            if skip_reason:
                logger.info(f"Skipping task {task.task_id}: {skip_reason}")
                return TaskResult(
                    task_id=task.task_id or "unknown",
                    status=TaskStatus.SKIPPED,
                    metadata={"skip_reason": skip_reason}
                )
        
        if self.enable_dedup:
            existing = self._check_dedup(task)
            if existing:
                logger.info(f"Found existing content for task {task.task_id}")
                return TaskResult(
                    task_id=task.task_id or "unknown",
                    status=TaskStatus.SKIPPED,
                    result=existing,
                    metadata={"skip_reason": "duplicate"}
                )
        
        factory = self._task_factories.get(task.task_type)
        if not factory:
            raise ValueError(f"No factory registered for {task.task_type}")
        
        task_config = factory(task)
        
        result = self.executor.execute_task(task_config)
        
        if result.status == TaskStatus.SUCCESS and self.enable_dedup:
            self._store_dedup(task, result.result)
        
        return result
    
    def generate_batch(
        self,
        tasks: List[GenerationTask],
        strategy: BatchStrategy = BatchStrategy.SEQUENTIAL,
        stop_on_failure: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> BatchResult:
        start_time = time.time()
        
        if strategy == BatchStrategy.PRIORITY:
            tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        elif strategy == BatchStrategy.SCENE_BASED:
            tasks = self._sort_by_scene_order(tasks)
        
        tracker, owns_tracker = self._get_or_create_tracker(len(tasks))
        if owns_tracker:
            tracker.start("Batch generation")
        
        results = []
        for idx, task in enumerate(tasks):
            if not task.task_id:
                task.task_id = f"{task.task_type.value}_{idx}_{int(time.time())}"
            
            logger.info(f"Processing batch task {idx + 1}/{len(tasks)}: {task.task_id}")
            
            result = self.generate_single(task)
            results.append(result)
            
            tracker.update(f"Task {task.task_id}", completed=idx + 1)
            
            if progress_callback:
                progress_callback(idx + 1, len(tasks))
            
            if result.status == TaskStatus.FAILED and stop_on_failure:
                logger.error(f"Stopping batch due to failure: {task.task_id}")
                break
        
        total_time = time.time() - start_time
        
        successful = sum(1 for r in results if r.status == TaskStatus.SUCCESS)
        failed = sum(1 for r in results if r.status == TaskStatus.FAILED)
        skipped = sum(1 for r in results if r.status == TaskStatus.SKIPPED)
        
        if owns_tracker:
            tracker.finish()
        
        batch_result = BatchResult(
            total_tasks=len(tasks),
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=results,
            total_time=total_time
        )
        
        self._log_batch_summary(batch_result)
        
        return batch_result
    
    def generate_scene(
        self,
        scene_config: Dict[str, Any],
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> Dict[str, TaskResult]:
        results = {}
        scene_id = scene_config.get("scene_id", f"scene_{int(time.time())}")
        
        logger.info(f"Starting scene generation: {scene_id}")
        
        if "image" in scene_config:
            task = GenerationTask(
                task_type=GenerationType.IMAGE,
                task_id=f"{scene_id}_image",
                prompt=scene_config["image"]["prompt"],
                params=scene_config["image"].get("params", {}),
                metadata={"scene_id": scene_id}
            )
            
            if progress_callback:
                progress_callback("image", 0, 1)
            
            results["image"] = self.generate_single(task)
            
            if progress_callback:
                progress_callback("image", 1, 1)
        
        image_success = results.get("image", TaskResult(task_id="", status=TaskStatus.SUCCESS)).status == TaskStatus.SUCCESS
        if "video" in scene_config and image_success:
            video_task = GenerationTask(
                task_type=GenerationType.VIDEO,
                task_id=f"{scene_id}_video",
                prompt=scene_config["video"]["prompt"],
                params=scene_config["video"].get("params", {}),
                metadata={"scene_id": scene_id, "image_result": results.get("image")}
            )
            
            if progress_callback:
                progress_callback("video", 0, 1)
            
            results["video"] = self.generate_single(video_task)
            
            if progress_callback:
                progress_callback("video", 1, 1)
        
        for audio_type in ["audio", "music"]:
            if audio_type in scene_config:
                task = GenerationTask(
                    task_type=GenerationType.AUDIO if audio_type == "audio" else GenerationType.MUSIC,
                    task_id=f"{scene_id}_{audio_type}",
                    prompt=scene_config[audio_type]["prompt"],
                    params=scene_config[audio_type].get("params", {}),
                    metadata={"scene_id": scene_id, "video_result": results.get("video")}
                )
                
                if progress_callback:
                    progress_callback(audio_type, 0, 1)
                
                results[audio_type] = self.generate_single(task)
                
                if progress_callback:
                    progress_callback(audio_type, 1, 1)
        
        self._log_scene_summary(scene_id, results)
        
        return results
    
    def _sort_by_scene_order(self, tasks: List[GenerationTask]) -> List[GenerationTask]:
        order = {
            GenerationType.IMAGE: 0,
            GenerationType.VIDEO: 1,
            GenerationType.AUDIO: 2,
            GenerationType.MUSIC: 2,
        }
        return sorted(tasks, key=lambda t: (order.get(t.task_type, 999), -t.priority))
    
    def _log_batch_summary(self, result: BatchResult):
        logger.info("=" * 60)
        logger.info("Batch Generation Summary:")
        logger.info(f"  Total tasks: {result.total_tasks}")
        logger.info(f"  Successful: {result.successful}")
        logger.info(f"  Failed: {result.failed}")
        logger.info(f"  Skipped: {result.skipped}")
        logger.info(f"  Success rate: {result.successful / max(1, result.total_tasks) * 100:.1f}%")
        logger.info(f"  Total time: {result.total_time:.2f}s")
        logger.info(f"  Avg time per task: {result.total_time / max(1, result.total_tasks):.2f}s")
        logger.info("=" * 60)
    
    def _log_scene_summary(self, scene_id: str, results: Dict[str, TaskResult]):
        logger.info(f"Scene {scene_id} generation completed:")
        for task_type, result in results.items():
            status = result.status.value
            logger.info(f"  {task_type}: {status}")


class WorkflowProgressiveGenerator(ProgressiveGenerator):
    """
    Specialized progressive generator for ComfyUI workflows.
    
    Integrates with workflow nodes and provides high-level API
    for common generation patterns.
    """
    
    def __init__(self, workflow_node=None, **kwargs):
        super().__init__(**kwargs)
        self.workflow_node = workflow_node
    
    def generate_images_batch(
        self,
        prompts: List[str],
        params_list: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> BatchResult:
        tasks = []
        params_list = params_list or [{}] * len(prompts)
        
        for idx, (prompt, params) in enumerate(zip(prompts, params_list)):
            task = GenerationTask(
                task_type=GenerationType.IMAGE,
                task_id=f"image_{idx}",
                prompt=prompt,
                params={**params, **kwargs}
            )
            tasks.append(task)
        
        return self.generate_batch(tasks)
    
    def generate_videos_batch(
        self,
        prompts: List[str],
        params_list: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> BatchResult:
        tasks = []
        params_list = params_list or [{}] * len(prompts)
        
        for idx, (prompt, params) in enumerate(zip(prompts, params_list)):
            task = GenerationTask(
                task_type=GenerationType.VIDEO,
                task_id=f"video_{idx}",
                prompt=prompt,
                params={**params, **kwargs}
            )
            tasks.append(task)
        
        return self.generate_batch(tasks)
    
    def generate_content_pack(
        self,
        pack_config: Dict[str, Any],
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> Dict[str, Any]:
        results = {
            "images": [],
            "videos": [],
            "audio": [],
            "music": [],
            "metadata": {
                "pack_id": pack_config.get("pack_id", f"pack_{int(time.time())}"),
                "created_at": time.time()
            }
        }
        
        if "scenes" in pack_config:
            for idx, scene in enumerate(pack_config["scenes"]):
                scene_results = self.generate_scene(
                    scene,
                    lambda t, c, total: progress_callback(f"scene_{idx}_{t}", c, total) if progress_callback else None
                )
                
                for key in ["image", "video", "audio", "music"]:
                    if key in scene_results:
                        dest_key = f"{key}s" if key in ("image", "video") else key
                        results[dest_key].append(scene_results[key])
        
        else:
            for content_type in ["images", "videos", "audio", "music"]:
                if content_type in pack_config:
                    prompts = pack_config[content_type].get("prompts", [])
                    params = pack_config[content_type].get("params", {})
                    
                    task_type = {
                        "images": GenerationType.IMAGE,
                        "videos": GenerationType.VIDEO,
                        "audio": GenerationType.AUDIO,
                        "music": GenerationType.MUSIC,
                    }[content_type]
                    
                    tasks = [
                        GenerationTask(
                            task_type=task_type,
                            task_id=f"{content_type}_{idx}",
                            prompt=prompt,
                            params=params
                        )
                        for idx, prompt in enumerate(prompts)
                    ]
                    
                    batch_result = self.generate_batch(tasks)
                    results[content_type] = batch_result.results
        
        return results
