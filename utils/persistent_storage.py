"""
数据持久化管理模块

提供角色数据和场景数据的持久化存储
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
import logging

logger = logging.getLogger(__name__)


class PersistentStorage:
    """持久化存储管理器"""
    
    def __init__(self, storage_dir: str = "data"):
        """
        初始化存储管理器
        
        Args:
            storage_dir: 存储目录路径
        """
        self.base_path = Path(__file__).parent.parent / storage_dir
        self.base_path.mkdir(exist_ok=True, parents=True)
        
        # 线程锁，防止并发写入冲突
        self._lock = threading.Lock()
        
        # 缓存
        self._cache = {}
    
    def _get_file_path(self, filename: str) -> Path:
        """获取文件完整路径"""
        return self.base_path / filename
    
    def save_json(self, filename: str, data: Dict) -> bool:
        """
        保存JSON数据到文件
        
        Args:
            filename: 文件名
            data: 要保存的数据
            
        Returns:
            是否保存成功
        """
        file_path = self._get_file_path(filename)
        
        try:
            with self._lock:
                # 添加元数据
                if isinstance(data, dict):
                    data['_metadata'] = {
                        'saved_at': datetime.now().isoformat(),
                        'version': '1.0'
                    }
                
                # 写入临时文件
                temp_path = file_path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 原子性替换
                temp_path.replace(file_path)
                
                # 更新缓存
                self._cache[filename] = data
                
                return True
                
        except Exception as e:
            logger.error(f"保存数据失败 {filename}: {e}", exc_info=True)
            return False
    
    def load_json(self, filename: str, use_cache: bool = True) -> Optional[Dict]:
        """
        从文件加载JSON数据
        
        Args:
            filename: 文件名
            use_cache: 是否使用缓存
            
        Returns:
            加载的数据，如果文件不存在返回None
        """
        # 检查缓存
        if use_cache and filename in self._cache:
            return self._cache[filename]
        
        file_path = self._get_file_path(filename)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新缓存
            self._cache[filename] = data
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败 {filename}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"加载数据失败 {filename}: {e}", exc_info=True)
            return None
    
    def delete(self, filename: str) -> bool:
        """
        删除数据文件
        
        Args:
            filename: 文件名
            
        Returns:
            是否删除成功
        """
        file_path = self._get_file_path(filename)
        
        try:
            with self._lock:
                if file_path.exists():
                    file_path.unlink()
                
                # 清除缓存
                if filename in self._cache:
                    del self._cache[filename]
                
                return True
                
        except Exception as e:
            logger.error(f"删除数据失败 {filename}: {e}", exc_info=True)
            return False
    
    def exists(self, filename: str) -> bool:
        """检查文件是否存在"""
        return self._get_file_path(filename).exists()
    
    def list_files(self, pattern: str = "*.json") -> List[str]:
        """列出所有数据文件"""
        return [f.name for f in self.base_path.glob(pattern)]


class CharacterDatabase:
    """角色数据库"""
    
    DATABASE_FILE = "characters.json"
    
    def __init__(self):
        self.storage = PersistentStorage()
        self._load_database()
    
    def _load_database(self):
        """加载角色数据库"""
        data = self.storage.load_json(self.DATABASE_FILE)
        if data and 'characters' in data:
            self.characters = data['characters']
        else:
            self.characters = {}
    
    def _save_database(self):
        """保存角色数据库"""
        data = {
            'characters': self.characters,
            'total_count': len(self.characters),
            'last_updated': datetime.now().isoformat()
        }
        return self.storage.save_json(self.DATABASE_FILE, data)
    
    def add_character(self, character_id: str, character_data: Dict) -> bool:
        """添加角色"""
        self.characters[character_id] = character_data
        return self._save_database()
    
    def get_character(self, character_id: str) -> Optional[Dict]:
        """获取角色"""
        return self.characters.get(character_id)
    
    def get_character_by_name(self, name: str) -> Optional[Dict]:
        """通过名称获取角色"""
        for char_id, char_data in self.characters.items():
            if char_data.get('name') == name:
                return char_data
        return None
    
    def update_character(self, character_id: str, updates: Dict) -> bool:
        """更新角色数据"""
        if character_id not in self.characters:
            return False
        
        self.characters[character_id].update(updates)
        return self._save_database()
    
    def delete_character(self, character_id: str) -> bool:
        """删除角色"""
        if character_id in self.characters:
            del self.characters[character_id]
            return self._save_database()
        return False
    
    def list_characters(self) -> List[Dict]:
        """列出所有角色"""
        return [
            {
                'id': char_id,
                'name': char_data.get('name'),
                'has_voice': char_data.get('voice') is not None,
                'created_at': char_data.get('created_at')
            }
            for char_id, char_data in self.characters.items()
        ]
    
    def search_characters(self, query: str) -> List[Dict]:
        """搜索角色"""
        results = []
        query_lower = query.lower()
        
        for char_id, char_data in self.characters.items():
            # 搜索名称和描述
            if (query_lower in char_data.get('name', '').lower() or
                query_lower in char_data.get('description', '').lower()):
                results.append(char_data)
        
        return results


class SceneDatabase:
    """场景数据库"""
    
    DATABASE_FILE = "scenes.json"
    
    def __init__(self):
        self.storage = PersistentStorage()
        self._load_database()
    
    def _load_database(self):
        """加载场景数据库"""
        data = self.storage.load_json(self.DATABASE_FILE)
        if data and 'scenes' in data:
            self.scenes = data['scenes']
        else:
            self.scenes = {}
    
    def _save_database(self):
        """保存场景数据库"""
        data = {
            'scenes': self.scenes,
            'total_count': len(self.scenes),
            'last_updated': datetime.now().isoformat()
        }
        return self.storage.save_json(self.DATABASE_FILE, data)
    
    def add_scene(self, scene_id: str, scene_data: Dict) -> bool:
        """添加场景"""
        self.scenes[scene_id] = scene_data
        return self._save_database()
    
    def get_scene(self, scene_id: str) -> Optional[Dict]:
        """获取场景"""
        return self.scenes.get(scene_id)
    
    def get_scenes_by_project(self, project_id: str) -> List[Dict]:
        """获取项目的所有场景"""
        return [
            scene_data for scene_data in self.scenes.values()
            if scene_data.get('project_id') == project_id
        ]
    
    def update_scene(self, scene_id: str, updates: Dict) -> bool:
        """更新场景"""
        if scene_id not in self.scenes:
            return False
        
        self.scenes[scene_id].update(updates)
        return self._save_database()
    
    def delete_scene(self, scene_id: str) -> bool:
        """删除场景"""
        if scene_id in self.scenes:
            del self.scenes[scene_id]
            return self._save_database()
        return False


class ProjectDatabase:
    """项目数据库"""
    
    DATABASE_FILE = "projects.json"
    
    def __init__(self):
        self.storage = PersistentStorage()
        self._load_database()
    
    def _load_database(self):
        """加载项目数据库"""
        data = self.storage.load_json(self.DATABASE_FILE)
        if data and 'projects' in data:
            self.projects = data['projects']
        else:
            self.projects = {}
    
    def _save_database(self):
        """保存项目数据库"""
        data = {
            'projects': self.projects,
            'total_count': len(self.projects),
            'last_updated': datetime.now().isoformat()
        }
        return self.storage.save_json(self.DATABASE_FILE, data)
    
    def create_project(self, project_id: str, project_data: Dict) -> bool:
        """创建项目"""
        self.projects[project_id] = {
            **project_data,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        return self._save_database()
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取项目"""
        return self.projects.get(project_id)
    
    def update_project(self, project_id: str, updates: Dict) -> bool:
        """更新项目"""
        if project_id not in self.projects:
            return False
        
        self.projects[project_id].update(updates)
        return self._save_database()
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        if project_id in self.projects:
            del self.projects[project_id]
            return self._save_database()
        return False
    
    def list_projects(self, status: str = None) -> List[Dict]:
        """列出项目"""
        projects = []
        for proj_id, proj_data in self.projects.items():
            if status is None or proj_data.get('status') == status:
                projects.append({
                    'id': proj_id,
                    **proj_data
                })
        return projects


