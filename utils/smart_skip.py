"""
智能跳过模块

功能：
1. 根据场景特征判断是否需要生成
2. 支持多种跳过规则
3. 可配置的跳过策略

使用方法:
    from utils.smart_skip import SmartSkipper
    
    skipper = SmartSkipper()
    should_gen, reason = skipper.should_generate_image(scene)
"""

import logging
from typing import Dict, Tuple, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SkipRule:
    """跳过规则"""
    field: str
    condition: str
    value: Any
    reason: str


class SmartSkipper:
    """
    智能跳过器
    
    根据场景特征判断是否需要生成内容
    
    Examples:
        >>> skipper = SmartSkipper()
        >>> 
        >>> # 检查是否需要生成图像
        >>> should_gen, reason = skipper.should_generate_image(scene)
        >>> 
        >>> if should_gen:
        ...     generate_image(scene)
        ... else:
        ...     logger.info(f"跳过: {reason}")
    """
    
    # 图像生成跳过规则
    # 传入数据: {scene_number, visual_prompt, image_url, scene_type, skip_image}
    IMAGE_SKIP_RULES = [
        SkipRule("image_url", "exists", True, "已有图像"),
        SkipRule("visual_prompt", "empty", True, "无视觉提示词"),
        SkipRule("scene_type", "equals", "dialogue_only", "纯对话场景"),
        SkipRule("skip_image", "equals", True, "标记跳过图像生成"),
    ]
    
    # 视频生成跳过规则
    # 传入数据: {scene_number, image_url, video_url, scene_type, skip_video}
    VIDEO_SKIP_RULES = [
        SkipRule("video_url", "exists", True, "已有视频"),
        SkipRule("image_url", "empty", True, "缺少图像（视频依赖图像）"),
        SkipRule("scene_type", "equals", "static", "静态场景（无需视频）"),
        SkipRule("skip_video", "equals", True, "标记跳过视频生成"),
    ]
    
    # 音频生成跳过规则
    # 传入数据: {scene_number, dialogue, audio_url, scene_type, skip_audio}
    AUDIO_SKIP_RULES = [
        SkipRule("audio_url", "exists", True, "已有音频"),
        SkipRule("dialogue", "empty", True, "无对话内容"),
        SkipRule("scene_type", "equals", "narration", "旁白场景（使用字幕）"),
        SkipRule("skip_audio", "equals", True, "标记跳过音频生成"),
    ]
    
    # 音乐生成跳过规则
    # 传入数据: {scene_number, mood, music_url, scene_type, use_stock_music, skip_music}
    MUSIC_SKIP_RULES = [
        SkipRule("music_url", "exists", True, "已有音乐"),
        SkipRule("scene_type", "equals", "silent", "静音场景"),
        SkipRule("use_stock_music", "equals", True, "使用通用音乐"),
        SkipRule("skip_music", "equals", True, "标记跳过音乐生成"),
    ]
    
    def __init__(self, custom_rules: Optional[Dict[str, List[SkipRule]]] = None):
        """
        初始化
        
        Args:
            custom_rules: 自定义规则 {"image": [...], "video": [...]}
        """
        self.rules = {
            "image": self.IMAGE_SKIP_RULES.copy(),
            "video": self.VIDEO_SKIP_RULES.copy(),
            "audio": self.AUDIO_SKIP_RULES.copy(),
            "music": self.MUSIC_SKIP_RULES.copy(),
        }
        
        # 添加自定义规则
        if custom_rules:
            for content_type, rules in custom_rules.items():
                if content_type in self.rules:
                    self.rules[content_type].extend(rules)
        
        # 统计
        self.stats = {
            "total_checked": 0,
            "total_skipped": 0,
            "skipped_by_type": {
                "image": 0,
                "video": 0,
                "audio": 0,
                "music": 0
            },
            "skip_reasons": {}
        }
    
    def should_generate_image(self, scene: Dict) -> Tuple[bool, str]:
        """
        判断是否需要生成图像
        
        Args:
            scene: 场景数据
        
        Returns:
            (是否需要生成, 原因)
        """
        return self._check_rules(scene, "image")
    
    def should_generate_video(self, scene: Dict) -> Tuple[bool, str]:
        """
        判断是否需要生成视频
        
        Args:
            scene: 场景数据
        
        Returns:
            (是否需要生成, 原因)
        """
        return self._check_rules(scene, "video")
    
    def should_generate_audio(self, scene: Dict) -> Tuple[bool, str]:
        """
        判断是否需要生成音频
        
        Args:
            scene: 场景数据
        
        Returns:
            (是否需要生成, 原因)
        """
        return self._check_rules(scene, "audio")
    
    def should_generate_music(self, scene: Dict) -> Tuple[bool, str]:
        """
        判断是否需要生成音乐
        
        Args:
            scene: 场景数据
        
        Returns:
            (是否需要生成, 原因)
        """
        return self._check_rules(scene, "music")
    
    def _check_rules(self, scene: Dict, content_type: str) -> Tuple[bool, str]:
        """
        检查跳过规则
        
        Args:
            scene: 场景数据
            content_type: 内容类型
        
        Returns:
            (是否需要生成, 原因)
        """
        self.stats["total_checked"] += 1
        
        rules = self.rules.get(content_type, [])
        
        for rule in rules:
            # 检查条件
            if self._evaluate_rule(scene, rule):
                # 记录统计
                self.stats["total_skipped"] += 1
                self.stats["skipped_by_type"][content_type] += 1
                
                reason_key = f"{content_type}:{rule.reason}"
                self.stats["skip_reasons"][reason_key] = \
                    self.stats["skip_reasons"].get(reason_key, 0) + 1
                
                logger.debug(f"跳过{content_type}生成: {rule.reason}")
                return False, rule.reason
        
        return True, "需要生成"
    
    def _evaluate_rule(self, scene: Dict, rule: SkipRule) -> bool:
        """
        评估规则
        
        Args:
            scene: 场景数据
            rule: 跳过规则
        
        Returns:
            是否满足跳过条件
        """
        field_value = scene.get(rule.field)
        
        if rule.condition == "exists":
            # 字段存在且非空
            return bool(field_value) == rule.value
        
        elif rule.condition == "empty":
            # 字段为空
            is_empty = not field_value or (
                isinstance(field_value, str) and not field_value.strip()
            )
            return is_empty == rule.value
        
        elif rule.condition == "equals":
            # 字段等于某值
            return field_value == rule.value
        
        elif rule.condition == "in":
            # 字段在列表中
            return field_value in rule.value
        
        elif rule.condition == "not_in":
            # 字段不在列表中
            return field_value not in rule.value
        
        elif rule.condition == "contains":
            # 字段包含某值
            return rule.value in str(field_value)
        
        elif rule.condition == "greater_than":
            # 字段大于某值
            try:
                return float(field_value) > rule.value
            except (TypeError, ValueError):
                return False
        
        elif rule.condition == "less_than":
            # 字段小于某值
            try:
                return float(field_value) < rule.value
            except (TypeError, ValueError):
                return False
        
        return False
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "skip_rate": (
                self.stats["total_skipped"] / max(self.stats["total_checked"], 1)
            )
        }
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            "total_checked": 0,
            "total_skipped": 0,
            "skipped_by_type": {
                "image": 0,
                "video": 0,
                "audio": 0,
                "music": 0
            },
            "skip_reasons": {}
        }


