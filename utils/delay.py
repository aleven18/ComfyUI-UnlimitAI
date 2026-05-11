"""
智能延迟系统

特性：
- 自适应延迟（根据API响应动态调整）
- 指数退避重试
- 抖动策略（防止惊群效应）
- 可配置的延迟策略
- 支持异步

使用方法:
    from utils.delay import SmartDelay, delay
    
    # 简单延迟
    delay(1.0)
    
    # 智能延迟
    smart_delay = SmartDelay()
    smart_delay.wait("api_call")
    
    # 重试装饰器
    @retry_on_failure(max_retries=3)
    def api_call():
        ...
"""

import time
import random
import asyncio
from typing import Optional, Callable, Any, Tuple
from functools import wraps
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DelayConfig:
    """延迟配置"""
    min_delay: float = 0.1
    max_delay: float = 60.0
    initial_delay: float = 1.0
    multiplier: float = 2.0
    jitter: float = 0.1
    
    def validate(self):
        """验证配置"""
        assert self.min_delay > 0, "min_delay必须大于0"
        assert self.max_delay > self.min_delay, "max_delay必须大于min_delay"
        assert self.initial_delay >= self.min_delay, "initial_delay必须大于等于min_delay"
        assert self.multiplier > 1.0, "multiplier必须大于1.0"
        assert 0.0 <= self.jitter < 1.0, "jitter必须在[0, 1)范围内"


class SmartDelay:
    """
    智能延迟管理器
    
    根据API响应和错误率自动调整延迟时间
    
    Examples:
        >>> delay = SmartDelay()
        >>> 
        >>> # 成功后调用
        >>> delay.on_success()
        >>> 
        >>> # 失败后调用
        >>> delay.on_failure()
        >>> 
        >>> # 等待
        >>> delay.wait()
    """
    
    def __init__(
        self,
        config: Optional[DelayConfig] = None,
        min_delay: float = 0.1,
        max_delay: float = 60.0,
        initial_delay: float = 1.0,
        multiplier: float = 2.0,
        jitter: float = 0.1
    ):
        self.config = config or DelayConfig(
            min_delay=min_delay,
            max_delay=max_delay,
            initial_delay=initial_delay,
            multiplier=multiplier,
            jitter=jitter
        )
        
        self.config.validate()
        
        self.current_delay = self.config.initial_delay
        self.success_count = 0
        self.failure_count = 0
        self.last_adjustment = time.time()
    
    def wait(self, operation: str = "operation") -> float:
        """
        等待
        
        Args:
            operation: 操作名称（用于日志）
        
        Returns:
            实际等待时间（秒）
        """
        # 添加抖动
        jitter_amount = self.current_delay * self.config.jitter
        actual_delay = self.current_delay + random.uniform(-jitter_amount, jitter_amount)
        
        # 确保在范围内
        actual_delay = max(self.config.min_delay, min(actual_delay, self.config.max_delay))
        
        logger.debug(f"等待 {actual_delay:.2f}秒 (操作: {operation})")
        time.sleep(actual_delay)
        
        return actual_delay
    
    async def wait_async(self, operation: str = "operation") -> float:
        """
        异步等待
        
        Args:
            operation: 操作名称
        
        Returns:
            实际等待时间（秒）
        """
        jitter_amount = self.current_delay * self.config.jitter
        actual_delay = self.current_delay + random.uniform(-jitter_amount, jitter_amount)
        actual_delay = max(self.config.min_delay, min(actual_delay, self.config.max_delay))
        
        logger.debug(f"异步等待 {actual_delay:.2f}秒 (操作: {operation})")
        await asyncio.sleep(actual_delay)
        
        return actual_delay
    
    def on_success(self):
        """
        成功回调
        
        成功后降低延迟时间
        """
        self.success_count += 1
        
        # 每次成功后降低延迟
        self.current_delay = max(
            self.config.min_delay,
            self.current_delay / self.config.multiplier
        )
        
        logger.debug(
            f"操作成功，降低延迟至 {self.current_delay:.2f}秒 "
            f"(成功: {self.success_count}, 失败: {self.failure_count})"
        )
    
    def on_failure(self, is_rate_limit: bool = False):
        """
        失败回调
        
        Args:
            is_rate_limit: 是否是频率限制错误
        
        失败后增加延迟时间
        """
        self.failure_count += 1
        
        # 频率限制错误增加更多延迟
        if is_rate_limit:
            self.current_delay = min(
                self.config.max_delay,
                self.current_delay * self.config.multiplier * 2
            )
        else:
            self.current_delay = min(
                self.config.max_delay,
                self.current_delay * self.config.multiplier
            )
        
        logger.warning(
            f"操作失败，增加延迟至 {self.current_delay:.2f}秒 "
            f"(成功: {self.success_count}, 失败: {self.failure_count})"
        )
    
    def reset(self):
        """重置延迟"""
        self.current_delay = self.config.initial_delay
        self.success_count = 0
        self.failure_count = 0
        self.last_adjustment = time.time()
        
        logger.info("延迟已重置")
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "current_delay": self.current_delay,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": (
                self.success_count / (self.success_count + self.failure_count)
                if (self.success_count + self.failure_count) > 0
                else 0.0
            )
        }


