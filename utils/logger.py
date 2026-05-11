"""
统一日志系统

特性：
- 支持不同日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 支持文件输出和日志轮转
- 支持彩色控制台输出
- 支持结构化日志
- 性能优化

使用方法:
    from utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("这是一条信息")
    logger.error("这是一条错误", exc_info=True)
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional
import os


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 保存原始levelname
        orig_levelname = record.levelname
        
        # 添加颜色
        if record.levelname in self.COLORS and sys.stdout.isatty():
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname:8s}"
                f"{self.RESET}"
            )
        
        # 格式化
        result = super().format(record)
        
        # 恢复原始levelname
        record.levelname = orig_levelname
        
        return result


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器（JSON格式）"""
    
    def format(self, record):
        import json
        
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加额外字段
        if hasattr(record, 'data'):
            log_obj['data'] = record.data
        
        # 添加异常信息
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj, ensure_ascii=False)


def get_logger(
    name: str = "UnlimitAI",
    level: str = None,
    log_file: Optional[str] = None,
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    use_colors: bool = True,
    use_structured: bool = False
) -> logging.Logger:
    """
    获取或创建日志器
    
    Args:
        name: 日志器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选）
        max_size: 单个日志文件最大大小（字节）
        backup_count: 保留的日志文件数量
        use_colors: 是否使用彩色输出
        use_structured: 是否使用结构化日志（JSON格式）
    
    Returns:
        配置好的日志器
    
    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("操作成功")
        >>> logger.error("操作失败", exc_info=True)
        
        >>> # 带额外数据
        >>> logger.info("用户登录", extra={"data": {"user_id": 123}})
    """
    # 从环境变量获取日志级别
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO')
    
    logger = logging.getLogger(name)
    
    # 如果已经有处理器，直接返回
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # 防止日志传播到根日志器
    logger.propagate = False
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if use_structured:
        console_format = StructuredFormatter()
    elif use_colors and sys.stdout.isatty():
        console_format = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 按大小轮转
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 文件使用详细格式
        if use_structured:
            file_format = StructuredFormatter()
        else:
            file_format = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | '
                '%(filename)s:%(lineno)d | %(funcName)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def log_function_call(logger: logging.Logger):
    """
    函数调用日志装饰器
    
    Examples:
        >>> @log_function_call(logger)
        ... def my_function(x, y):
        ...     return x + y
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"调用函数: {func_name}, 参数: args={args}, kwargs={kwargs}")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"函数 {func_name} 执行成功")
                return result
            except Exception as e:
                logger.error(f"函数 {func_name} 执行失败: {e}", exc_info=True)
                raise
        
        return wrapper
    return decorator


def log_execution_time(logger: logging.Logger):
    """
    执行时间日志装饰器
    
    Examples:
        >>> @log_execution_time(logger)
        ... def slow_function():
        ...     time.sleep(1)
    """
    import time
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"{func.__name__} 执行完成，耗时: {execution_time:.2f}秒"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} 执行失败，耗时: {execution_time:.2f}秒",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


class LoggerContext:
    """
    日志上下文管理器
    
    Examples:
        >>> with LoggerContext(logger, "处理用户请求"):
        ...     # 处理逻辑
        ...     pass
    """
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.info(f"开始: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        execution_time = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"完成: {self.operation}，耗时: {execution_time:.2f}秒"
            )
        else:
            self.logger.error(
                f"失败: {self.operation}，耗时: {execution_time:.2f}秒",
                exc_info=True
            )
        
        return False  # 不抑制异常


# 创建默认日志器
default_logger = get_logger(
    name="UnlimitAI",
    log_file="logs/unlimitai.log"
)


# 便捷函数
def debug(msg, *args, **kwargs):
    """记录DEBUG日志"""
    default_logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    """记录INFO日志"""
    default_logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    """记录WARNING日志"""
    default_logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    """记录ERROR日志"""
    default_logger.error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    """记录CRITICAL日志"""
    default_logger.critical(msg, *args, **kwargs)


if __name__ == "__main__":
    # 演示日志功能
    logger = get_logger("Demo", level="DEBUG", log_file="logs/demo.log")
    
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误")
    
    # 带额外数据
    logger.info("用户登录", extra={"data": {"user_id": 123, "ip": "192.168.1.1"}})
    
    # 使用装饰器
    @log_execution_time(logger)
    def slow_function():
        import time
        time.sleep(0.1)
        return "done"
    
    result = slow_function()
    
    # 使用上下文管理器
    with LoggerContext(logger, "处理请求"):
        import time
        time.sleep(0.1)
