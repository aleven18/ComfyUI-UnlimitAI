"""
持久化存储单元测试
"""

import pytest
import json
from pathlib import Path
from utils.persistent_storage import (
    CharacterDatabase,
    SceneDatabase,
    ProjectDatabase
)


class TestCharacterDatabase:
    """角色数据库测试"""
    
    @pytest.fixture
    def db(self, temp_dir):
        """创建测试数据库"""
        db_path = temp_dir / "test_characters.json"
        return CharacterDatabase(str(db_path))
    
    def test_initialization(self, db):
        """测试初始化"""
        assert db is not None
        assert db.db_path.exists()
    
    def test_save_character(self, db, sample_character_data):
        """测试保存角色"""
        result = db.save_character(
            character_name=sample_character_data["name"],
            character_data=sample_character_data
        )
        
        assert result is True
        
        # 验证文件已创建
        assert db.db_path.exists()
    
    def test_load_character(self, db, sample_character_data):
        """测试加载角色"""
        # 先保存
        db.save_character(
            character_name=sample_character_data["name"],
            character_data=sample_character_data
        )
        
        # 加载
        result = db.load_character(
            character_name=sample_character_data["name"]
        )
        
        assert result is not None
        assert result["name"] == sample_character_data["name"]
    
    def test_load_nonexistent_character(self, db):
        """测试加载不存在的角色"""
        result = db.load_character(
            character_name="不存在的角色"
        )
        
        assert result is None
    
    def test_update_character(self, db, sample_character_data):
        """测试更新角色"""
        # 先保存
        db.save_character(
            character_name=sample_character_data["name"],
            character_data=sample_character_data
        )
        
        # 更新
        updated_data = sample_character_data.copy()
        updated_data["age"] = 20
        
        result = db.update_character(
            character_name=sample_character_data["name"],
            updates=updated_data
        )
        
        assert result is True
        
        # 验证更新
        loaded = db.load_character(
            character_name=sample_character_data["name"]
        )
        assert loaded["age"] == 20
    
    def test_delete_character(self, db, sample_character_data):
        """测试删除角色"""
        # 先保存
        db.save_character(
            character_name=sample_character_data["name"],
            character_data=sample_character_data
        )
        
        # 删除
        result = db.delete_character(
            character_name=sample_character_data["name"]
        )
        
        assert result is True
        
        # 验证删除
        loaded = db.load_character(
            character_name=sample_character_data["name"]
        )
        assert loaded is None
    
    def test_list_characters(self, db, sample_character_data):
        """测试列出所有角色"""
        # 保存多个角色
        db.save_character(
            character_name=sample_character_data["name"],
            character_data=sample_character_data
        )
        
        character2 = sample_character_data.copy()
        character2["name"] = "小红"
        db.save_character(
            character_name="小红",
            character_data=character2
        )
        
        # 列出
        result = db.list_characters()
        
        assert len(result) == 2
    
    def test_search_characters(self, db, sample_character_data):
        """测试搜索角色"""
        # 保存角色
        db.save_character(
            character_name=sample_character_data["name"],
            character_data=sample_character_data
        )
        
        # 搜索
        result = db.search_characters(
            query=sample_character_data["name"]
        )
        
        assert len(result) > 0
        assert result[0]["name"] == sample_character_data["name"]