class SceneAnalyzer:
    """
    场景分析器
    
    分析场景特征，辅助跳过决策
    """
    
    @staticmethod
    def analyze_scene_type(scene: Dict) -> str:
        """
        分析场景类型
        
        Args:
            scene: 场景数据
        
        Returns:
            场景类型
        """
        # 已明确指定类型
        if scene.get("scene_type"):
            return scene["scene_type"]
        
        # 根据特征推断
        description = scene.get("description", "").lower()
        dialogue = scene.get("dialogue", "")
        
        # 纯对话场景
        if dialogue and not scene.get("visual_prompt"):
            return "dialogue_only"
        
        # 静态场景
        static_keywords = ["特写", "静止", "肖像", "portrait", "still", "close-up"]
        if any(kw in description for kw in static_keywords):
            return "static"
        
        # 转场场景
        if "转场" in description or "transition" in description:
            return "transition"
        
        # 旁白场景
        if scene.get("narrator") or "旁白" in dialogue:
            return "narration"
        
        # 默认：动态场景
        return "dynamic"
    
    @staticmethod
    def estimate_complexity(scene: Dict) -> str:
        """
        估计场景复杂度
        
        Args:
            scene: 场景数据
        
        Returns:
            复杂度: simple/medium/complex
        """
        complexity_score = 0
        
        # 角色数量
        characters = scene.get("characters", [])
        if len(characters) > 3:
            complexity_score += 2
        elif len(characters) > 1:
            complexity_score += 1
        
        # 描述长度
        description = scene.get("description", "")
        if len(description) > 200:
            complexity_score += 1
        
        # 特效关键词
        effect_keywords = ["特效", "魔法", "爆炸", "effect", "magic", "explosion"]
        if any(kw in description.lower() for kw in effect_keywords):
            complexity_score += 2
        
        # 判断
        if complexity_score >= 3:
            return "complex"
        elif complexity_score >= 1:
            return "medium"
        else:
            return "simple"
    
    @staticmethod
    def get_dependencies(scene: Dict) -> Dict[str, List[str]]:
        """
        获取场景依赖关系
        
        Args:
            scene: 场景数据
        
        Returns:
            {"video": ["image"], "audio": ["dialogue"], ...}
        """
        dependencies = {}
        
        # 视频依赖图像
        if scene.get("visual_prompt"):
            dependencies["video"] = ["image"]
        
        # 音频依赖对话
        if scene.get("dialogue"):
            dependencies["audio"] = []
        
        # 音乐依赖场景情绪
        if scene.get("mood"):
            dependencies["music"] = []
        
        return dependencies


# 便捷函数
def create_skipper(custom_rules: Optional[Dict] = None) -> SmartSkipper:
    """创建智能跳过器"""
    return SmartSkipper(custom_rules)


if __name__ == "__main__":
    # 测试
    skipper = SmartSkipper()
    
    # 测试场景
    test_scene = {
        "scene_number": 1,
        "title": "测试场景",
        "description": "一个简单的测试场景",
        "visual_prompt": "A simple test scene",
        "dialogue": "Hello, this is a test.",
        "characters": ["角色A"],
        "mood": "neutral"
    }
    
    print("图像:", skipper.should_generate_image(test_scene))
    print("视频:", skipper.should_generate_video(test_scene))
    print("音频:", skipper.should_generate_audio(test_scene))
    print("音乐:", skipper.should_generate_music(test_scene))
    print("\n统计:", skipper.get_stats())
