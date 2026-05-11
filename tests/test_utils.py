"""
工具模块测试

测试所有核心工具模块：
- logger: 日志系统
- exceptions: 异常处理
- config: 配置管理
- delay: 智能延迟
"""

import pytest
import os
import sys
import time
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# 日志系统测试
# =============================================================================

class TestLogger:
    """日志系统测试"""
    
    def test_logger_initialization(self):
        """测试日志器初始化"""
        from utils.logger import get_logger
        
        logger = get_logger("test_logger")
        
        assert logger is not None
        assert logger.name == "test_logger"
    
    def test_logger_levels(self):
        """测试日志级别"""
        from utils.logger import get_logger
        
        logger = get_logger("test_levels", level="DEBUG")
        
        assert logger.level == 10  # DEBUG = 10
    
    def test_logger_file_output(self, temp_dir):
        """测试日志文件输出"""
        from utils.logger import get_logger
        
        log_file = temp_dir / "test.log"
        logger = get_logger(
            "test_file",
            log_file=str(log_file),
            level="DEBUG"
        )
        
        logger.info("测试信息")
        
        # 验证文件已创建
        assert log_file.exists()
        
        # 验证内容
        content = log_file.read_text()
        assert "测试信息" in content
    
    def test_colored_formatter(self):
        """测试彩色格式化器"""
        from utils.logger import ColoredFormatter
        import logging
        
        formatter = ColoredFormatter(
            '%(levelname)s | %(message)s'
        )
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="测试",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        
        assert "INFO" in result
        assert "测试" in result
    
    def test_logger_context_manager(self):
        """测试日志上下文管理器"""
        from utils.logger import LoggerContext, get_logger
        
        logger = get_logger("test_context")
        
        with LoggerContext(logger, "测试操作"):
            time.sleep(0.01)
        
        # 如果没有抛出异常，则测试通过
        assert True
    
    def test_log_function_call_decorator(self):
        """测试函数调用日志装饰器"""
        from utils.logger import log_function_call, get_logger
        
        logger = get_logger("test_decorator")
        
        @log_function_call(logger)
        def test_function(x, y):
            return x + y
        
        result = test_function(1, 2)
        
        assert result == 3


# =============================================================================
# 异常处理测试
# =============================================================================

class TestExceptions:
    """异常处理测试"""
    
    def test_base_exception(self):
        """测试基础异常"""
        from utils.exceptions import UnlimitAIError, ErrorCodes
        
        error = UnlimitAIError(
            message="测试错误",
            code=ErrorCodes.UNKNOWN_ERROR
        )
        
        assert error.code == ErrorCodes.UNKNOWN_ERROR
        assert error.message == "测试错误"
        assert "测试错误" in str(error)
    
    def test_exception_to_dict(self):
        """测试异常转换为字典"""
        from utils.exceptions import UnlimitAIError, ErrorCodes
        
        error = UnlimitAIError(
            message="测试错误",
            code=ErrorCodes.UNKNOWN_ERROR,
            details={"key": "value"}
        )
        
        result = error.to_dict()
        
        assert "error" in result
        assert result["error"]["code"] == ErrorCodes.UNKNOWN_ERROR
        assert result["error"]["message"] == "测试错误"
    
    def test_api_error(self):
        """测试API错误"""
        from utils.exceptions import APIError, ErrorCodes
        
        error = APIError(
            message="API调用失败",
            status_code=500,
            url="https://api.example.com"
        )
        
        assert error.code == ErrorCodes.API_ERROR
        assert error.status_code == 500
        assert error.url == "https://api.example.com"
    
    def test_api_connection_error(self):
        """测试API连接错误"""
        from utils.exceptions import APIConnectionError
        
        error = APIConnectionError(
            url="https://api.example.com",
            cause=Exception("Connection failed")
        )
        
        assert "api.example.com" in str(error)
    
    def test_api_timeout_error(self):
        """测试API超时错误"""
        from utils.exceptions import APITimeoutError
        
        error = APITimeoutError(timeout=30)
        
        assert "30" in str(error)
    
    def test_validation_error(self):
        """测试验证错误"""
        from utils.exceptions import ValidationError, ErrorCodes
        
        error = ValidationError(
            message="参数无效",
            param="test_param",
            value="invalid_value"
        )
        
        assert error.code == ErrorCodes.INVALID_PARAMETER
        assert error.details["param"] == "test_param"
    
    def test_file_not_found_error(self):
        """测试文件不存在错误"""
        from utils.exceptions import FileNotFoundStorageError
        
        error = FileNotFoundStorageError(path="/nonexistent/file.txt")
        
        assert "file.txt" in str(error)
    
    def test_error_handler(self):
        """测试错误处理器"""
        from utils.exceptions import ErrorHandler, UnlimitAIError
        
        handler = ErrorHandler()
        
        error = Exception("测试错误")
        
        result = handler.handle(error, reraise=False)
        
        assert isinstance(result, UnlimitAIError)
    
    def test_handle_errors_decorator(self):
        """测试错误处理装饰器"""
        from utils.exceptions import handle_errors
        
        @handle_errors(reraise=False, default_return="default")
        def risky_function():
            raise ValueError("测试错误")
        
        result = risky_function()
        
        assert result == "default"
    
    def test_assert_condition(self):
        """测试条件断言"""
        from utils.exceptions import assert_condition, ValidationError
        
        # 条件为真，不应抛出异常
        assert_condition(True, "条件不满足")
        
        # 条件为假，应抛出异常
        with pytest.raises(ValidationError):
            assert_condition(False, "条件不满足")
    
    def test_assert_not_none(self):
        """测试非空断言"""
        from utils.exceptions import assert_not_none, MissingParameterError
        
        assert_not_none("value", "param")
        
        with pytest.raises(MissingParameterError):
            assert_not_none(None, "param")


