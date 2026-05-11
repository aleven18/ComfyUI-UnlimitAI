"""
角色管理节点模块

包含以下关键节点：
- CharacterImageLoaderNode: 角色图加载（外观一致性）
- VoiceDefinitionNode: 音色定义（多角色配音）
- CharacterManagerNode: 角色管理（统一管理）
- CharacterConsistencyNode: 角色一致性控制
"""

import logging
logger = logging.getLogger(__name__)

import hashlib
import json
import random
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class CharacterImageLoaderNode:
    """
    角色图加载节点
    
    功能：
    1. 加载角色参考图
    2. 提取角色特征描述
    3. 生成角色embedding
    4. 维护角色外观一致性
    """
    
    def __init__(self):
        self.character_database = {}
    
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
        
        if not image_url:
            return (
                {"error": "Image URL is required"},
                "❌ 错误：未提供图片URL",
                None
            )
        
        if not character_name:
            return (
                {"error": "Character name is required"},
                "❌ 错误：未提供角色名称",
                None
            )
        
        # 生成角色ID
        character_id = self._generate_character_id(character_name)
        
        # 提取或生成角色描述
        if auto_generate_description and not character_description:
            character_description = self._generate_character_description(
                gender, age_range, style
            )
        
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
            "embedding": None,  # 实际使用时可以存储图像embedding
            "created_at": self._get_timestamp(),
            "tags": self._extract_tags(character_description)
        }
        
        # 生成摘要
        summary = self._generate_character_summary(character_data)
        
        # 存储到数据库
        self.character_database[character_id] = character_data
        
        return (
            character_data,
            summary,
            image_url  # 在实际实现中，这里应该是加载的图像对象
        )
    
    def _generate_character_id(self, name: str) -> str:
        """生成角色ID"""
        timestamp = self._get_timestamp()
        data = f"{name}_{timestamp}"
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
        # 简单的关键词提取
        keywords = []
        common_tags = [
            "长发", "短发", "黑发", "金发", "眼镜", 
            "西装", "休闲", "运动", "可爱", "酷"
        ]
        
        for tag in common_tags:
            if tag in description:
                keywords.append(tag)
        
        return keywords
    
    def _generate_character_summary(self, data: Dict) -> str:
        """生成角色摘要"""
        summary = f"""【角色档案】

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
"""
        return summary
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class VoiceDefinitionNode:
    """
    音色定义节点
    
    功能：
    1. 定义角色音色
    2. 设置音色参数
    3. 生成音色预览
    4. 维护音色一致性
    """
    
    # 支持的TTS引擎
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
        self.voice_database = {}
    
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
        
        if not character_name:
            return (
                {"error": "Character name is required"},
                "❌ 错误：未提供角色名称",
                None
            )
        
        # 如果没有指定voice_id，自动选择
        if not voice_id:
            voice_id = self._auto_select_voice(tts_engine, voice_type)
        
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
        
        # 存储到数据库
        voice_key = f"{character_name}_voice"
        self.voice_database[voice_key] = voice_data
        
        return (
            voice_data,
            summary,
            None  # 在实际实现中，这里应该是生成的音频预览
        )
    
    def _auto_select_voice(self, engine: str, voice_type: str) -> str:
        """自动选择音色"""
        voices = self.TTS_ENGINES[engine]["voices"][voice_type]
        return voices[0]  # 返回默认音色
    
    def _generate_voice_summary(self, data: Dict) -> str:
        """生成音色摘要"""
        summary = f"""【音色配置】

角色名称: {data['character_name']}
TTS引擎: {data['engine_name']}
音色类型: {data['voice_type']}
音色ID: {data['voice_id']}
音色风格: {data['voice_style']}

参数设置:
  语速: {data['speech_rate']:.1f}x
  音调: {data['pitch']:.1f}x
  情感标签: {'启用' if data['emotion_tags'] else '禁用'}

支持功能:
  {', '.join(data['features'])}

创建时间: {data['created_at']}
"""
        return summary
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class CharacterManagerNode:
    """
    角色管理节点
    
    功能：
    1. 注册角色（外观+音色）
    2. 维护角色一致性
    3. 角色数据库管理
    4. 角色复用
    """
    
    def __init__(self):
        self.character_registry = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "operation": (["register", "update", "get", "list"], {"default": "register"}),
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
        
        if operation == "register":
            return self._register_character(character_data, voice_data)
        elif operation == "update":
            return self._update_character(character_id, character_data, voice_data)
        elif operation == "get":
            return self._get_character(character_id, character_name)
        elif operation == "list":
            return self._list_characters()
        else:
            return (
                {},
                f"❌ 未知操作: {operation}",
                {}
            )
    
    def _register_character(
        self,
        character_data: Dict,
        voice_data: Dict
    ) -> Tuple[Dict, str, Dict]:
        """注册新角色"""
        
        if not character_data:
            return (
                {},
                "❌ 错误：缺少角色图像数据",
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
        self.character_registry[char_id] = character_profile
        
        # 生成结果
        summary = f"""【角色注册成功】

角色名称: {character_profile.get('name', 'Unknown')}
角色ID: {char_id}
外观数据: ✅ 已加载
音色数据: {'✅ 已配置' if voice_data else '⚠️ 未配置'}

可以在生成节点中使用此角色ID来保持一致性。
"""
        
        return (
            character_profile,
            summary,
            {"total_characters": len(self.character_registry)}
        )
    
    def _update_character(
        self,
        character_id: str,
        character_data: Dict,
        voice_data: Dict
    ) -> Tuple[Dict, str, Dict]:
        """更新角色"""
        
        if not character_id or character_id not in self.character_registry:
            return (
                {},
                f"❌ 错误：角色ID {character_id} 不存在",
                {}
            )
        
        # 更新数据
        profile = self.character_registry[character_id]
        
        if character_data:
            profile.update(character_data)
        
        if voice_data:
            profile['voice'] = voice_data
        
        summary = f"✅ 角色 {profile.get('name', character_id)} 已更新"
        
        return (
            profile,
            summary,
            {"total_characters": len(self.character_registry)}
        )
    
    def _get_character(
        self,
        character_id: str,
        character_name: str
    ) -> Tuple[Dict, str, Dict]:
        """获取角色"""
        
        # 优先使用ID查找
        if character_id and character_id in self.character_registry:
            profile = self.character_registry[character_id]
            summary = f"✅ 找到角色: {profile.get('name', character_id)}"
            return (profile, summary, {"total_characters": len(self.character_registry)})
        
        # 使用名称查找
        if character_name:
            for char_id, profile in self.character_registry.items():
                if profile.get('name') == character_name:
                    summary = f"✅ 找到角色: {character_name}"
                    return (profile, summary, {"total_characters": len(self.character_registry)})
        
        return (
            {},
            f"❌ 未找到角色: {character_name or character_id}",
            {}
        )
    
    def _list_characters(self) -> Tuple[Dict, str, Dict]:
        """列出所有角色"""
        
        if not self.character_registry:
            return (
                {},
                "⚠️ 角色数据库为空",
                {"total_characters": 0}
            )
        
        # 生成列表
        char_list = []
        for char_id, profile in self.character_registry.items():
            char_list.append({
                "id": char_id,
                "name": profile.get('name', 'Unknown'),
                "has_voice": profile.get('voice') is not None,
                "status": profile.get('status', 'active')
            })
        
        # 生成摘要
        summary_lines = ["【角色列表】\n"]
        for char in char_list:
            voice_status = "✅" if char['has_voice'] else "⚠️"
            summary_lines.append(
                f"{voice_status} {char['name']} (ID: {char['id'][:8]}...)"
            )
        
        summary = "\n".join(summary_lines)
        
        return (
            {},
            summary,
            {
                "total_characters": len(self.character_registry),
                "characters": char_list
            }
        )


class CharacterConsistencyNode:
    """
    角色一致性控制节点
    
    功能：
    1. 在图像生成时应用角色特征
    2. 在音频生成时应用角色音色
    3. 维护跨场景的角色一致性
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
                {"error": "No character profile provided"}
            )
        
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
            return (additional_prompt, "{}", {"error": f"Unknown target type: {target_type}"})
    
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
            parts.append(additional_prompt)
        
        # 添加风格和质量标签
        style_tags = {
            "realistic": "photorealistic, realistic, photograph",
            "anime": "anime style, manga style, cel shading",
            "cartoon": "cartoon style, stylized",
            "artistic": "digital art, concept art, illustration"
        }
        
        parts.append(style_tags.get(style, style_tags["realistic"]))
        parts.append("high quality, detailed, sharp focus")
        
        # 组合提示词
        enhanced_prompt = ", ".join(parts)
        
        # 一致性参数
        consistency_params = {
            "seed": seed,
            "character_id": profile.get('id'),
            "style": style
        }
        
        # 元数据
        metadata = {
            "character_name": profile.get('name'),
            "consistency_applied": True,
            "seed_used": seed
        }
        
        return (
            enhanced_prompt,
            json.dumps(consistency_params),
            metadata
        )
    
    def _apply_video_consistency(
        self,
        profile: Dict,
        additional_prompt: str,
        scene_description: str
    ) -> Tuple[str, str, Dict]:
        """应用视频一致性"""
        
        # 类似图像一致性，但添加视频特定参数
        enhanced_prompt, consistency_params, metadata = self._apply_image_consistency(
            profile, additional_prompt, scene_description
        )
        
        # 添加视频特定标签
        enhanced_prompt += ", smooth motion, natural movement"
        
        consistency_params_dict = json.loads(consistency_params)
        consistency_params_dict["video_specific"] = True
        
        metadata["target"] = "video"
        
        return (
            enhanced_prompt,
            json.dumps(consistency_params_dict),
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
                {"warning": "No voice data in character profile"}
            )
        
        # 音频参数
        audio_params = {
            "tts_engine": voice_data.get('tts_engine'),
            "voice_id": voice_data.get('voice_id'),
            "speech_rate": voice_data.get('speech_rate', 1.0),
            "pitch": voice_data.get('pitch', 1.0),
            "emotion_tags": voice_data.get('emotion_tags', True)
        }
        
        # 元数据
        metadata = {
            "character_name": profile.get('name'),
            "voice_style": voice_data.get('voice_style'),
            "consistency_applied": True
        }
        
        return (
            scene_description,
            json.dumps(audio_params),
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
    "CharacterImageLoaderNode": "👤 Character Image Loader (角色图加载)",
    "VoiceDefinitionNode": "🎤 Voice Definition (音色定义)",
    "CharacterManagerNode": "📋 Character Manager (角色管理)",
    "CharacterConsistencyNode": "🎯 Character Consistency (角色一致性)",
}
