"""
统一异常处理体系

特性：
- 分层异常设计（基础异常 -> 领域异常 -> 具体异常）
- 错误代码和错误信息分离
- 支持错误上下文
- 支持错误链
- 支持国际化

使用方法:
    from utils.exceptions import (
        UnlimitAIError,
        APIError,
        ValidationError,
        handle_errors
    )
    
    raise ValidationError("参数不能为空", code="E001")
"""

from typing import Optional, Dict, Any, List
from functools import wraps
import traceback
import sys
import builtins


class ErrorCodes:
    """错误代码枚举"""
    
    # 通用错误 (1xxx)
    UNKNOWN_ERROR = "E1000"
    INVALID_PARAMETER = "E1001"
    MISSING_PARAMETER = "E1002"
    TYPE_ERROR = "E1003"
    VALUE_ERROR = "E1004"
    
    # API错误 (2xxx)
    API_ERROR = "E2000"
    API_CONNECTION_ERROR = "E2001"
    API_TIMEOUT_ERROR = "E2002"
    API_AUTH_ERROR = "E2003"
    API_RATE_LIMIT = "E2004"
    API_SERVER_ERROR = "E2005"
    API_RESPONSE_ERROR = "E2006"
    
    # 文件错误 (3xxx)
    FILE_ERROR = "E3000"
    FILE_NOT_FOUND = "E3001"
    FILE_READ_ERROR = "E3002"
    FILE_WRITE_ERROR = "E3003"
    FILE_FORMAT_ERROR = "E3004"
    
    # 处理错误 (4xxx)
    PROCESSING_ERROR = "E4000"
    TEXT_GENERATION_ERROR = "E4001"
    IMAGE_GENERATION_ERROR = "E4002"
    VIDEO_GENERATION_ERROR = "E4003"
    AUDIO_GENERATION_ERROR = "E4004"
    MUSIC_GENERATION_ERROR = "E4005"
    
    # 资源错误 (5xxx)
    RESOURCE_ERROR = "E5000"
    INSUFFICIENT_MEMORY = "E5001"
    INSUFFICIENT_STORAGE = "E5002"
    GPU_ERROR = "E5003"
    
    # 配置错误 (6xxx)
    CONFIG_ERROR = "E6000"
    MISSING_API_KEY = "E6001"
    INVALID_CONFIG = "E6002"


class ErrorMessages:
    """错误消息映射（支持国际化）"""
    
    MESSAGES = {
        # 通用错误
        ErrorCodes.UNKNOWN_ERROR: "未知错误",
        ErrorCodes.INVALID_PARAMETER: "参数无效: {param}",
        ErrorCodes.MISSING_PARAMETER: "缺少必需参数: {param}",
        ErrorCodes.TYPE_ERROR: "类型错误: 期望 {expected}, 实际 {actual}",
        ErrorCodes.VALUE_ERROR: "值错误: {value}",
        
        # API错误
        ErrorCodes.API_ERROR: "API调用失败",
        ErrorCodes.API_CONNECTION_ERROR: "API连接失败: {url}",
        ErrorCodes.API_TIMEOUT_ERROR: "API请求超时: {timeout}秒",
        ErrorCodes.API_AUTH_ERROR: "API认证失败，请检查API Key",
        ErrorCodes.API_RATE_LIMIT: "API请求频率超限，请稍后重试",
        ErrorCodes.API_SERVER_ERROR: "API服务器错误: {status_code}",
        ErrorCodes.API_RESPONSE_ERROR: "API响应格式错误",
        
        # 文件错误
        ErrorCodes.FILE_ERROR: "文件操作失败",
        ErrorCodes.FILE_NOT_FOUND: "文件不存在: {path}",
        ErrorCodes.FILE_READ_ERROR: "文件读取失败: {path}",
        ErrorCodes.FILE_WRITE_ERROR: "文件写入失败: {path}",
        ErrorCodes.FILE_FORMAT_ERROR: "文件格式错误: {format}",
        
        # 处理错误
        ErrorCodes.PROCESSING_ERROR: "处理失败",
        ErrorCodes.TEXT_GENERATION_ERROR: "文本生成失败: {reason}",
        ErrorCodes.IMAGE_GENERATION_ERROR: "图像生成失败: {reason}",
        ErrorCodes.VIDEO_GENERATION_ERROR: "视频生成失败: {reason}",
        ErrorCodes.AUDIO_GENERATION_ERROR: "音频生成失败: {reason}",
        ErrorCodes.MUSIC_GENERATION_ERROR: "音乐生成失败: {reason}",
        
        # 资源错误
        ErrorCodes.RESOURCE_ERROR: "资源错误",
        ErrorCodes.INSUFFICIENT_MEMORY: "内存不足",
        ErrorCodes.INSUFFICIENT_STORAGE: "存储空间不足",
        ErrorCodes.GPU_ERROR: "GPU错误: {error}",
        
        # 配置错误
        ErrorCodes.CONFIG_ERROR: "配置错误",
        ErrorCodes.MISSING_API_KEY: "缺少API Key，请在环境变量中设置 {env_var}",
        ErrorCodes.INVALID_CONFIG: "配置无效: {config_name}",
    }
    
    @classmethod
    def get(cls, code: str, **kwargs) -> str:
        """获取错误消息"""
        msg = cls.MESSAGES.get(code, f"未知错误: {code}")
        try:
            return msg.format(**kwargs)
        except KeyError:
            return msg


