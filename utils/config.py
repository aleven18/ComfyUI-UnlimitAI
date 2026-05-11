"""
配置管理系统

特性：
- 支持多层配置（环境变量 > 配置文件 > 默认值）
- 支持配置验证
- 支持配置热重载
- 支持配置继承

使用方法:
    from utils.config import Config
    
    config = Config.load()
    api_key = config.get("api_key")
    model = config.get("default_model.text")
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from functools import lru_cache
import logging

from utils.exceptions import ConfigError, MissingAPIKeyError


logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """模型配置"""
    default: str
    options: List[str] = field(default_factory=list)


@dataclass
class APIConfig:
    """API配置"""
    api_key: str
    base_url: str = "https://api.unlimitai.org"
    timeout: int = 60
    max_retries: int = 3


@dataclass
class GenerationConfig:
    """生成参数配置"""
    default_image_size: str = "1024x1024"
    default_video_duration: float = 5.0
    default_audio_sample_rate: int = 22050
    default_music_duration: float = 30.0


@dataclass
class StorageConfig:
    """存储配置"""
    data_dir: str = "data"
    character_db: str = "data/characters.json"
    scene_db: str = "data/scenes.json"
    project_db: str = "data/projects.json"
    cache_ttl: int = 3600


class Config:
    """
    配置管理器
    
    配置优先级：
    1. 环境变量（最高）
    2. 配置文件
    3. 默认值（最低）
    
    Examples:
        >>> config = Config.load()
        >>> api_key = config.api.api_key
        >>> model = config.models.text.default
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        env_file: Optional[str] = None
    ):
        self.config_path = config_path or "config.yaml"
        self.env_file = env_file or ".env"
        
        self._config: Dict[str, Any] = {}
        self._env_config: Dict[str, Any] = {}
        self._file_config: Dict[str, Any] = {}
        
        self._load()
    
    def _load(self):
        """加载配置"""
        # 1. 加载环境变量
        self._load_env()
        
        # 2. 加载配置文件
        self._load_file()
        
        # 3. 合并配置
        self._merge()
        
        # 4. 验证配置
        self._validate()
        
        logger.info("配置加载完成")
    
    def _load_env(self):
        """加载环境变量"""
        # 尝试从.env文件加载
        self._load_env_file()
        
        # 从系统环境变量加载
        self._env_config = {
            "api_key": os.getenv("UNITED_API_KEY"),
            "api_base_url": os.getenv("UNITED_API_BASE_URL"),
            "api_timeout": self._parse_int(os.getenv("API_TIMEOUT")),
            "max_retries": self._parse_int(os.getenv("MAX_RETRIES")),
            "log_level": os.getenv("LOG_LEVEL"),
            "log_file": os.getenv("LOG_FILE"),
            "log_colors": self._parse_bool(os.getenv("LOG_COLORS")),
            "default_text_model": os.getenv("DEFAULT_TEXT_MODEL"),
            "default_image_model": os.getenv("DEFAULT_IMAGE_MODEL"),
            "default_video_model": os.getenv("DEFAULT_VIDEO_MODEL"),
            "default_audio_model": os.getenv("DEFAULT_AUDIO_MODEL"),
            "default_music_model": os.getenv("DEFAULT_MUSIC_MODEL"),
            "default_image_size": os.getenv("DEFAULT_IMAGE_SIZE"),
            "default_video_duration": self._parse_float(os.getenv("DEFAULT_VIDEO_DURATION")),
            "data_dir": os.getenv("DATA_DIR"),
            "debug": self._parse_bool(os.getenv("DEBUG")),
            "dev_mode": self._parse_bool(os.getenv("DEV_MODE")),
        }
        
        # 移除None值
        self._env_config = {k: v for k, v in self._env_config.items() if v is not None}
    
    def _load_env_file(self):
        """从.env文件加载环境变量"""
        env_path = Path(self.env_file)
        
        if not env_path.exists():
            logger.debug(f".env文件不存在: {env_path}")
            return
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 设置环境变量（如果尚未设置）
                        if key not in os.environ:
                            os.environ[key] = value
            
            logger.debug(f"从.env文件加载配置: {env_path}")
            
        except Exception as e:
            logger.warning(f"加载.env文件失败: {e}")
    
    def _load_file(self):
        """加载配置文件"""
        config_path = Path(self.config_path)
        
        if not config_path.exists():
            logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix in ['.yaml', '.yml']:
                    self._file_config = yaml.safe_load(f) or {}
                elif config_path.suffix == '.json':
                    self._file_config = json.load(f)
                else:
                    logger.warning(f"不支持的配置文件格式: {config_path.suffix}")
                    
            logger.debug(f"从配置文件加载: {config_path}")
            
        except Exception as e:
            logger.warning(f"加载配置文件失败: {e}")
    
    def _merge(self):
        """合并配置"""
        # 默认配置
        default_config = self._get_defaults()
        
        # 合并顺序：默认值 < 文件配置 < 环境变量
        self._config = self._deep_merge(default_config, self._file_config)
        self._config = self._deep_merge(self._config, self._env_config)
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _get_defaults(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "api": {
                "api_key": "",
                "base_url": "https://api.unlimitai.org",
                "timeout": 60,
                "max_retries": 3,
            },
            "models": {
                "text": {
                    "default": "deepseek-chat",
                    "options": ["deepseek-chat", "gpt-4", "claude-3-opus"]
                },
                "image": {
                    "default": "flux.1-schnell",
                    "options": ["flux.1-schnell", "flux.1-dev", "ideogram-v2"]
                },
                "video": {
                    "default": "kling-video-v2",
                    "options": ["kling-video-v2", "runway-gen3-turbo"]
                },
                "audio": {
                    "default": "tts-1",
                    "options": ["tts-1", "tts-1-hd", "minimax-tts"]
                },
                "music": {
                    "default": "musicgen",
                    "options": ["musicgen", "stable-audio-2.0"]
                }
            },
            "generation": {
                "default_image_size": "1024x1024",
                "default_video_duration": 5.0,
                "default_audio_sample_rate": 22050,
                "default_music_duration": 30.0,
            },
            "storage": {
                "data_dir": "data",
                "character_db": "data/characters.json",
                "scene_db": "data/scenes.json",
                "project_db": "data/projects.json",
                "cache_ttl": 3600,
            },
            "logging": {
                "level": "INFO",
                "file": "logs/unlimitai.log",
                "colors": True,
            },
            "performance": {
                "cache_enabled": True,
                "async_enabled": True,
            },
            "development": {
                "debug": False,
                "dev_mode": False,
            }
        }
    
    def _validate(self):
        """验证配置"""
        # 验证API Key
        if not self._config.get("api", {}).get("api_key"):
            logger.warning("未设置API Key，某些功能可能无法使用")
        
        # 验证模型名称
        models = self._config.get("models", {})
        for model_type, model_config in models.items():
            default_model = model_config.get("default")
            if default_model and default_model not in model_config.get("options", []):
                logger.warning(
                    f"默认{model_type}模型 '{default_model}' 不在可用选项中"
                )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        支持点分隔的嵌套键，例如 "models.text.default"
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            配置值
        
        Examples:
            >>> config.get("api_key")
            'your_api_key'
            
            >>> config.get("models.text.default")
            'deepseek-chat'
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值（运行时）
        
        Args:
            key: 配置键
            value: 配置值
        
        Note:
            此方法仅在运行时生效，不会保存到文件
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"设置配置: {key} = {value}")
    
    def save(self, path: Optional[str] = None):
        """
        保存配置到文件
        
        Args:
            path: 保存路径（默认为原配置文件路径）
        """
        save_path = Path(path or self.config_path)
        
        try:
            # 确保目录存在
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            with open(save_path, 'w', encoding='utf-8') as f:
                if save_path.suffix in ['.yaml', '.yml']:
                    yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
                elif save_path.suffix == '.json':
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到: {save_path}")
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            raise ConfigError(f"保存配置失败: {e}")
    
    def reload(self):
        """重新加载配置"""
        logger.info("重新加载配置...")
        self._load()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self._config.copy()
    
    def __repr__(self) -> str:
        return f"Config(api_key={'***' if self.get('api_key') else 'None'})"
    
    @staticmethod
    def _parse_int(value: Optional[str]) -> Optional[int]:
        """解析整数"""
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None
    
    @staticmethod
    def _parse_float(value: Optional[str]) -> Optional[float]:
        """解析浮点数"""
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None
    
    @staticmethod
    def _parse_bool(value: Optional[str]) -> Optional[bool]:
        """解析布尔值"""
        if value is None:
            return None
        return value.lower() in ['true', '1', 'yes', 'on']
    
    @classmethod
    @lru_cache(maxsize=1)
    def load(cls, config_path: Optional[str] = None, env_file: Optional[str] = None) -> 'Config':
        """
        加载配置（单例模式）
        
        Args:
            config_path: 配置文件路径
            env_file: 环境变量文件路径
        
        Returns:
            Config实例
        
        Examples:
            >>> config = Config.load()
            >>> config.get("api_key")
        """
        return cls(config_path=config_path, env_file=env_file)


def get_config() -> Config:
    """获取全局配置实例"""
    return Config.load()


if __name__ == "__main__":
    # 演示配置系统
    config = Config.load()
    
    print(f"API Key: {config.get('api_key', 'not set')}")
    print(f"默认文本模型: {config.get('models.text.default')}")
    print(f"默认图像模型: {config.get('models.image.default')}")
    print(f"配置: {config}")
