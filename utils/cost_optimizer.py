"""
成本优化工具模块

提供多种降本提质的实用工具：
- 两阶段生成
- 智能模型选择
- 提示词优化
- 资源复用
- 缓存系统
"""

import hashlib
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TwoStageGenerator:
    """两阶段生成器"""
    
    PREVIEW_MODELS = {
        "text": "deepseek-chat",
        "image": "flux-schnell",
        "video": "vidu2",
        "audio": "tts-1",
        "music": "suno-inspiration"
    }
    
    PRODUCTION_MODELS = {
        "text": "deepseek-chat",  # 文本无需重复
        "image": "flux-pro",
        "video": "kling-v2",
        "audio": "speech-02-turbo",
        "music": "suno-custom"
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.preview_results = {}
        self.approved_scenes = set()
    
    def generate_preview(self, scene: Dict) -> Dict:
        """生成预览版本"""
        scene_id = scene.get('scene_number', 0)
        
        # 使用经济模型快速生成
        preview = {
            "scene_id": scene_id,
            "image": self._generate_image_preview(scene),
            "video": self._generate_video_preview(scene),
            "audio": self._generate_audio_preview(scene),
            "cost": self._calculate_preview_cost()
        }
        
        self.preview_results[scene_id] = preview
        return preview
    
    def generate_final(self, scene_id: int) -> Dict:
        """生成最终版本（仅对已批准的场景）"""
        if scene_id not in self.approved_scenes:
            raise ValueError(f"场景 {scene_id} 未批准，无法生成最终版本")
        
        preview = self.preview_results.get(scene_id)
        if not preview:
            raise ValueError(f"场景 {scene_id} 没有预览版本")
        
        scene = preview.get('scene')
        
        # 使用高质量模型生成最终版本
        final = {
            "scene_id": scene_id,
            "image": self._generate_image_final(scene),
            "video": self._generate_video_final(scene),
            "audio": self._generate_audio_final(scene),
            "cost": self._calculate_final_cost()
        }
        
        return final
    
    def approve_scene(self, scene_id: int):
        """批准场景，允许生成最终版本"""
        self.approved_scenes.add(scene_id)
    
    def _calculate_preview_cost(self) -> float:
        """计算预览成本"""
        return 0.20  # $0.20/场景
    
    def _calculate_final_cost(self) -> float:
        """计算最终成本"""
        return 0.47  # $0.47/场景


class SmartModelSelector:
    """智能模型选择器"""
    
    COMPLEXITY_WEIGHTS = {
        "character_count": 1.0,
        "has_effects": 2.0,
        "has_text": 1.5,
        "outdoor_scene": 0.5,
        "complex_composition": 1.0
    }
    
    MODEL_COSTS = {
        "flux-schnell": 0.003,
        "flux-pro": 0.03,
        "imagen-4": 0.04,
        "vidu2": 0.15,
        "kling-v2": 0.30
    }
    
    def select_image_model(self, scene: Dict) -> Tuple[str, str]:
        """根据场景选择图像模型"""
        complexity = self._analyze_scene_complexity(scene)
        
        if complexity == "simple":
            return "flux-schnell", "简单场景，经济模型"
        elif complexity == "medium":
            return "flux-pro", "中等场景，平衡模型"
        else:
            return "imagen-4", "复杂场景，高质量模型"
    
    def select_video_model(self, scene: Dict, budget: str = "balanced") -> Tuple[str, str]:
        """根据场景和预算选择视频模型"""
        complexity = self._analyze_scene_complexity(scene)
        
        if budget == "budget":
            return "vidu2", "经济预算，VIDU v2"
        elif budget == "quality":
            return "kling-v2", "质量优先，Kling v2"
        else:
            # 平衡预算：简单场景用VIDU，复杂场景用Kling
            if complexity == "simple":
                return "vidu2", "简单场景，VIDU v2"
            else:
                return "kling-v2", "复杂场景，Kling v2"
    
    def _analyze_scene_complexity(self, scene: Dict) -> str:
        """分析场景复杂度"""
        score = 0
        
        # 人物数量
        characters = scene.get('characters', [])
        if len(characters) > 3:
            score += 2
        elif len(characters) > 1:
            score += 1
        
        # 场景描述关键词
        description = scene.get('description', '').lower()
        visual_prompt = scene.get('visual_prompt', '').lower()
        combined_text = f"{description} {visual_prompt}"
        
        # 特效
        if any(kw in combined_text for kw in ['特效', 'magic', 'effect', '粒子']):
            score += 2
        
        # 文字渲染
        if any(kw in combined_text for kw in ['文字', 'text', '标题', 'title']):
            score += 1.5
        
        # 室外场景
        if any(kw in combined_text for kw in ['室外', 'outdoor', '街道', 'street', '自然', 'nature']):
            score += 0.5
        
        # 复杂构图
        if any(kw in combined_text for kw in ['复杂', 'complex', '多角度', 'multiple angles']):
            score += 1
        
        # 判断复杂度等级
        if score >= 3:
            return "complex"
        elif score >= 1:
            return "medium"
        else:
            return "simple"
    
    def calculate_optimized_cost(self, scenes: List[Dict], budget: str = "balanced") -> Dict:
        """计算优化后的成本"""
        costs = {
            "text": 0,
            "image": 0,
            "video": 0,
            "audio": 0,
            "music": 0,
            "total": 0
        }
        
        for scene in scenes:
            # 文本（统一使用DeepSeek）
            costs["text"] += 0.00003
            
            # 图像（智能选择）
            image_model, _ = self.select_image_model(scene)
            costs["image"] += self.MODEL_COSTS[image_model]
            
            # 视频（智能选择）
            video_model, _ = self.select_video_model(scene, budget)
            costs["video"] += self.MODEL_COSTS[video_model]
            
            # 音频（统一使用Minimax）
            costs["audio"] += 0.10
            
            # 音乐（统一使用Suno Custom）
            costs["music"] += 0.10
        
        costs["total"] = sum(costs.values())
        return costs


class PromptOptimizer:
    """提示词优化器"""
    
    NEGATIVE_PROMPTS = {
        "人物": "deformed, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb, ugly, disgusting, poorly drawn hands, missing limb, floating limbs, disconnected limbs, malformed hands, blurry, out of focus",
        
        "场景": "blur, haze, low quality, pixelated, grainy, text, watermark, signature, logo, caption",
        
        "通用": "worst quality, low quality, normal quality, lowres, small, medium, large, cropped, text, error, logo, watermark, signature, jpeg artifacts",
        
        "视频": "static, slideshow, flickering, distortion, jittery, unnatural movement, morphing, glitches"
    }
    
    QUALITY_TAGS = {
        "low": "good quality, clear",
        "medium": "high quality, detailed, sharp",
        "high": "best quality, highly detailed, ultra detailed, 4K, 8K, sharp focus, masterpiece",
        "cinematic": "cinematic lighting, film grain, dramatic lighting, volumetric lighting, ray tracing"
    }
    
    STYLE_TAGS = {
        "photorealistic": "photorealistic, realistic, photograph, raw photo, DSLR",
        "anime": "anime style, manga style, cel shading, vibrant colors",
        "cinematic": "cinematic, movie scene, film look, widescreen, anamorphic",
        "artistic": "digital art, concept art, illustration, painting"
    }
    
    def optimize_image_prompt(
        self,
        scene: Dict,
        quality: str = "high",
        style: str = "cinematic"
    ) -> Tuple[str, str]:
        """优化图像提示词"""
        # 提取场景信息
        description = scene.get('description', '')
        characters = scene.get('characters', [])
        mood = scene.get('mood', 'neutral')
        
        # 构建优化后的提示词
        parts = []
        
        # 1. 主体描述
        if characters:
            char_desc = self._describe_characters(characters)
            parts.append(char_desc)
        
        # 2. 场景描述
        parts.append(description)
        
        # 3. 构图和镜头
        composition = self._suggest_composition(scene)
        parts.append(composition)
        
        # 4. 光影和氛围
        lighting = self._suggest_lighting(mood)
        parts.append(lighting)
        
        # 5. 风格和质量标签
        quality_tags = self.QUALITY_TAGS.get(quality, self.QUALITY_TAGS["medium"])
        style_tags = self.STYLE_TAGS.get(style, self.STYLE_TAGS["cinematic"])
        parts.append(f"{style_tags}, {quality_tags}")
        
        # 组合提示词
        positive_prompt = ", ".join(parts)
        
        # 负面提示词
        negative_prompt = ", ".join([
            self.NEGATIVE_PROMPTS["人物"],
            self.NEGATIVE_PROMPTS["场景"],
            self.NEGATIVE_PROMPTS["通用"]
        ])
        
        return positive_prompt, negative_prompt
    
    def optimize_video_prompt(
        self,
        scene: Dict,
        duration: float
    ) -> Tuple[str, str]:
        """优化视频提示词"""
        # 基于图像提示词
        positive, negative = self.optimize_image_prompt(scene)
        
        # 添加视频特定标签
        camera_movement = self._suggest_camera_movement(scene)
        motion_hint = self._suggest_motion(scene, duration)
        
        positive = f"{positive}, {camera_movement}, {motion_hint}"
        negative = f"{negative}, {self.NEGATIVE_PROMPTS['视频']}"
        
        return positive, negative
    
    def _describe_characters(self, characters: List[str]) -> str:
        """描述角色"""
        if not characters:
            return ""
        
        char_count = len(characters)
        if char_count == 1:
            return f"single person, {characters[0]}"
        elif char_count == 2:
            return f"two people, {', '.join(characters)}"
        else:
            return f"group of {char_count} people, {', '.join(characters)}"
    
    def _suggest_composition(self, scene: Dict) -> str:
        """建议构图"""
        description = scene.get('description', '').lower()
        
        if any(kw in description for kw in ['特写', 'close-up', '脸']):
            return "close-up shot, face focus"
        elif any(kw in description for kw in ['全身', 'full body']):
            return "full body shot, standing pose"
        elif any(kw in description for kw in ['远景', 'wide', '全景']):
            return "wide shot, establishing shot, environmental"
        else:
            return "medium shot, waist up, three quarter view"
    
    def _suggest_lighting(self, mood: str) -> str:
        """建议光影"""
        LIGHTING_MAP = {
            "romantic": "soft warm lighting, golden hour, romantic atmosphere",
            "tension": "dramatic lighting, high contrast, shadows",
            "happy": "bright natural lighting, sunny day, cheerful",
            "sad": "dim lighting, overcast, melancholic",
            "action": "dynamic lighting, motion blur, energetic",
            "neutral": "natural lighting, soft shadows, balanced"
        }
        
        return LIGHTING_MAP.get(mood, LIGHTING_MAP["neutral"])
    
    def _suggest_camera_movement(self, scene: Dict) -> str:
        """建议镜头运动"""
        description = scene.get('description', '').lower()
        
        if any(kw in description for kw in ['行走', 'walking', '移动']):
            return "tracking shot, smooth camera movement"
        elif any(kw in description for kw in ['静止', 'still', '站立']):
            return "static shot, steady camera"
        elif any(kw in description for kw in ['特写', 'close-up']):
            return "slow zoom in, gradual approach"
        else:
            return "gentle camera movement, subtle pan"
    
    def _suggest_motion(self, scene: Dict, duration: float) -> str:
        """建议运动"""
        if duration <= 4:
            return "subtle motion, minimal movement"
        elif duration <= 8:
            return "natural motion, smooth movement"
        else:
            return "dynamic motion, active movement"


class CharacterConsistency:
    """角色一致性管理器"""
    
    def __init__(self):
        self.characters: Dict[str, Dict] = {}
    
    def register_character(
        self,
        name: str,
        description: str,
        age: int = None,
        gender: str = None,
        features: List[str] = None
    ):
        """注册角色"""
        self.characters[name] = {
            "description": description,
            "age": age,
            "gender": gender,
            "features": features or [],
            "seed": random.randint(0, 2**32 - 1),
            "reference_images": []
        }
    
    def get_character_prompt(
        self,
        name: str,
        action: str = "",
        expression: str = ""
    ) -> str:
        """获取角色提示词"""
        if name not in self.characters:
            return ""
        
        char = self.characters[name]
        
        parts = [char["description"]]
        
        if action:
            parts.append(action)
        
        if expression:
            parts.append(expression)
        
        # 添加seed保持一致性
        parts.append(f"seed={char['seed']}")
        
        return ", ".join(parts)
    
    def add_reference_image(self, name: str, image_url: str):
        """添加参考图片"""
        if name in self.characters:
            self.characters[name]["reference_images"].append(image_url)


class BackgroundManager:
    """背景资源管理器"""
    
    def __init__(self):
        self.backgrounds: Dict[str, str] = {}
    
    def get_or_create(
        self,
        location: str,
        time_of_day: str = "day",
        weather: str = "clear"
    ) -> str:
        """获取或创建背景"""
        key = f"{location}_{time_of_day}_{weather}"
        
        if key not in self.backgrounds:
            # 生成新背景
            prompt = self._create_background_prompt(location, time_of_day, weather)
            # image_url = generate_background_image(prompt)
            # self.backgrounds[key] = image_url
            self.backgrounds[key] = f"placeholder_{key}"
        
        return self.backgrounds[key]
    
    def _create_background_prompt(
        self,
        location: str,
        time_of_day: str,
        weather: str
    ) -> str:
        """创建背景提示词"""
        TIME_MAP = {
            "dawn": "dawn, sunrise, golden hour, warm lighting",
            "morning": "morning, bright natural light, fresh atmosphere",
            "day": "daytime, sunlight, clear visibility",
            "afternoon": "afternoon, warm sunlight, soft shadows",
            "evening": "evening, sunset, golden hour",
            "night": "night, moonlight, artificial lighting"
        }
        
        WEATHER_MAP = {
            "clear": "clear sky, sunny",
            "cloudy": "cloudy sky, overcast",
            "rainy": "rain, wet surfaces, puddles",
            "snowy": "snow, winter atmosphere"
        }
        
        time_desc = TIME_MAP.get(time_of_day, TIME_MAP["day"])
        weather_desc = WEATHER_MAP.get(weather, WEATHER_MAP["clear"])
        
        return f"{location}, {time_desc}, {weather_desc}, no people, empty scene, wide angle"


class AssetCache:
    """资源缓存管理器"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, prompt: str, model: str, params: Dict) -> str:
        """生成缓存键"""
        data = {
            "prompt": prompt,
            "model": model,
            "params": params
        }
        return hashlib.md5(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
    
    def get(self, prompt: str, model: str, params: Dict) -> Optional[Dict]:
        """从缓存获取"""
        key = self.get_cache_key(prompt, model, params)
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        
        return None
    
    def set(self, prompt: str, model: str, params: Dict, result: Dict):
        """保存到缓存"""
        key = self.get_cache_key(prompt, model, params)
        cache_file = self.cache_dir / f"{key}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    def clear(self):
        """清空缓存"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir()


class CostOptimizer:
    """成本优化器"""
    
    def __init__(self):
        self.model_selector = SmartModelSelector()
        self.prompt_optimizer = PromptOptimizer()
        self.cache = AssetCache()
        self.character_manager = CharacterConsistency()
        self.background_manager = BackgroundManager()
    
    def optimize_scene(self, scene: Dict, budget: str = "balanced") -> Dict:
        """优化单个场景"""
        # 1. 优化提示词
        image_prompt, negative = self.prompt_optimizer.optimize_image_prompt(
            scene,
            quality="high" if budget == "quality" else "medium"
        )
        
        video_prompt, video_negative = self.prompt_optimizer.optimize_video_prompt(
            scene,
            duration=10
        )
        
        # 2. 智能选择模型
        image_model, image_reason = self.model_selector.select_image_model(scene)
        video_model, video_reason = self.model_selector.select_video_model(scene, budget)
        
        # 3. 返回优化结果
        return {
            "scene_id": scene.get('scene_number', 0),
            "prompts": {
                "image": {
                    "positive": image_prompt,
                    "negative": negative
                },
                "video": {
                    "positive": video_prompt,
                    "negative": video_negative
                }
            },
            "models": {
                "image": image_model,
                "video": video_model
            },
            "reasons": {
                "image": image_reason,
                "video": video_reason
            }
        }
    
    def calculate_savings(
        self,
        scenes: List[Dict],
        strategy: str = "balanced"
    ) -> Dict:
        """计算节省的成本"""
        # 原始成本（全部使用中端模型）
        original_cost = len(scenes) * 0.53
        
        # 优化后成本
        optimized_cost = self.model_selector.calculate_optimized_cost(
            scenes,
            budget=strategy
        )
        
        savings = original_cost - optimized_cost["total"]
        savings_percent = (savings / original_cost) * 100
        
        return {
            "original_cost": original_cost,
            "optimized_cost": optimized_cost,
            "savings": savings,
            "savings_percent": savings_percent,
            "strategy": strategy
        }


# 使用示例
if __name__ == "__main__":
    # 示例场景
    sample_scene = {
        "scene_number": 1,
        "title": "春日相遇",
        "description": "林晓薇在街上差点被车撞，被陆晨轩救下",
        "characters": ["林晓薇", "陆晨轩"],
        "mood": "romantic",
        "dialogue": "(breath) 小心！你没事吧？"
    }
    
    # 使用优化器
    optimizer = CostOptimizer()
    
    # 优化场景
    optimized = optimizer.optimize_scene(sample_scene, budget="balanced")
    
    print("优化结果:")
    print(json.dumps(optimized, indent=2, ensure_ascii=False))
    
    # 计算节省
    scenes = [sample_scene] * 10
    savings = optimizer.calculate_savings(scenes, strategy="balanced")
    
    print("\n成本节省:")
    print(json.dumps(savings, indent=2, ensure_ascii=False))