class UnlimitAIError(Exception):
    """
    基础异常类
    
    Attributes:
        code: 错误代码
        message: 错误消息
        details: 详细信息
        cause: 原始异常
        context: 错误上下文
    """
    
    def __init__(
        self,
        message: str = None,
        code: str = ErrorCodes.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        response_body: Optional[Any] = None,
    ):
        self.code = code
        self.message = message or ErrorMessages.get(code, **(details or {}))
        self.details = details or {}
        self.cause = cause
        self.context = context or {}
        self.status_code = status_code
        self.response_body = response_body
        
        super().__init__(self.message)
    
    def __str__(self):
        parts = [f"[{self.code}] {self.message}"]
        
        if self.details:
            parts.append(f"详情: {self.details}")
        
        if self.context:
            parts.append(f"上下文: {self.context}")
        
        if self.cause:
            parts.append(f"原因: {self.cause}")
        
        return "\n".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于API响应）"""
        result = {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }
        
        if self.context:
            result["error"]["context"] = self.context
        
        if self.cause:
            result["error"]["cause"] = str(self.cause)
        
        return result


# ============================================================================
# API异常
# ============================================================================

class APIError(UnlimitAIError):
    """API错误基类"""
    
    def __init__(
        self,
        message: str = None,
        code: str = ErrorCodes.API_ERROR,
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if status_code:
            details['status_code'] = status_code
        if url:
            details['url'] = url
        
        super().__init__(message=message, code=code, details=details, **kwargs)
        self.status_code = status_code
        self.url = url


class APIConnectionError(APIError):
    """API连接错误"""
    
    def __init__(self, url: str, cause: Exception = None):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.API_CONNECTION_ERROR, url=url),
            code=ErrorCodes.API_CONNECTION_ERROR,
            url=url,
            cause=cause
        )


class APITimeoutError(APIError):
    """API超时错误"""
    
    def __init__(self, timeout: int, url: str = None):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.API_TIMEOUT_ERROR, timeout=timeout),
            code=ErrorCodes.API_TIMEOUT_ERROR,
            details={"timeout": timeout},
            url=url
        )


class APIAuthError(APIError):
    """API认证错误"""
    
    def __init__(self, message: str = None):
        super().__init__(
            message=message or ErrorMessages.get(ErrorCodes.API_AUTH_ERROR),
            code=ErrorCodes.API_AUTH_ERROR,
            status_code=401
        )


class APIRateLimitError(APIError):
    """API频率限制错误"""
    
    def __init__(self, retry_after: int = None):
        details = {}
        if retry_after:
            details['retry_after'] = retry_after
        
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.API_RATE_LIMIT),
            code=ErrorCodes.API_RATE_LIMIT,
            status_code=429,
            details=details
        )
        self.retry_after = retry_after


class APIServerError(APIError):
    """API服务器错误"""
    
    def __init__(self, status_code: int, message: str = None):
        super().__init__(
            message=message or ErrorMessages.get(
                ErrorCodes.API_SERVER_ERROR, 
                status_code=status_code
            ),
            code=ErrorCodes.API_SERVER_ERROR,
            status_code=status_code
        )


class APIResponseError(APIError):
    """API响应错误"""
    
    def __init__(self, message: str = None, response: Any = None):
        super().__init__(
            message=message or ErrorMessages.get(ErrorCodes.API_RESPONSE_ERROR),
            code=ErrorCodes.API_RESPONSE_ERROR,
            details={"response": str(response) if response else None}
        )


# ============================================================================
# 验证异常
# ============================================================================

class ValidationError(UnlimitAIError):
    """验证错误"""
    
    def __init__(
        self,
        message: str = None,
        param: str = None,
        value: Any = None,
        code: str = ErrorCodes.INVALID_PARAMETER
    ):
        details = {}
        if param:
            details['param'] = param
        if value is not None:
            details['value'] = value
        
        if not message and param:
            message = ErrorMessages.get(code, param=param, value=value)
        
        super().__init__(message=message, code=code, details=details)


class MissingParameterError(ValidationError):
    """缺少参数错误"""
    
    def __init__(self, param: str):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.MISSING_PARAMETER, param=param),
            param=param,
            code=ErrorCodes.MISSING_PARAMETER
        )


class InvalidParameterError(ValidationError):
    """无效参数错误"""
    
    def __init__(self, param: str, value: Any, reason: str = None):
        message = f"参数 '{param}' 无效"
        if reason:
            message += f": {reason}"
        
        super().__init__(message=message, param=param, value=value)


class TypeValidationError(ValidationError):
    """类型错误"""
    
    def __init__(self, param: str, expected: str, actual: str):
        super().__init__(
            message=ErrorMessages.get(
                ErrorCodes.TYPE_ERROR,
                expected=expected,
                actual=actual
            ),
            param=param,
            code=ErrorCodes.TYPE_ERROR
        )


# ============================================================================
# 文件异常
# ============================================================================

class FileError(UnlimitAIError):
    """文件错误基类"""
    
    def __init__(
        self,
        message: str = None,
        code: str = ErrorCodes.FILE_ERROR,
        path: str = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if path:
            details['path'] = path
        
        super().__init__(message=message, code=code, details=details, **kwargs)


class FileNotFoundStorageError(FileError):
    """文件不存在错误"""
    
    def __init__(self, path: str):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.FILE_NOT_FOUND, path=path),
            code=ErrorCodes.FILE_NOT_FOUND,
            path=path
        )


class FileReadError(FileError):
    """文件读取错误"""
    
    def __init__(self, path: str, cause: Exception = None):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.FILE_READ_ERROR, path=path),
            code=ErrorCodes.FILE_READ_ERROR,
            path=path,
            cause=cause
        )


class FileWriteError(FileError):
    """文件写入错误"""
    
    def __init__(self, path: str, cause: Exception = None):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.FILE_WRITE_ERROR, path=path),
            code=ErrorCodes.FILE_WRITE_ERROR,
            path=path,
            cause=cause
        )


# ============================================================================
# 处理异常
# ============================================================================

class ProcessingError(UnlimitAIError):
    """处理错误基类"""
    
    def __init__(
        self,
        message: str = None,
        code: str = ErrorCodes.PROCESSING_ERROR,
        stage: str = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if stage:
            details['stage'] = stage
        
        super().__init__(message=message, code=code, details=details, **kwargs)


class TextGenerationError(ProcessingError):
    """文本生成错误"""
    
    def __init__(self, reason: str = None, model: str = None):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.TEXT_GENERATION_ERROR, reason=reason),
            code=ErrorCodes.TEXT_GENERATION_ERROR,
            stage="text_generation",
            details={"reason": reason, "model": model}
        )


class ImageGenerationError(ProcessingError):
    """图像生成错误"""
    
    def __init__(self, reason: str = None, model: str = None):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.IMAGE_GENERATION_ERROR, reason=reason),
            code=ErrorCodes.IMAGE_GENERATION_ERROR,
            stage="image_generation",
            details={"reason": reason, "model": model}
        )


class VideoGenerationError(ProcessingError):
    """视频生成错误"""
    
    def __init__(self, reason: str = None, model: str = None):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.VIDEO_GENERATION_ERROR, reason=reason),
            code=ErrorCodes.VIDEO_GENERATION_ERROR,
            stage="video_generation",
            details={"reason": reason, "model": model}
        )


class AudioGenerationError(ProcessingError):
    """音频生成错误"""
    
    def __init__(self, reason: str = None, model: str = None):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.AUDIO_GENERATION_ERROR, reason=reason),
            code=ErrorCodes.AUDIO_GENERATION_ERROR,
            stage="audio_generation",
            details={"reason": reason, "model": model}
        )


# ============================================================================
# 配置异常
# ============================================================================

class ConfigError(UnlimitAIError):
    """配置错误"""
    
    def __init__(
        self,
        message: str = None,
        code: str = ErrorCodes.CONFIG_ERROR,
        config_name: str = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if config_name:
            details['config_name'] = config_name
        
        super().__init__(message=message, code=code, details=details, **kwargs)


class MissingAPIKeyError(ConfigError):
    """缺少API Key错误"""
    
    def __init__(self, env_var: str = "UNITED_API_KEY"):
        super().__init__(
            message=ErrorMessages.get(ErrorCodes.MISSING_API_KEY, env_var=env_var),
            code=ErrorCodes.MISSING_API_KEY,
            details={"env_var": env_var}
        )


# ============================================================================
# 错误处理器
# ============================================================================

class ErrorHandler:
    """
    错误处理器
    
    Examples:
        >>> handler = ErrorHandler()
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     handler.handle(e, context={"operation": "test"})
    """
    
    def __init__(self, logger=None):
        from utils.logger import get_logger
        self.logger = logger or get_logger(__name__)
    
    def handle(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        reraise: bool = True
    ) -> Optional[UnlimitAIError]:
        """
        处理错误
        
        Args:
            error: 原始错误
            context: 错误上下文
            reraise: 是否重新抛出异常
        
        Returns:
            转换后的UnlimitAIError（如果reraise=False）
        """
        # 如果已经是UnlimitAIError，直接处理
        if isinstance(error, UnlimitAIError):
            if context:
                error.context.update(context)
            
            self.logger.error(
                f"{error}",
                exc_info=True,
                extra={"data": {"error_code": error.code, "context": context}}
            )
            
            if reraise:
                raise error
            return error
        
        # 转换其他异常
        converted_error = self._convert_error(error, context)
        
        self.logger.error(
            f"错误转换: {type(error).__name__} -> {converted_error.code}",
            exc_info=True,
            extra={"data": {"original_error": str(error), "context": context}}
        )
        
        if reraise:
            raise converted_error
        
        return converted_error
    
    def _convert_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> UnlimitAIError:
        """转换异常为UnlimitAIError"""
        
        # 网络错误
        if isinstance(error, (ConnectionError, ConnectionRefusedError)):
            return APIConnectionError(
                url=context.get('url') if context else None,
                cause=error
            )
        
        # 超时错误
        if isinstance(error, TimeoutError):
            return APITimeoutError(
                timeout=context.get('timeout', 30) if context else 30,
                url=context.get('url') if context else None
            )
        
        # 文件错误
        if isinstance(error, builtins.FileNotFoundError):
            return FileNotFoundStorageError(path=str(error))
        
        if isinstance(error, PermissionError):
            return FileWriteError(
                path=context.get('path') if context else 'unknown',
                cause=error
            )
        
        # 值错误
        if isinstance(error, ValueError):
            return ValidationError(
                message=str(error),
                code=ErrorCodes.VALUE_ERROR
            )
        
        # 类型错误
        if isinstance(error, builtins.TypeError):
            return ValidationError(
                message=str(error),
                code=ErrorCodes.TYPE_ERROR
            )
        
        # 其他错误
        return UnlimitAIError(
            message=str(error),
            code=ErrorCodes.UNKNOWN_ERROR,
            cause=error,
            context=context
        )


def handle_errors(
    logger=None,
    reraise: bool = True,
    default_return: Any = None
):
    """
    错误处理装饰器
    
    Args:
        logger: 日志器
        reraise: 是否重新抛出异常
        default_return: 发生异常时的默认返回值
    
    Examples:
        >>> @handle_errors(reraise=False, default_return=None)
        ... def risky_function():
        ...     return risky_operation()
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = ErrorHandler(logger)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args)[:200],  # 限制长度
                    "kwargs": str(kwargs)[:200]
                }
                
                if reraise:
                    handler.handle(e, context=context, reraise=True)
                else:
                    handler.handle(e, context=context, reraise=False)
                    return default_return
        
        return wrapper
    return decorator