class CacheManager:
    """缓存管理器"""
    
    CACHE_FILE = "cache.json"
    MAX_CACHE_SIZE = 1000
    
    def __init__(self):
        self.storage = PersistentStorage()
        self._load_cache()
    
    def _load_cache(self):
        """加载缓存"""
        data = self.storage.load_json(self.CACHE_FILE)
        if data and 'cache' in data:
            self.cache = data['cache']
        else:
            self.cache = {}
    
    def _save_cache(self):
        """保存缓存"""
        data = {
            'cache': self.cache,
            'count': len(self.cache),
            'last_updated': datetime.now().isoformat()
        }
        return self.storage.save_json(self.CACHE_FILE, data)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_item = self.cache.get(key)
        if cache_item:
            # 检查是否过期
            expires_at = cache_item.get('expires_at')
            if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                del self.cache[key]
                return None
            return cache_item.get('value')
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 存活时间（秒），默认1小时
        """
        # 检查缓存大小
        if len(self.cache) >= self.MAX_CACHE_SIZE:
            # 删除最旧的缓存项
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].get('created_at', '')
            )
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat() if ttl else None
        }
        self._save_cache()
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
            self._save_cache()
    
    def clear(self):
        """清空缓存"""
        self.cache = {}
        self._save_cache()


# 从datetime导入timedelta
from datetime import timedelta


# 全局实例
_character_db = None
_scene_db = None
_project_db = None
_cache_manager = None


def get_character_db() -> CharacterDatabase:
    """获取角色数据库实例"""
    global _character_db
    if _character_db is None:
        _character_db = CharacterDatabase()
    return _character_db


def get_scene_db() -> SceneDatabase:
    """获取场景数据库实例"""
    global _scene_db
    if _scene_db is None:
        _scene_db = SceneDatabase()
    return _scene_db


def get_project_db() -> ProjectDatabase:
    """获取项目数据库实例"""
    global _project_db
    if _project_db is None:
        _project_db = ProjectDatabase()
    return _project_db


def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