class TestSceneDatabase:
    """场景数据库测试"""
    
    @pytest.fixture
    def db(self, temp_dir):
        """创建测试数据库"""
        db_path = temp_dir / "test_scenes.json"
        return SceneDatabase(str(db_path))
    
    def test_save_scene(self, db, sample_scene_data):
        """测试保存场景"""
        result = db.save_scene(
            scene_id=sample_scene_data["scene_id"],
            scene_data=sample_scene_data
        )
        
        assert result is True
    
    def test_load_scene(self, db, sample_scene_data):
        """测试加载场景"""
        # 先保存
        db.save_scene(
            scene_id=sample_scene_data["scene_id"],
            scene_data=sample_scene_data
        )
        
        # 加载
        result = db.load_scene(
            scene_id=sample_scene_data["scene_id"]
        )
        
        assert result is not None
        assert result["scene_id"] == sample_scene_data["scene_id"]
    
    def test_get_scenes_by_location(self, db, sample_scene_data):
        """测试按位置获取场景"""
        # 保存场景
        db.save_scene(
            scene_id=sample_scene_data["scene_id"],
            scene_data=sample_scene_data
        )
        
        # 按位置查询
        result = db.get_scenes_by_location(
            location=sample_scene_data["location"]
        )
        
        assert len(result) > 0
        assert result[0]["location"] == sample_scene_data["location"]
    
    def test_get_scenes_by_character(self, db, sample_scene_data):
        """测试按角色获取场景"""
        # 保存场景
        db.save_scene(
            scene_id=sample_scene_data["scene_id"],
            scene_data=sample_scene_data
        )
        
        # 按角色查询
        result = db.get_scenes_by_character(
            character_name="小明"
        )
        
        assert len(result) > 0


class TestProjectDatabase:
    """项目数据库测试"""
    
    @pytest.fixture
    def db(self, temp_dir):
        """创建测试数据库"""
        db_path = temp_dir / "test_projects.json"
        return ProjectDatabase(str(db_path))
    
    def test_create_project(self, db):
        """测试创建项目"""
        project_data = {
            "name": "测试项目",
            "description": "这是一个测试项目",
            "novel_content": "小说内容..."
        }
        
        result = db.create_project(
            project_id="project_001",
            project_data=project_data
        )
        
        assert result is True
    
    def test_load_project(self, db):
        """测试加载项目"""
        # 先创建
        project_data = {
            "name": "测试项目",
            "description": "这是一个测试项目"
        }
        db.create_project(
            project_id="project_001",
            project_data=project_data
        )
        
        # 加载
        result = db.load_project(
            project_id="project_001"
        )
        
        assert result is not None
        assert result["name"] == "测试项目"
    
    def test_update_project(self, db):
        """测试更新项目"""
        # 先创建
        project_data = {
            "name": "测试项目",
            "description": "这是一个测试项目"
        }
        db.create_project(
            project_id="project_001",
            project_data=project_data
        )
        
        # 更新
        updated_data = {
            "description": "更新后的描述"
        }
        result = db.update_project(
            project_id="project_001",
            updates=updated_data
        )
        
        assert result is True
        
        # 验证
        loaded = db.load_project(project_id="project_001")
        assert loaded["description"] == "更新后的描述"
    
    def test_list_projects(self, db):
        """测试列出项目"""
        # 创建多个项目
        db.create_project(
            project_id="project_001",
            project_data={"name": "项目1"}
        )
        db.create_project(
            project_id="project_002",
            project_data={"name": "项目2"}
        )
        
        # 列出
        result = db.list_projects()
        
        assert len(result) == 2


@pytest.mark.integration
class TestDatabaseIntegration:
    """数据库集成测试"""
    
    def test_database_persistence(self, temp_dir):
        """测试数据库持久化"""
        db_path = temp_dir / "test_persistence.json"
        
        # 创建数据库并保存数据
        db1 = CharacterDatabase(str(db_path))
        db1.save_character(
            character_name="测试角色",
            character_data={"name": "测试角色", "age": 18}
        )
        
        # 关闭并重新打开
        del db1
        
        # 重新加载数据库
        db2 = CharacterDatabase(str(db_path))
        result = db2.load_character(character_name="测试角色")
        
        assert result is not None
        assert result["name"] == "测试角色"
    
    def test_concurrent_access(self, temp_dir):
        """测试并发访问"""
        # TODO: 实现并发访问测试
        pass
    
    def test_large_dataset(self, temp_dir):
        """测试大数据集"""
        db_path = temp_dir / "test_large.json"
        db = CharacterDatabase(str(db_path))
        
        # 创建大量数据
        for i in range(100):
            db.save_character(
                character_name=f"角色{i}",
                character_data={"name": f"角色{i}", "index": i}
            )
        
        # 验证
        result = db.list_characters()
        assert len(result) == 100
