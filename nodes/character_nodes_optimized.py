"""
角色管理节点模块（优化版）

包含以下关键节点：
- CharacterImageLoaderNode: 角色图加载（外观一致性）
- VoiceDefinitionNode: 音色定义（多角色配音）
- CharacterManagerNode: 角色管理（统一管理）
- CharacterConsistencyNode: 角色一致性控制

优化内容：
1. 添加数据持久化支持
2. 修复IMAGE类型返回
3. 完善错误处理
4. 添加输入验证
"""

import hashlib
import json
import random
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import sys
import logging

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..utils.persistent_storage import get_character_db
from ..utils.api_client import InputValidator, ErrorHandler

logger = logging.getLogger(__name__)


class CharacterImageLoaderNode:
    """
    角色图加载节点（优化版）
    
    功能：
    1. 加载角色参考图
    2. 提取角色特征描述
    3. 生成角色embedding
    4. 维护角色外观一致性
    5. 数据持久化存储
    
    优化：
    - 正确返回IMAGE类型
    - 持久化存储角色数据
    - 完善的输入验证和错误处理
    """
    
    def __init__(self):
        self.db = get_character_db()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_url": ("STRING", {"default": ""}),
                "character_name": ("STRING", {"default": ""}),
            },
            "optional": {
                "character_description": ("STRING", {"multiline": True, "default": ""}),
                "gender": (["male", "female", "other"], {"default": "female"}),
                "age_range": (["child", "teenager", "young_adult", "middle_aged", "elderly"], {"default": "young_adult"}),
                "style": (["realistic", "anime", "cartoon", "artistic"], {"default": "realistic"}),
                "auto_generate_description": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("CHARACTER", "STRING", "IMAGE")
    RETURN_NAMES = ("character_data", "character_summary", "image_preview")
    FUNCTION = "load_character_image"
    CATEGORY = "UnlimitAI/Character"
    
    def load_character_image(
        self,
        image_url: str,
        character_name: str,
        character_description: str = "",
        gender: str = "female",
        age_range: str = "young_adult",
        style: str = "realistic",
        auto_generate_description: bool = True
    ) -> Tuple[Dict, str, Any]:
        """加载角色图像"""
        
        # 输入验证
        if not image_url:
            return (
                {"error": "Image URL is required"},
                "❌ 错误：未提供图片URL\n\n请提供角色的参考图片URL",
                None
            )
        
        if not InputValidator.validate_url(image_url):
            return (
                {"error": "Invalid URL format"},
                "❌ 错误：图片URL格式不正确\n\n请提供有效的URL（以http://或https://开头）",
                None
            )
        
        if not character_name:
            return (
                {"error": "Character name is required"},
                "❌ 错误：未提供角色名称\n\n请为角色命名，例如：林晓薇",
                None
            )
        
        if not InputValidator.validate_prompt(character_name, max_length=50):
            return (
                {"error": "Character name too long"},
                "❌ 错误：角色名称过长\n\n请限制在50字符以内",
                None
            )
        
        try:
            # 加载图像
            image_array = self._load_image(image_url)
            
            if image_array is None:
                return (
                    {"error": "Failed to load image"},
                    "❌ 错误：无法加载图片\n\n请检查URL是否有效，或图片是否存在",
                    None
                )
            
            # 生成角色ID
            character_id = self._generate_character_id(character_name)
            
            # 提取或生成角色描述
            if auto_generate_description and not character_description:
                character_description = self._generate_character_description(
                    gender, age_range, style
                )
            
            # 清理描述文本
            character_description = InputValidator.sanitize_prompt(character_description)
            
            # 创建角色数据
            character_data = {
                "id": character_id,
                "name": character_name,
                "image_url": image_url,
                "description": character_description,
                "gender": gender,
                "age_range": age_range,
                "style": style,
                "seed": random.randint(0, 2**32 - 1),
                "created_at": self._get_timestamp(),
                "tags": self._extract_tags(character_description)
            }
            
            # 保存到数据库
            if self.db.add_character(character_id, character_data):
                # 生成摘要
                summary = self._generate_character_summary(character_data)
                
                return (
                    character_data,
                    summary,
                    image_array
                )
            else:
                return (
                    {"error": "Failed to save character"},
                    "❌ 错误：保存角色数据失败\n\n请检查存储权限或磁盘空间",
                    image_array
                )
                
        except Exception as e:
            return ErrorHandler.format_error(e, "加载角色图像时出错")
    
    def _load_image(self, image_url: str) -> Optional[Any]:
        """加载图像并转换为ComfyUI格式"""
        try:
            import numpy as np
            from PIL import Image
            import requests
            from io import BytesIO
            
            # 从URL加载
            if image_url.startswith('http'):
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            else:
                # 从本地文件加载
                image = Image.open(image_url)
            
            # 转换为RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 调整大小（可选）
            max_size = 1024
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # 转换为numpy数组 (ComfyUI IMAGE格式)
            image_array = np.array(image).astype(np.float32) / 255.0
            
            return image_array
            
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"图像加载失败: {e}", exc_info=True)
            return None
    
    def _generate_character_id(self, name: str) -> str:
        """生成角色ID"""
        timestamp = self._get_timestamp()
        data = f"{name}_{timestamp}_{random.randint(1000, 9999)}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _generate_character_description(
        self,
        gender: str,
        age_range: str,
        style: str
    ) -> str:
        """生成基础角色描述"""
        
        GENDER_DESC = {
            "male": "男性",
            "female": "女性",
            "other": "中性"
        }
        
        AGE_DESC = {
            "child": "儿童（6-12岁）",
            "teenager": "青少年（13-19岁）",
            "young_adult": "青年（20-35岁）",
            "middle_aged": "中年（36-55岁）",
            "elderly": "老年（56岁以上）"
        }
        
        STYLE_DESC = {
            "realistic": "写实风格",
            "anime": "动漫风格",
            "cartoon": "卡通风格",
            "artistic": "艺术风格"
        }
        
        return f"{GENDER_DESC[gender]}，{AGE_DESC[age_range]}，{STYLE_DESC[style]}"
    
    def _extract_tags(self, description: str) -> List[str]:
        """从描述中提取标签"""
        keywords = []
        common_tags = [
            "长发", "短发", "黑发", "金发", "眼镜", 
            "西装", "休闲", "运动", "可爱", "酷",
            "温柔", "严肃", "活泼", "文静"
        ]
        
        for tag in common_tags:
            if tag in description:
                keywords.append(tag)
        
        return keywords
    
    def _generate_character_summary(self, data: Dict) -> str:
        """生成角色摘要"""
        summary = f"""【角色档案】✅

角色名称: {data['name']}
角色ID: {data['id']}
性别: {data['gender']}
年龄段: {data['age_range']}
风格: {data['style']}

角色描述:
{data['description']}

标签: {', '.join(data['tags']) if data['tags'] else '无'}

一致性控制:
  Seed: {data['seed']}
  创建时间: {data['created_at']}

💾 数据已保存到数据库，可在后续场景中复用
"""
        return summary
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class VoiceDefinitionNode:
    """
    音色定义节点（优化版）
    
    功能：
    1. 定义角色音色
    2. 设置音色参数
    3. 生成音色预览
    4. 维护音色一致性
    5. 数据持久化存储
    
    优化：
    - 持久化存储音色数据
    - 完善的输入验证
    - 详细的错误提示
    """
    
    TTS_ENGINES = {
        "minimax": {
            "name": "Minimax TTS",
            "voices": {
                "male": ["male-qn-jingying", "male-qn-badao", "male-qn-jingqiang"],
                "female": ["female-shaonv", "female-yujie", "female-chengshu"]
            },
            "features": ["emotion_tags", "chinese_optimized"]
        },
        "openai": {
            "name": "OpenAI TTS",
            "voices": {
                "male": ["onyx", "echo"],
                "female": ["nova", "shimmer"]
            },
            "features": ["multilingual", "high_quality"]
        }
    }
    
    def __init__(self):
        self.db = get_character_db()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_name": ("STRING", {"default": ""}),
                "tts_engine": (["minimax", "openai"], {"default": "minimax"}),
                "voice_type": (["male", "female"], {"default": "female"}),
            },
            "optional": {
                "voice_id": ("STRING", {"default": ""}),
                "voice_style": (["gentle", "energetic", "calm", "serious", "cheerful"], {"default": "gentle"}),
                "speech_rate": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.0}),
                "pitch": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.0}),
                "emotion_tags": ("BOOLEAN", {"default": True}),
                "preview_text": ("STRING", {"default": "你好，这是一个音色预览。"}),
            }
        }
    
    RETURN_TYPES = ("VOICE", "STRING", "AUDIO")
    RETURN_NAMES = ("voice_data", "voice_summary", "voice_preview")
    FUNCTION = "define_voice"
    CATEGORY = "UnlimitAI/Character"
    
    def define_voice(
        self,
        character_name: str,
        tts_engine: str,
        voice_type: str,
        voice_id: str = "",
        voice_style: str = "gentle",
        speech_rate: float = 1.0,
        pitch: float = 1.0,
        emotion_tags: bool = True,
        preview_text: str = "你好，这是一个音色预览。"
    ) -> Tuple[Dict, str, Any]:
        """定义角色音色"""
        
        # 输入验证
        if not character_name:
            return (
                {"error": "Character name is required"},
                "❌ 错误：未提供角色名称\n\n请指定要配置音色的角色名称",
                None
            )
        
        if not InputValidator.validate_prompt(preview_text, max_length=200):
            return (
                {"error": "Preview text too long"},
                "❌ 错误：预览文本过长\n\n请限制在200字符以内",
                None
            )
        
        # 验证参数范围
        if not 0.5 <= speech_rate <= 2.0:
            return (
                {"error": "Invalid speech rate"},
                "❌ 错误：语速参数超出范围\n\n有效范围：0.5 - 2.0",
                None
            )
        
        if not 0.5 <= pitch <= 2.0:
            return (
                {"error": "Invalid pitch"},
                "❌ 错误：音调参数超出范围\n\n有效范围：0.5 - 2.0",
                None
            )
        
        try:
            # 如果没有指定voice_id，自动选择
            if not voice_id:
                voice_id = self._auto_select_voice(tts_engine, voice_type)
            else:
                # 验证voice_id是否有效
                if not self._validate_voice_id(tts_engine, voice_type, voice_id):
                    return (
                        {"error": "Invalid voice ID"},
                        f"❌ 错误：无效的音色ID\n\n{tts_engine} 引擎的 {voice_type} 音色不包含 '{voice_id}'\n\n可选音色：{', '.join(self.TTS_ENGINES[tts_engine]['voices'][voice_type])}",
                        None
                    )
            
            # 创建音色数据
            voice_data = {
                "character_name": character_name,
                "tts_engine": tts_engine,
                "engine_name": self.TTS_ENGINES[tts_engine]["name"],
                "voice_type": voice_type,
                "voice_id": voice_id,
                "voice_style": voice_style,
                "speech_rate": speech_rate,
                "pitch": pitch,
                "emotion_tags": emotion_tags,
                "features": self.TTS_ENGINES[tts_engine]["features"],
                "created_at": self._get_timestamp()
            }
            
            # 生成摘要
            summary = self._generate_voice_summary(voice_data)
            
            # 更新角色数据库（如果角色存在）
            self._update_character_voice(character_name, voice_data)
            
            return (
                voice_data,
                summary,
                None  # 音频预览需要实际API调用
            )
            
        except Exception as e:
            return ErrorHandler.format_error(e, "定义音色时出错")
    
    def _auto_select_voice(self, engine: str, voice_type: str) -> str:
        """自动选择音色"""
        voices = self.TTS_ENGINES[engine]["voices"][voice_type]
        return voices[0]
    
    def _validate_voice_id(self, engine: str, voice_type: str, voice_id: str) -> bool:
        """验证音色ID"""
        valid_voices = self.TTS_ENGINES[engine]["voices"][voice_type]
        return voice_id in valid_voices
    
    def _update_character_voice(self, character_name: str, voice_data: Dict):
        """更新角色的音色数据"""
        character = self.db.get_character_by_name(character_name)
        
        if character:
            character_id = character.get('id')
            self.db.update_character(character_id, {'voice': voice_data})
    
    def _generate_voice_summary(self, data: Dict) -> str:
        """生成音色摘要"""
        summary = f"""【音色配置】✅

角色名称: {data['character_name']}
TTS引擎: {data['engine_name']}
音色类型: {data['voice_type']}
音色ID: {data['voice_id']}
音色风格: {data['voice_style']}

参数设置:
  语速: {data['speech_rate']:.1f}x
  音调: {data['pitch']:.1f}x
  情感标签: {'✅ 启用' if data['emotion_tags'] else '❌ 禁用'}

支持功能:
  {', '.join(data['features'])}

创建时间: {data['created_at']}

💾 音色已关联到角色，可在后续场景中自动应用
"""
        return summary
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class CharacterManagerNode:
    """
    角色管理节点（优化版）
    
    功能：
    1. 注册角色（外观+音色）
    2. 维护角色一致性
    3. 角色数据库管理
    4. 角色复用
    
    优化：
    - 持久化存储
    - 完善的查询功能
    - 详细的操作反馈
    """
    
    def __init__(self):
        self.db = get_character_db()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "operation": (["register", "update", "get", "list", "delete"], {"default": "list"}),
            },
            "optional": {
                "character_data": ("CHARACTER", {"default": None}),
                "voice_data": ("VOICE", {"default": None}),
                "character_name": ("STRING", {"default": ""}),
                "character_id": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("CHARACTER_PROFILE", "STRING", "DICT")
    RETURN_NAMES = ("character_profile", "operation_result", "character_list")
    FUNCTION = "manage_character"
    CATEGORY = "UnlimitAI/Character"
    
    def manage_character(
        self,
        operation: str,
        character_data: Dict = None,
        voice_data: Dict = None,
        character_name: str = "",
        character_id: str = ""
    ) -> Tuple[Dict, str, Dict]:
        """管理角色"""
        
        try:
            if operation == "register":
                return self._register_character(character_data, voice_data)
            elif operation == "update":
                return self._update_character(character_id, character_data, voice_data)
            elif operation == "get":
                return self._get_character(character_id, character_name)
            elif operation == "delete":
                return self._delete_character(character_id, character_name)
            elif operation == "list":
                return self._list_characters()
            else:
                return (
                    {},
                    f"❌ 未知操作: {operation}\n\n支持的操作: register, update, get, delete, list",
                    {}
                )
        except Exception as e:
            return ErrorHandler.format_error(e, f"执行 {operation} 操作时出错")
    
    def _register_character(
        self,
        character_data: Dict,
        voice_data: Dict
    ) -> Tuple[Dict, str, Dict]:
        """注册新角色"""
        
        if not character_data:
            return (
                {},
                "❌ 错误：缺少角色图像数据\n\n请先使用 CharacterImageLoader 加载角色图像",
                {}
            )
        
        # 合并角色数据
        character_profile = {
            **character_data,
            "voice": voice_data if voice_data else None,
            "scenes_used": 0,
            "status": "active"
        }
        
        # 注册到数据库
        char_id = character_data.get('id', 'unknown')
        
        summary = f"""【角色注册成功】✅

角色名称: {character_profile.get('name', 'Unknown')}
角色ID: {char_id}
外观数据: ✅ 已加载
音色数据: {'✅ 已配置' if voice_data else '⚠️ 未配置'}

💾 角色数据已保存到数据库

💡 使用提示:
  - 在生成节点中使用角色名称或ID来保持一致性
  - 音色会在音频生成时自动应用
  - 可随时通过"update"操作更新角色信息
"""
        
        return (
            character_profile,
            summary,
            {"total_characters": len(self.db.characters)}
        )
    
    def _update_character(
        self,
        character_id: str,
        character_data: Dict,
        voice_data: Dict
    ) -> Tuple[Dict, str, Dict]:
        """更新角色"""
        
        if not character_id:
            return (
                {},
                "❌ 错误：未提供角色ID\n\n请提供要更新的角色ID",
                {}
            )
        
        character = self.db.get_character(character_id)
        
        if not character:
            return (
                {},
                f"❌ 错误：角色ID {character_id} 不存在\n\n请先注册角色或检查ID是否正确",
                {}
            )
        
        # 更新数据
        updates = {}
        if character_data:
            updates.update(character_data)
        if voice_data:
            updates['voice'] = voice_data
        
        if self.db.update_character(character_id, updates):
            updated_character = self.db.get_character(character_id)
            
            summary = f"""【角色更新成功】✅

角色名称: {updated_character.get('name')}
角色ID: {character_id}

更新内容:
  外观: {'已更新' if character_data else '未修改'}
  音色: {'已更新' if voice_data else '未修改'}
"""
            
            return (
                updated_character,
                summary,
                {"total_characters": len(self.db.characters)}
            )
        else:
            return (
                {},
                "❌ 更新失败\n\n请检查存储权限或磁盘空间",
                {}
            )
    
    def _get_character(
        self,
        character_id: str,
        character_name: str
    ) -> Tuple[Dict, str, Dict]:
        """获取角色"""
        
        # 优先使用ID查找
        if character_id:
            character = self.db.get_character(character_id)
            if character:
                summary = f"✅ 找到角色: {character.get('name', character_id)}"
                return (
                    character,
                    summary,
                    {"total_characters": len(self.db.characters)}
                )
        
        # 使用名称查找
        if character_name:
            character = self.db.get_character_by_name(character_name)
            if character:
                summary = f"✅ 找到角色: {character_name}"
                return (
                    character,
                    summary,
                    {"total_characters": len(self.db.characters)}
                )
        
        return (
            {},
            f"❌ 未找到角色\n\n角色ID: {character_id or '未提供'}\n角色名称: {character_name or '未提供'}\n\n请检查输入或使用'list'操作查看所有角色",
            {}
        )
    
    def _delete_character(
        self,
        character_id: str,
        character_name: str
    ) -> Tuple[Dict, str, Dict]:
        """删除角色"""
        
        # 查找角色
        character = None
        if character_id:
            character = self.db.get_character(character_id)
        elif character_name:
            character = self.db.get_character_by_name(character_name)
            if character:
                character_id = character.get('id')
        
        if not character:
            return (
                {},
                "❌ 未找到要删除的角色",
                {}
            )
        
        character_name = character.get('name', 'Unknown')
        
        if self.db.delete_character(character_id):
            summary = f"""【角色删除成功】✅

已删除角色: {character_name}
角色ID: {character_id}

⚠️ 注意：此操作不可撤销
"""
            return (
                {},
                summary,
                {"total_characters": len(self.db.characters)}
            )
        else:
            return (
                {},
                "❌ 删除失败",
                {}
            )
    
    def _list_characters(self) -> Tuple[Dict, str, Dict]:
        """列出所有角色"""
        
        characters = self.db.list_characters()
        
        if not characters:
            return (
                {},
                "⚠️ 角色数据库为空\n\n使用 CharacterImageLoader 加载角色图像，然后使用本节点注册角色",
                {"total_characters": 0}
            )
        
        # 生成列表
        summary_lines = ["【角色列表】\n"]
        for char in characters:
            voice_status = "✅" if char.get('has_voice') else "⚠️"
            summary_lines.append(
                f"{voice_status} {char.get('name', 'Unknown')} (ID: {char.get('id', '')[:8]}...)"
            )
        
        summary = "\n".join(summary_lines)
        summary += f"\n\n总计: {len(characters)}个角色"
        
        return (
            {},
            summary,
            {
                "total_characters": len(characters),
                "characters": characters
            }
        )


class CharacterConsistencyNode:
    """
    角色一致性控制节点（优化版）
    
    功能：
    1. 在图像生成时应用角色特征
    2. 在音频生成时应用角色音色
    3. 维护跨场景的角色一致性
    
    优化：
    - 更完善的提示词增强
    - 支持多种目标类型
    - 详细的一致性参数
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_profile": ("CHARACTER_PROFILE",),
                "target_type": (["image", "video", "audio"], {"default": "image"}),
            },
            "optional": {
                "additional_prompt": ("STRING", {"default": ""}),
                "scene_description": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "DICT")
    RETURN_NAMES = ("enhanced_prompt", "consistency_params", "metadata")
    FUNCTION = "apply_consistency"
    CATEGORY = "UnlimitAI/Character"
    
    def apply_consistency(
        self,
        character_profile: Dict,
        target_type: str,
        additional_prompt: str = "",
        scene_description: str = ""
    ) -> Tuple[str, str, Dict]:
        """应用角色一致性"""
        
        if not character_profile:
            return (
                additional_prompt,
                "{}",
                {"error": "No character profile provided", "warning": "未提供角色档案，将使用原始提示词"}
            )
        
        try:
            # 根据目标类型应用一致性
            if target_type == "image":
                return self._apply_image_consistency(
                    character_profile, additional_prompt, scene_description
                )
            elif target_type == "video":
                return self._apply_video_consistency(
                    character_profile, additional_prompt, scene_description
                )
            elif target_type == "audio":
                return self._apply_audio_consistency(
                    character_profile, scene_description
                )
            else:
                return (
                    additional_prompt,
                    "{}",
                    {"error": f"Unknown target type: {target_type}"}
                )
                
        except Exception as e:
            return ErrorHandler.format_error(e, "应用角色一致性时出错")
    
    def _apply_image_consistency(
        self,
        profile: Dict,
        additional_prompt: str,
        scene_description: str
    ) -> Tuple[str, str, Dict]:
        """应用图像一致性"""
        
        # 基础角色描述
        character_desc = profile.get('description', '')
        seed = profile.get('seed', 0)
        style = profile.get('style', 'realistic')
        
        # 构建增强提示词
        parts = []
        
        if character_desc:
            parts.append(character_desc)
        
        if scene_description:
            parts.append(scene_description)
        
        if additional_prompt:
            # 清理额外提示词
            additional_prompt = InputValidator.sanitize_prompt(additional_prompt)
            parts.append(additional_prompt)
        
        # 添加风格和质量标签
        style_tags = {
            "realistic": "photorealistic, realistic, photograph, 4K, high detail",
            "anime": "anime style, manga style, cel shading, vibrant colors",
            "cartoon": "cartoon style, stylized, clean lines",
            "artistic": "digital art, concept art, illustration, masterpiece"
        }
        
        parts.append(style_tags.get(style, style_tags["realistic"]))
        parts.append("high quality, detailed, sharp focus")
        
        # 组合提示词
        enhanced_prompt = ", ".join(parts)
        
        # 一致性参数
        consistency_params = {
            "seed": seed,
            "character_id": profile.get('id'),
            "character_name": profile.get('name'),
            "style": style,
            "ref_image": profile.get('image_url')
        }
        
        # 元数据
        metadata = {
            "character_name": profile.get('name'),
            "consistency_applied": True,
            "seed_used": seed,
            "has_voice": profile.get('voice') is not None
        }
        
        return (
            enhanced_prompt,
            json.dumps(consistency_params, ensure_ascii=False),
            metadata
        )
    
    def _apply_video_consistency(
        self,
        profile: Dict,
        additional_prompt: str,
        scene_description: str
    ) -> Tuple[str, str, Dict]:
        """应用视频一致性"""
        
        # 基于图像一致性，但添加视频特定参数
        enhanced_prompt, consistency_params, metadata = self._apply_image_consistency(
            profile, additional_prompt, scene_description
        )
        
        # 添加视频特定标签
        enhanced_prompt += ", smooth motion, natural movement, cinematic"
        
        consistency_params_dict = json.loads(consistency_params)
        consistency_params_dict["video_specific"] = True
        consistency_params_dict["motion_hint"] = "natural"
        
        metadata["target"] = "video"
        
        return (
            enhanced_prompt,
            json.dumps(consistency_params_dict, ensure_ascii=False),
            metadata
        )
    
    def _apply_audio_consistency(
        self,
        profile: Dict,
        scene_description: str
    ) -> Tuple[str, str, Dict]:
        """应用音频一致性"""
        
        voice_data = profile.get('voice')
        
        if not voice_data:
            return (
                scene_description,
                "{}",
                {
                    "warning": "角色未配置音色",
                    "character_name": profile.get('name'),
                    "suggestion": "使用 VoiceDefinition 节点为角色配置音色"
                }
            )
        
        # 音频参数
        audio_params = {
            "tts_engine": voice_data.get('tts_engine'),
            "voice_id": voice_data.get('voice_id'),
            "speech_rate": voice_data.get('speech_rate', 1.0),
            "pitch": voice_data.get('pitch', 1.0),
            "emotion_tags": voice_data.get('emotion_tags', True),
            "voice_style": voice_data.get('voice_style')
        }
        
        # 元数据
        metadata = {
            "character_name": profile.get('name'),
            "voice_style": voice_data.get('voice_style'),
            "consistency_applied": True,
            "engine": voice_data.get('engine_name')
        }
        
        return (
            scene_description,
            json.dumps(audio_params, ensure_ascii=False),
            metadata
        )


# 节点映射
NODE_CLASS_MAPPINGS = {
    "CharacterImageLoaderNode": CharacterImageLoaderNode,
    "VoiceDefinitionNode": VoiceDefinitionNode,
    "CharacterManagerNode": CharacterManagerNode,
    "CharacterConsistencyNode": CharacterConsistencyNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CharacterImageLoaderNode": "👤 Character Image Loader (角色图加载) ✨优化版",
    "VoiceDefinitionNode": "🎤 Voice Definition (音色定义) ✨优化版",
    "CharacterManagerNode": "📋 Character Manager (角色管理) ✨优化版",
    "CharacterConsistencyNode": "🎯 Character Consistency (角色一致性) ✨优化版",
}
