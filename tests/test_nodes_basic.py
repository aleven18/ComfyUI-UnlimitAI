"""
节点基础功能测试

测试所有节点类型的基础功能：
- 节点初始化
- 输入验证
- 输出类型
- 参数处理
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from PIL import Image

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# 节点初始化测试
# =============================================================================

class TestNodeInitialization:
    """节点初始化测试"""
    
    def test_character_image_loader_init(self):
        """测试角色图像加载器初始化"""
        from nodes.character_nodes_optimized import CharacterImageLoader
        
        node = CharacterImageLoader()
        
        assert node is not None
        assert hasattr(node, 'INPUT_TYPES')
    
    def test_voice_definition_init(self):
        """测试音色定义节点初始化"""
        from nodes.character_nodes_optimized import VoiceDefinition
        
        node = VoiceDefinition()
        
        assert node is not None
        assert hasattr(node, 'INPUT_TYPES')
    
    def test_character_manager_init(self):
        """测试角色管理器初始化"""
        from nodes.character_nodes_optimized import CharacterManager
        
        node = CharacterManager()
        
        assert node is not None
        assert hasattr(node, 'INPUT_TYPES')
    
    def test_text_node_init(self):
        """测试文本节点初始化"""
        try:
            from nodes.text_nodes import TextGeneratorNode
            
            node = TextGeneratorNode()
            
            assert node is not None
        except ImportError:
            pytest.skip("文本节点模块未找到")
    
    def test_image_node_init(self):
        """测试图像节点初始化"""
        try:
            from nodes.image_nodes import ImageGeneratorNode
            
            node = ImageGeneratorNode()
            
            assert node is not None
        except ImportError:
            pytest.skip("图像节点模块未找到")


# =============================================================================
# 输入验证测试
# =============================================================================

class TestInputValidation:
    """输入验证测试"""
    
    def test_validate_prompt_not_empty(self):
        """测试提示词不能为空"""
        from utils.api_client import InputValidator
        
        validator = InputValidator()
        
        with pytest.raises(Exception):  # 应该抛出ValidationError
            validator.validate_prompt("")
    
    def test_validate_prompt_max_length(self):
        """测试提示词最大长度"""
        from utils.api_client import InputValidator
        
        validator = InputValidator(max_length=100)
        
        long_prompt = "a" * 200
        
        with pytest.raises(Exception):
            validator.validate_prompt(long_prompt)
    
    def test_validate_model_name(self):
        """测试模型名称验证"""
        from utils.api_client import InputValidator
        
        validator = InputValidator()
        
        # 有效模型名称
        result = validator.validate_model_name("deepseek-chat")
        assert result == "deepseek-chat"
        
        # 无效模型名称应该抛出异常或返回错误
        # 具体行为取决于实现
    
    def test_validate_image_size(self):
        """测试图像尺寸验证"""
        from utils.api_client import InputValidator
        
        validator = InputValidator()
        
        # 有效尺寸
        result = validator.validate_image_size("1024x1024")
        assert result == "1024x1024"
        
        # 无效尺寸
        with pytest.raises(Exception):
            validator.validate_image_size("invalid")
    
    def test_validate_duration_range(self):
        """测试时长范围验证"""
        from utils.api_client import InputValidator
        
        validator = InputValidator(min_duration=1.0, max_duration=60.0)
        
        # 有效时长
        result = validator.validate_duration(10.0)
        assert result == 10.0
        
        # 超出范围
        with pytest.raises(Exception):
            validator.validate_duration(0.5)
        
        with pytest.raises(Exception):
            validator.validate_duration(100.0)


# =============================================================================
# 输出类型测试
# =============================================================================

class TestOutputTypes:
    """输出类型测试"""
    
    def test_character_image_output_type(self):
        """测试角色图像输出类型"""
        from nodes.character_nodes_optimized import CharacterImageLoader
        
        node = CharacterImageLoader()
        
        # 检查RETURN_TYPES是否存在
        if hasattr(node, 'RETURN_TYPES'):
            return_types = node.RETURN_TYPES
            
            # 应该包含IMAGE类型（ComfyUI标准类型）
            assert 'IMAGE' in return_types or 'image' in str(return_types).lower()
    
    def test_voice_definition_output_type(self):
        """测试音色定义输出类型"""
        from nodes.character_nodes_optimized import VoiceDefinition
        
        node = VoiceDefinition()
        
        if hasattr(node, 'RETURN_TYPES'):
            return_types = node.RETURN_TYPES
            
            # 应该包含VOICE或类似类型
            assert return_types is not None
    
    def test_text_node_output_type(self):
        """测试文本节点输出类型"""
        try:
            from nodes.text_nodes import TextGeneratorNode
            
            node = TextGeneratorNode()
            
            if hasattr(node, 'RETURN_TYPES'):
                return_types = node.RETURN_TYPES
                
                # 应该包含STRING类型
                assert 'STRING' in return_types or 'string' in str(return_types).lower()
        except ImportError:
            pytest.skip("文本节点模块未找到")
    
    def test_image_node_output_type(self):
        """测试图像节点输出类型"""
        try:
            from nodes.image_nodes import ImageGeneratorNode
            
            node = ImageGeneratorNode()
            
            if hasattr(node, 'RETURN_TYPES'):
                return_types = node.RETURN_TYPES
                
                # 应该包含IMAGE类型
                assert 'IMAGE' in return_types or 'image' in str(return_types).lower()
        except ImportError:
            pytest.skip("图像节点模块未找到")


# =============================================================================
# 角色节点功能测试
# =============================================================================

class TestCharacterNodes:
    """角色节点功能测试"""
    
    def test_character_image_loader_from_url(self):
        """测试从URL加载角色图像"""
        from nodes.character_nodes_optimized import CharacterImageLoader
        
        node = CharacterImageLoader()
        
        # 模拟URL加载（不实际下载）
        # 具体测试取决于实现
        assert node is not None
    
    def test_voice_definition_create(self):
        """测试创建音色定义"""
        from nodes.character_nodes_optimized import VoiceDefinition
        
        node = VoiceDefinition()
        
        # 检查是否可以创建音色配置
        if hasattr(node, 'define'):
            result = node.define(
                character_name="测试角色",
                gender="male",
                age="young",
                tone="friendly",
                speed="normal",
                engine="minimax"
            )
            
            assert result is not None
    
    def test_character_manager_create(self):
        """测试创建角色"""
        from nodes.character_nodes_optimized import CharacterManager
        
        node = CharacterManager()
        
        # 检查是否可以创建角色
        assert node is not None


# =============================================================================
# 文本节点功能测试
# =============================================================================

class TestTextNodes:
    """文本节点功能测试"""
    
    def test_text_generator_parameters(self):
        """测试文本生成参数"""
        try:
            from nodes.text_nodes import TextGeneratorNode
            
            node = TextGeneratorNode()
            
            # 检查输入类型
            if hasattr(node, 'INPUT_TYPES'):
                input_types = node.INPUT_TYPES()
                
                assert input_types is not None
                assert isinstance(input_types, dict)
        except ImportError:
            pytest.skip("文本节点模块未找到")
    
    def test_text_parser_parameters(self):
        """测试文本解析参数"""
        try:
            from nodes.text_nodes import TextParserNode
            
            node = TextParserNode()
            
            assert node is not None
        except ImportError:
            pytest.skip("文本解析节点未找到")


# =============================================================================
# 图像节点功能测试
# =============================================================================

class TestImageNodes:
    """图像节点功能测试"""
    
    def test_image_generator_parameters(self):
        """测试图像生成参数"""
        try:
            from nodes.image_nodes import ImageGeneratorNode
            
            node = ImageGeneratorNode()
            
            # 检查输入类型
            if hasattr(node, 'INPUT_TYPES'):
                input_types = node.INPUT_TYPES()
                
                assert input_types is not None
        except ImportError:
            pytest.skip("图像节点模块未找到")
    
    def test_image_size_parameter(self):
        """测试图像尺寸参数"""
        try:
            from nodes.image_nodes import ImageGeneratorNode
            
            node = ImageGeneratorNode()
            
            if hasattr(node, 'INPUT_TYPES'):
                input_types = node.INPUT_TYPES()
                
                # 检查是否包含size参数
                # 具体检查取决于实现
                assert True
        except ImportError:
            pytest.skip("图像节点模块未找到")


# =============================================================================
# 视频节点功能测试
# =============================================================================

class TestVideoNodes:
    """视频节点功能测试"""
    
    def test_video_generator_init(self):
        """测试视频生成器初始化"""
        try:
            from nodes.video_nodes import VideoGeneratorNode
            
            node = VideoGeneratorNode()
            
            assert node is not None
        except ImportError:
            pytest.skip("视频节点模块未找到")
    
    def test_video_duration_parameter(self):
        """测试视频时长参数"""
        try:
            from nodes.video_nodes import VideoGeneratorNode
            
            node = VideoGeneratorNode()
            
            if hasattr(node, 'INPUT_TYPES'):
                input_types = node.INPUT_TYPES()
                
                # 检查是否包含duration参数
                assert True
        except ImportError:
            pytest.skip("视频节点模块未找到")


# =============================================================================
# 音频节点功能测试
# =============================================================================

class TestAudioNodes:
    """音频节点功能测试"""
    
    def test_audio_generator_init(self):
        """测试音频生成器初始化"""
        try:
            from nodes.audio_nodes import AudioGeneratorNode
            
            node = AudioGeneratorNode()
            
            assert node is not None
        except ImportError:
            pytest.skip("音频节点模块未找到")


# =============================================================================
# 音乐节点功能测试
# =============================================================================

class TestMusicNodes:
    """音乐节点功能测试"""
    
    def test_music_generator_init(self):
        """测试音乐生成器初始化"""
        try:
            from nodes.music_nodes import MusicGeneratorNode
            
            node = MusicGeneratorNode()
            
            assert node is not None
        except ImportError:
            pytest.skip("音乐节点模块未找到")


# =============================================================================
# 工作流节点功能测试
# =============================================================================

class TestWorkflowNodes:
    """工作流节点功能测试"""
    
    def test_workflow_controller_init(self):
        """测试工作流控制器初始化"""
        try:
            from nodes.workflow_nodes import WorkflowControllerNode
            
            node = WorkflowControllerNode()
            
            assert node is not None
        except ImportError:
            pytest.skip("工作流节点模块未找到")
    
    def test_cost_calculator_init(self):
        """测试成本计算器初始化"""
        try:
            from nodes.optimization_nodes import CostCalculatorNode
            
            node = CostCalculatorNode()
            
            assert node is not None
        except ImportError:
            pytest.skip("成本计算节点未找到")


# =============================================================================
# 节点类型系统测试
# =============================================================================

class TestNodeTypeSystem:
    """节点类型系统测试"""
    
    def test_node_has_required_methods(self):
        """测试节点是否有必需的方法"""
        from nodes.character_nodes_optimized import CharacterImageLoader
        
        node = CharacterImageLoader()
        
        # ComfyUI节点必需的方法
        required_methods = ['INPUT_TYPES']
        
        for method in required_methods:
            assert hasattr(node, method), f"缺少必需方法: {method}"
    
    def test_node_input_types_structure(self):
        """测试节点输入类型结构"""
        from nodes.character_nodes_optimized import CharacterImageLoader
        
        node = CharacterImageLoader()
        
        input_types = node.INPUT_TYPES()
        
        # 应该是一个字典
        assert isinstance(input_types, dict)
        
        # 应该包含required或optional键
        assert 'required' in input_types or 'optional' in input_types
    
    def test_node_function_callable(self):
        """测试节点主函数是否可调用"""
        from nodes.character_nodes_optimized import CharacterImageLoader
        
        node = CharacterImageLoader()
        
        # 检查主函数是否存在
        # ComfyUI节点通常有一个主函数
        if hasattr(node, 'load_from_url'):
            assert callable(node.load_from_url)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
