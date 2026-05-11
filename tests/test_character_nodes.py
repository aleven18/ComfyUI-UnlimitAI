"""
角色节点单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np
from nodes.character_nodes_optimized import (
    CharacterImageLoader,
    VoiceDefinition,
    CharacterManager,
    CharacterConsistency
)


class TestCharacterImageLoader:
    """角色图像加载器测试"""
    
    @pytest.fixture
    def loader(self):
        """创建测试加载器"""
        return CharacterImageLoader()
    
    def test_initialization(self, loader):
        """测试初始化"""
        assert loader is not None
    
    @patch('nodes.character_nodes_optimized.UnlimitAIClient')
    def test_load_character_from_url(self, mock_client, loader):
        """测试从URL加载角色"""
        # Mock图像数据
        mock_image_data = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        
        # 执行
        result = loader.load_from_url(
            url="https://example.com/character.png",
            character_name="测试角色"
        )
        
        # 验证返回类型
        assert result is not None
    
    def test_load_character_from_local_file(self, loader, temp_dir):
        """测试从本地文件加载角色"""
        # 创建测试图像
        test_image = Image.new('RGB', (512, 512), color='red')
        image_path = temp_dir / "test_character.png"
        test_image.save(image_path)
        
        # 执行
        result = loader.load_from_file(
            file_path=str(image_path),
            character_name="测试角色"
        )
        
        # 验证
        assert result is not None
    
    def test_load_nonexistent_file(self, loader):
        """测试加载不存在的文件"""
        with pytest.raises(FileNotFoundError):
            loader.load_from_file(
                file_path="/nonexistent/path.png",
                character_name="测试角色"
            )
    
    def test_invalid_image_format(self, loader, temp_dir):
        """测试无效图像格式"""
        # 创建无效图像文件
        invalid_file = temp_dir / "invalid.txt"
        invalid_file.write_text("not an image")
        
        with pytest.raises(Exception):
            loader.load_from_file(
                file_path=str(invalid_file),
                character_name="测试角色"
            )


class TestVoiceDefinition:
    """音色定义测试"""
    
    @pytest.fixture
    def voice_def(self):
        """创建测试音色定义"""
        return VoiceDefinition()
    
    def test_initialization(self, voice_def):
        """测试初始化"""
        assert voice_def is not None
    
    def test_define_voice(self, voice_def):
        """测试定义音色"""
        result = voice_def.define(
            character_name="小明",
            gender="male",
            age="young",
            tone="friendly",
            speed="normal",
            engine="minimax"
        )
        
        assert result is not None
        assert result["character_name"] == "小明"
        assert result["gender"] == "male"
    
    def test_invalid_gender(self, voice_def):
        """测试无效性别"""
        with pytest.raises(ValueError):
            voice_def.define(
                character_name="测试",
                gender="invalid",
                age="young",
                tone="friendly",
                speed="normal",
                engine="minimax"
            )
    
    def test_invalid_engine(self, voice_def):
        """测试无效引擎"""
        with pytest.raises(ValueError):
            voice_def.define(
                character_name="测试",
                gender="male",
                age="young",
                tone="friendly",
                speed="normal",
                engine="invalid_engine"
            )
    
    def test_voice_preview(self, voice_def, mock_api_client):
        """测试音色预览"""
        # TODO: 实现音色预览测试
        pass


class TestCharacterManager:
    """角色管理器测试"""
    
    @pytest.fixture
    def manager(self, temp_database):
        """创建测试管理器"""
        return CharacterManager(database=temp_database)
    
    def test_create_character(self, manager, sample_character_data):
        """测试创建角色"""
        result = manager.create_character(
            character_data=sample_character_data
        )
        
        assert result is not None
        assert result["name"] == sample_character_data["name"]
    
    def test_get_character(self, manager, sample_character_data):
        """测试获取角色"""
        # 先创建角色
        created = manager.create_character(
            character_data=sample_character_data
        )
        
        # 获取角色
        result = manager.get_character(
            character_name=sample_character_data["name"]
        )
        
        assert result is not None
        assert result["name"] == sample_character_data["name"]
    
    def test_get_nonexistent_character(self, manager):
        """测试获取不存在的角色"""
        result = manager.get_character(
            character_name="不存在的角色"
        )
        
        assert result is None
    
    def test_update_character(self, manager, sample_character_data):
        """测试更新角色"""
        # 先创建角色
        manager.create_character(
            character_data=sample_character_data
        )
        
        # 更新角色
        updated_data = sample_character_data.copy()
        updated_data["age"] = 20
        
        result = manager.update_character(
            character_name=sample_character_data["name"],
            updates=updated_data
        )
        
        assert result is not None
        assert result["age"] == 20
    
    def test_delete_character(self, manager, sample_character_data):
        """测试删除角色"""
        # 先创建角色
        manager.create_character(
            character_data=sample_character_data
        )
        
        # 删除角色
        result = manager.delete_character(
            character_name=sample_character_data["name"]
        )
        
        assert result is True
        
        # 验证已删除
        deleted = manager.get_character(
            character_name=sample_character_data["name"]
        )
        assert deleted is None
    
    def test_list_characters(self, manager, sample_character_data):
        """测试列出角色"""
        # 创建多个角色
        manager.create_character(character_data=sample_character_data)
        
        character2 = sample_character_data.copy()
        character2["name"] = "小红"
        manager.create_character(character_data=character2)
        
        # 列出角色
        result = manager.list_characters()
        
        assert len(result) == 2
        assert result[0]["name"] == sample_character_data["name"]
        assert result[1]["name"] == "小红"


class TestCharacterConsistency:
    """角色一致性测试"""
    
    @pytest.fixture
    def consistency(self):
        """创建测试一致性检查器"""
        return CharacterConsistency()
    
    def test_check_appearance_consistency(self, consistency):
        """测试外观一致性检查"""
        # TODO: 实现一致性检查测试
        pass
    
    def test_check_voice_consistency(self, consistency):
        """测试音色一致性检查"""
        # TODO: 实现一致性检查测试
        pass
    
    def test_detect_inconsistency(self, consistency):
        """测试检测不一致"""
        # TODO: 实现不一致检测测试
        pass


@pytest.mark.integration
class TestCharacterNodesIntegration:
    """角色节点集成测试"""
    
    @pytest.fixture
    def real_manager(self, temp_database):
        """创建真实管理器"""
        return CharacterManager(database=temp_database)
    
    def test_full_character_workflow(self, real_manager, sample_character_data):
        """测试完整的角色工作流"""
        # 1. 创建角色
        created = real_manager.create_character(
            character_data=sample_character_data
        )
        assert created is not None
        
        # 2. 获取角色
        retrieved = real_manager.get_character(
            character_name=sample_character_data["name"]
        )
        assert retrieved is not None
        
        # 3. 更新角色
        updated_data = sample_character_data.copy()
        updated_data["age"] = 20
        updated = real_manager.update_character(
            character_name=sample_character_data["name"],
            updates=updated_data
        )
        assert updated["age"] == 20
        
        # 4. 删除角色
        deleted = real_manager.delete_character(
            character_name=sample_character_data["name"]
        )
        assert deleted is True