# =============================================================================
# 配置管理测试
# =============================================================================

class TestConfig:
    """配置管理测试"""
    
    def test_config_initialization(self, temp_dir):
        """测试配置初始化"""
        from utils.config import Config
        
        config_file = temp_dir / "test_config.yaml"
        config_file.write_text("test: value\n")
        
        config = Config(config_path=str(config_file))
        
        assert config is not None
    
    def test_config_load_env(self, monkeypatch):
        """测试从环境变量加载配置"""
        from utils.config import Config
        
        monkeypatch.setenv("UNITED_API_KEY", "test_key")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        config = Config()
        
        assert config.get("api_key") == "test_key"
        assert config.get("log_level") == "DEBUG"
    
    def test_config_load_file(self, temp_dir):
        """测试从文件加载配置"""
        from utils.config import Config
        
        config_file = temp_dir / "test_config.yaml"
        config_file.write_text("""
api:
  api_key: file_key
  timeout: 30
""")
        
        config = Config(config_path=str(config_file))
        
        assert config.get("api.api_key") == "file_key"
        assert config.get("api.timeout") == 30
    
    def test_config_env_override_file(self, temp_dir, monkeypatch):
        """测试环境变量覆盖文件配置"""
        from utils.config import Config
        
        config_file = temp_dir / "test_config.yaml"
        config_file.write_text("api_key: file_key\n")
        
        monkeypatch.setenv("UNITED_API_KEY", "env_key")
        
        config = Config(config_path=str(config_file))
        
        # 环境变量应该覆盖文件配置
        assert config.get("api_key") == "env_key"
    
    def test_config_get_nested(self, temp_dir):
        """测试获取嵌套配置"""
        from utils.config import Config
        
        config_file = temp_dir / "test_config.yaml"
        config_file.write_text("""
models:
  text:
    default: deepseek-chat
""")
        
        config = Config(config_path=str(config_file))
        
        assert config.get("models.text.default") == "deepseek-chat"
    
    def test_config_get_default(self):
        """测试获取默认值"""
        from utils.config import Config
        
        config = Config()
        
        result = config.get("nonexistent.key", default="default_value")
        
        assert result == "default_value"
    
    def test_config_set(self):
        """测试设置配置"""
        from utils.config import Config
        
        config = Config()
        
        config.set("test.key", "test_value")
        
        assert config.get("test.key") == "test_value"
    
    def test_config_save(self, temp_dir):
        """测试保存配置"""
        from utils.config import Config
        
        config_file = temp_dir / "test_save.yaml"
        
        config = Config(config_path=str(config_file))
        config.set("test.key", "test_value")
        config.save()
        
        # 验证文件已创建
        assert config_file.exists()
    
    def test_config_to_dict(self):
        """测试转换为字典"""
        from utils.config import Config
        
        config = Config()
        config.set("test.key", "test_value")
        
        result = config.to_dict()
        
        assert isinstance(result, dict)
        assert result["test"]["key"] == "test_value"


# =============================================================================
# 智能延迟测试
# =============================================================================