class ExponentialBackoff:
    """
    指数退避
    
    用于重试机制
    
    Examples:
        >>> backoff = ExponentialBackoff()
        >>> 
        >>> for attempt in range(5):
        ...     try:
        ...         risky_operation()
        ...         break
        ...     except Exception as e:
        ...         backoff.wait(attempt)
    """
    
    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """
        获取延迟时间
        
        Args:
            attempt: 尝试次数（从0开始）
        
        Returns:
            延迟时间（秒）
        """
        # 计算指数延迟
        delay = self.base_delay * (self.exponential_base ** attempt)
        
        # 添加抖动
        if self.jitter:
            delay = random.uniform(0, delay)
        
        # 限制最大延迟
        delay = min(delay, self.max_delay)
        
        return delay
    
    def wait(self, attempt: int) -> float:
        """
        等待
        
        Args:
            attempt: 尝试次数
        
        Returns:
            实际等待时间
        """
        delay = self.get_delay(attempt)
        logger.debug(f"第{attempt + 1}次重试，等待 {delay:.2f}秒")
        time.sleep(delay)
        return delay
    
    async def wait_async(self, attempt: int) -> float:
        """异步等待"""
        delay = self.get_delay(attempt)
        logger.debug(f"第{attempt + 1}次重试，异步等待 {delay:.2f}秒")
        await asyncio.sleep(delay)
        return delay


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    失败重试装饰器
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        exponential_base: 指数基数
        exceptions: 需要重试的异常类型
        on_retry: 重试回调函数
    
    Returns:
        装饰器
    
    Examples:
        >>> @retry_on_failure(max_retries=3, base_delay=1.0)
        ... def unreliable_function():
        ...     if random.random() < 0.5:
        ...         raise Exception("随机失败")
        ...     return "成功"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            backoff = ExponentialBackoff(
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base
            )
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # 调用重试回调
                        if on_retry:
                            on_retry(attempt, e)
                        
                        # 等待后重试
                        backoff.wait(attempt)
                    else:
                        logger.error(
                            f"函数 {func.__name__} 重试{max_retries}次后仍然失败: {e}"
                        )
                        raise
            
            # 理论上不会到达这里
            raise last_exception
        
        return wrapper
    return decorator