def assert_condition(condition: bool, message: str, code: str = ErrorCodes.INVALID_PARAMETER):
    """
    条件断言
    
    Examples:
        >>> assert_condition(value > 0, "值必须大于0")
    """
    if not condition:
        raise ValidationError(message=message, code=code)


def assert_not_none(value: Any, param: str):
    """
    断言值不为None
    
    Examples:
        >>> assert_not_none(user_input, "user_input")
    """
    if value is None:
        raise MissingParameterError(param=param)


def assert_type(value: Any, expected_type: type, param: str):
    """
    断言值类型
    
    Examples:
        >>> assert_type(name, str, "name")
    """
    if not isinstance(value, expected_type):
        raise ValidationError(
            message=f"参数 '{param}' 类型错误: 期望 {expected_type.__name__}, "
                    f"实际 {type(value).__name__}",
            param=param,
            value=value
        )


if __name__ == "__main__":
    # 演示异常系统
    from utils.logger import get_logger
    
    logger = get_logger("ExceptionDemo")
    
    # 使用错误代码
    try:
        raise ValidationError(
            message="用户名不能为空",
            code=ErrorCodes.INVALID_PARAMETER,
            details={"param": "username"}
        )
    except UnlimitAIError as e:
        logger.error(f"捕获异常: {e}")
        print(f"错误字典: {e.to_dict()}")
    
    # 使用装饰器
    @handle_errors(logger, reraise=False, default_return="default")
    def risky_function(x, y):
        return x / y
    
    result = risky_function(1, 0)
    print(f"结果: {result}")
    
    # 使用断言
    try:
        assert_condition(False, "条件不满足")
    except UnlimitAIError as e:
        logger.error(f"断言失败: {e}")
