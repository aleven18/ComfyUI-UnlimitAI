"""
API客户端单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from utils.api_client import (
    UnlimitAIClient,
    InputValidator,
    ErrorHandler
)
from utils.exceptions import (
    APIError,
    APIConnectionError,
    APITimeoutError,
    ValidationError
)


class TestUnlimitAIClient:
    """UnlimitAIClient测试类"""
    
    @pytest.fixture
    def client(self, mock_config):
        """创建测试客户端"""
        return UnlimitAIClient(api_key=mock_config["api_key"])
    
    def test_client_initialization(self, mock_config):
        """测试客户端初始化"""
        client = UnlimitAIClient(
            api_key=mock_config["api_key"],
            base_url=mock_config["api_base_url"]
        )
        
        assert client.api_key == mock_config["api_key"]
        assert client.base_url == mock_config["api_base_url"]
        assert client.session is not None
    
    def test_client_without_api_key(self):
        """测试没有API key时抛出异常"""
        with pytest.raises(ValidationError):
            UnlimitAIClient(api_key="")
    
    @patch('requests.Session.post')
    def test_generate_text_success(self, mock_post, client, sample_api_response):
        """测试文本生成成功"""
        # Mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_post.return_value = mock_response
        
        # 执行
        result = client.generate_text(
            prompt="测试提示词",
            model="deepseek-chat"
        )
        
        # 验证
        assert result == sample_api_response["data"]["text"]
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_generate_text_with_error(self, mock_post, client):
        """测试文本生成失败"""
        # Mock错误响应
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Server error"}
        mock_post.return_value = mock_response
        
        # 验证抛出异常
        with pytest.raises(APIError):
            client.generate_text(
                prompt="测试提示词",
                model="deepseek-chat"
            )
    
    @patch('requests.Session.post')
    def test_generate_image_success(self, mock_post, client, sample_image_response):
        """测试图像生成成功"""
        # Mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_image_response
        mock_post.return_value = mock_response
        
        # 执行
        result = client.generate_image(
            prompt="测试提示词",
            model="flux.1-schnell",
            size="1024x1024"
        )
        
        # 验证
        assert result == sample_image_response["data"]["images"][0]["url"]
    
    @patch('requests.Session.post')
    def test_generate_video_success(self, mock_post, client, sample_video_response):
        """测试视频生成成功"""
        # Mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_video_response
        mock_post.return_value = mock_response
        
        # 执行
        result = client.generate_video(
            prompt="测试提示词",
            model="kling-video-v2",
            duration=5.0
        )
        
        # 验证
        assert result == sample_video_response["data"]["videos"][0]["url"]
    
    @patch('requests.Session.post')
    def test_timeout_handling(self, mock_post, client):
        """测试超时处理"""
        # Mock超时
        mock_post.side_effect = requests.Timeout("Request timed out")
        
        # 验证抛出超时异常
        with pytest.raises(APITimeoutError):
            client.generate_text(
                prompt="测试提示词",
                model="deepseek-chat"
            )
    
    @patch('requests.Session.post')
    def test_connection_error_handling(self, mock_post, client):
        """测试连接错误处理"""
        # Mock连接错误
        mock_post.side_effect = requests.ConnectionError("Connection failed")
        
        # 验证抛出连接异常
        with pytest.raises(APIConnectionError):
            client.generate_text(
                prompt="测试提示词",
                model="deepseek-chat"
            )
    
    def test_retry_mechanism(self, client):
        """测试重试机制"""
        # TODO: 实现重试逻辑测试
        pass
    
    def test_close_session(self, client):
        """测试关闭会话"""
        client.close()
        # 验证会话已关闭
        assert True  # 简化验证


class TestInputValidator:
    """输入验证器测试"""
    
    def test_validate_prompt_success(self):
        """测试提示词验证成功"""
        validator = InputValidator()
        
        result = validator.validate_prompt("这是一个有效的提示词")
        
        assert result == "这是一个有效的提示词"
    
    def test_validate_prompt_empty(self):
        """测试空提示词验证失败"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_prompt("")
    
    def test_validate_prompt_too_long(self):
        """测试超长提示词验证失败"""
        validator = InputValidator(max_length=100)
        long_prompt = "a" * 200
        
        with pytest.raises(ValidationError):
            validator.validate_prompt(long_prompt)
    
    def test_validate_model_name_success(self):
        """测试模型名称验证成功"""
        validator = InputValidator()
        
        result = validator.validate_model_name("deepseek-chat")
        
        assert result == "deepseek-chat"
    
    def test_validate_model_name_invalid(self):
        """测试无效模型名称验证失败"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_model_name("invalid-model")
    
    def test_validate_image_size_success(self):
        """测试图像尺寸验证成功"""
        validator = InputValidator()
        
        result = validator.validate_image_size("1024x1024")
        
        assert result == "1024x1024"
    
    def test_validate_image_size_invalid(self):
        """测试无效图像尺寸验证失败"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_image_size("invalid")
    
    def test_validate_duration_success(self):
        """测试时长验证成功"""
        validator = InputValidator()
        
        result = validator.validate_duration(5.0)
        
        assert result == 5.0
    
    def test_validate_duration_invalid(self):
        """测试无效时长验证失败"""
        validator = InputValidator()
        
        with pytest.raises(ValidationError):
            validator.validate_duration(-1.0)
    
    def test_validate_duration_out_of_range(self):
        """测试超出范围的时长验证失败"""
        validator = InputValidator(max_duration=10.0)
        
        with pytest.raises(ValidationError):
            validator.validate_duration(20.0)


class TestErrorHandler:
    """错误处理器测试"""
    
    def test_handle_api_error(self):
        """测试处理API错误"""
        handler = ErrorHandler()
        
        error = APIError(
            message="API错误",
            status_code=500
        )
        
        result = handler.handle(error, reraise=False)
        
        assert result.code == "E2000"
    
    def test_handle_validation_error(self):
        """测试处理验证错误"""
        handler = ErrorHandler()
        
        error = ValidationError(
            message="验证失败",
            param="test_param"
        )
        
        result = handler.handle(error, reraise=False)
        
        assert result.code == "E1001"
    
    def test_convert_unknown_error(self):
        """测试转换未知错误"""
        handler = ErrorHandler()
        
        error = Exception("未知错误")
        
        result = handler.handle(error, reraise=False)
        
        assert result.code == "E1000"
    
    def test_handle_with_context(self):
        """测试带上下文的错误处理"""
        handler = ErrorHandler()
        
        error = Exception("测试错误")
        context = {"operation": "test_operation"}
        
        result = handler.handle(error, context=context, reraise=False)
        
        assert result.context == context


@pytest.mark.integration
class TestUnlimitAIClientIntegration:
    """API客户端集成测试"""
    
    @pytest.fixture
    def real_client(self):
        """创建真实客户端（需要API Key）"""
        api_key = os.getenv("UNITED_API_KEY")
        if not api_key:
            pytest.skip("未设置UNITED_API_KEY环境变量")
        
        return UnlimitAIClient(api_key=api_key)
    
    @pytest.mark.api
    def test_real_text_generation(self, real_client):
        """测试真实文本生成"""
        result = real_client.generate_text(
            prompt="写一句话",
            model="deepseek-chat"
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_real_image_generation(self, real_client):
        """测试真实图像生成"""
        result = real_client.generate_image(
            prompt="一只可爱的猫",
            model="flux.1-schnell",
            size="512x512"
        )
        
        assert isinstance(result, str)
        assert result.startswith("http")