def retry_on_failure_async(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    异步失败重试装饰器
    
    Examples:
        >>> @retry_on_failure_async(max_retries=3)
        ... async def unreliable_async_function():
        ...     if random.random() < 0.5:
        ...         raise Exception("随机失败")
        ...     return "成功"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            backoff = ExponentialBackoff(
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base
            )
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        if on_retry:
                            await on_retry(attempt, e)
                        
                        await backoff.wait_async(attempt)
                    else:
                        logger.error(
                            f"异步函数 {func.__name__} 重试{max_retries}次后仍然失败: {e}"
                        )
                        raise
            
            raise last_exception
        
        return wrapper
    return decorator


class RateLimiter:
    """
    频率限制器
    
    限制操作频率，避免触发API限制
    
    Examples:
        >>> limiter = RateLimiter(max_calls=10, period=1.0)
        >>> 
        >>> for i in range(20):
        ...     limiter.acquire()
        ...     make_api_call()
    """
    
    def __init__(self, max_calls: int, period: float = 1.0):
        """
        Args:
            max_calls: 时间窗口内最大调用次数
            period: 时间窗口（秒）
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        获取调用许可
        
        Args:
            timeout: 超时时间（秒），None表示无限等待
        
        Returns:
            是否成功获取许可
        """
        start_time = time.time()
        
        while True:
            now = time.time()
            
            # 移除过期的调用记录
            self.calls = [call for call in self.calls if now - call < self.period]
            
            # 检查是否可以调用
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            
            # 检查超时
            if timeout is not None and (time.time() - start_time) >= timeout:
                return False
            
            # 等待
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(min(sleep_time, 0.1))
    
    async def acquire_async(self, timeout: Optional[float] = None) -> bool:
        """异步获取调用许可"""
        start_time = time.time()
        
        while True:
            now = time.time()
            
            self.calls = [call for call in self.calls if now - call < self.period]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            
            if timeout is not None and (time.time() - start_time) >= timeout:
                return False
            
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                await asyncio.sleep(min(sleep_time, 0.1))


# 全局延迟管理器
_global_delay: Optional[SmartDelay] = None


def get_global_delay() -> SmartDelay:
    """获取全局延迟管理器"""
    global _global_delay
    if _global_delay is None:
        _global_delay = SmartDelay()
    return _global_delay


def delay(seconds: float, operation: str = "operation"):
    """
    简单延迟
    
    Args:
        seconds: 延迟时间（秒）
        operation: 操作名称
    
    Examples:
        >>> delay(1.0, "API调用")
    """
    logger.debug(f"延迟 {seconds:.2f}秒 (操作: {operation})")
    time.sleep(seconds)


async def delay_async(seconds: float, operation: str = "operation"):
    """异步延迟"""
    logger.debug(f"异步延迟 {seconds:.2f}秒 (操作: {operation})")
    await asyncio.sleep(seconds)


if __name__ == "__main__":
    # 演示智能延迟系统
    print("演示智能延迟系统")
    print("=" * 60)
    
    # 1. 智能延迟
    print("\n1. 智能延迟")
    smart_delay = SmartDelay(initial_delay=0.5, max_delay=5.0)
    
    for i in range(5):
        delay_time = smart_delay.wait("测试操作")
        print(f"第{i+1}次延迟: {delay_time:.2f}秒")
        
        if i < 2:
            smart_delay.on_failure()
        else:
            smart_delay.on_success()
    
    print(f"\n统计信息: {smart_delay.get_stats()}")
    
    # 2. 指数退避
    print("\n2. 指数退避")
    backoff = ExponentialBackoff(base_delay=0.5, max_delay=5.0)
    
    for attempt in range(5):
        delay_time = backoff.get_delay(attempt)
        print(f"尝试 {attempt}: 延迟 {delay_time:.2f}秒")
    
    # 3. 频率限制器
    print("\n3. 频率限制器")
    limiter = RateLimiter(max_calls=3, period=2.0)
    
    for i in range(5):
        acquired = limiter.acquire(timeout=5.0)
        print(f"调用 {i+1}: {'成功' if acquired else '超时'}")
    
    # 4. 重试装饰器
    print("\n4. 重试装饰器")
    
    call_count = 0
    
    @retry_on_failure(max_retries=3, base_delay=0.5)
    def unreliable_function():
        global call_count
        call_count += 1
        
        if call_count < 3:
            raise Exception(f"第{call_count}次失败")
        
        return "成功"
    
    try:
        result = unreliable_function()
        print(f"函数调用成功: {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")