class TestDelay:
    """智能延迟测试"""
    
    def test_smart_delay_initialization(self):
        """测试智能延迟初始化"""
        from utils.delay import SmartDelay
        
        delay = SmartDelay()
        
        assert delay is not None
        assert delay.current_delay > 0
    
    def test_smart_delay_wait(self):
        """测试智能延迟等待"""
        from utils.delay import SmartDelay
        
        delay = SmartDelay(
            initial_delay=0.1,
            max_delay=1.0
        )
        
        start_time = time.time()
        actual_delay = delay.wait("test")
        elapsed = time.time() - start_time
        
        assert actual_delay > 0
        assert elapsed >= 0.09  # 允许小误差
    
    def test_smart_delay_on_success(self):
        """测试成功回调降低延迟"""
        from utils.delay import SmartDelay
        
        delay = SmartDelay(initial_delay=1.0, min_delay=0.1)
        
        initial = delay.current_delay
        delay.on_success()
        
        assert delay.current_delay < initial
    
    def test_smart_delay_on_failure(self):
        """测试失败回调增加延迟"""
        from utils.delay import SmartDelay
        
        delay = SmartDelay(initial_delay=1.0, max_delay=10.0)
        
        initial = delay.current_delay
        delay.on_failure()
        
        assert delay.current_delay > initial
    
    def test_smart_delay_rate_limit(self):
        """测试频率限制错误大幅增加延迟"""
        from utils.delay import SmartDelay
        
        delay = SmartDelay(initial_delay=1.0, max_delay=100.0)
        
        initial = delay.current_delay
        delay.on_failure(is_rate_limit=True)
        
        # 频率限制应该增加更多延迟
        assert delay.current_delay > initial * 2
    
    def test_smart_delay_reset(self):
        """测试重置延迟"""
        from utils.delay import SmartDelay
        
        delay = SmartDelay(initial_delay=1.0)
        
        delay.on_failure()
        delay.on_failure()
        
        delay.reset()
        
        assert delay.current_delay == 1.0
        assert delay.success_count == 0
        assert delay.failure_count == 0
    
    def test_exponential_backoff(self):
        """测试指数退避"""
        from utils.delay import ExponentialBackoff
        
        backoff = ExponentialBackoff(
            base_delay=1.0,
            max_delay=60.0
        )
        
        # 延迟应该指数增长
        delays = [backoff.get_delay(i) for i in range(5)]
        
        assert delays[0] <= 1.0
        assert delays[1] <= 2.0
        assert delays[2] <= 4.0
    
    def test_retry_on_failure_decorator(self):
        """测试重试装饰器"""
        from utils.delay import retry_on_failure
        
        call_count = 0
        
        @retry_on_failure(max_retries=3, base_delay=0.1)
        def unreliable_function():
            nonlocal call_count
            call_count += 1
            
            if call_count < 3:
                raise ValueError("临时错误")
            
            return "成功"
        
        result = unreliable_function()
        
        assert result == "成功"
        assert call_count == 3
    
    def test_rate_limiter(self):
        """测试频率限制器"""
        from utils.delay import RateLimiter
        
        limiter = RateLimiter(max_calls=3, period=1.0)
        
        # 前3次应该成功
        assert limiter.acquire(timeout=0.5)
        assert limiter.acquire(timeout=0.5)
        assert limiter.acquire(timeout=0.5)
        
        # 第4次应该超时
        assert not limiter.acquire(timeout=0.5)
    
    def test_global_delay(self):
        """测试全局延迟管理器"""
        from utils.delay import get_global_delay
        
        delay1 = get_global_delay()
        delay2 = get_global_delay()
        
        assert delay1 is delay2


# =============================================================================
# 集成测试
# =============================================================================

class TestIntegration:
    """集成测试"""
    
    def test_logger_with_exceptions(self):
        """测试日志与异常集成"""
        from utils.logger import get_logger
        from utils.exceptions import APIError
        
        logger = get_logger("test_integration")
        
        try:
            raise APIError("API错误", status_code=500)
        except APIError as e:
            logger.error(f"捕获异常: {e}", exc_info=True)
        
        # 如果没有抛出异常，则测试通过
        assert True
    
    def test_config_with_logger(self, temp_dir):
        """测试配置与日志集成"""
        from utils.config import Config
        from utils.logger import get_logger
        
        config_file = temp_dir / "test_config.yaml"
        config_file.write_text("log_level: DEBUG\n")
        
        config = Config(config_path=str(config_file))
        logger = get_logger("test", level=config.get("log_level"))
        
        logger.debug("调试信息")
        
        # 如果没有抛出异常，则测试通过
        assert True
    
    def test_delay_with_retry(self):
        """测试延迟与重试集成"""
        from utils.delay import SmartDelay, retry_on_failure
        
        delay = SmartDelay(initial_delay=0.1, max_delay=1.0)
        
        @retry_on_failure(max_retries=2, base_delay=0.1)
        def operation():
            delay.wait("api_call")
            
            if delay.failure_count < 1:
                delay.on_failure()
                raise Exception("临时失败")
            
            delay.on_success()
            return "成功"
        
        result = operation()
        
        assert result == "成功"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
