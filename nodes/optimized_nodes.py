"""
Optimized workflow nodes for ComfyUI-UnlimitAI.
These nodes support input connections for api_key.
"""
import logging
logger = logging.getLogger(__name__)

import json
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..utils.helpers import make_request, poll_status, estimate_cost


class OptimizedNovelAnalyzerNode:
    """
    Optimized novel analyzer with api_key input support.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_text": ("STRING", {"default": "", "multiline": True}),
                "num_scenes": ("INT", {"default": 10, "min": 1, "max": 50}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "multiline": False, "forceInput": True}),
                "model": (["deepseek-chat", "gpt-4o", "claude-3-5-sonnet-20241022"], {"default": "deepseek-chat"}),
                "target_language": (["english", "chinese"], {"default": "english"}),
                "art_style": (["cinematic", "anime", "realistic", "artistic"], {"default": "cinematic"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("scenes_json", "summary", "total_cost")
    FUNCTION = "analyze"
    CATEGORY = "UnlimitAI/Workflow/Optimized"
    
    def analyze(
        self,
        novel_text: str,
        num_scenes: int,
        api_key: str = "",
        model: str = "deepseek-chat",
        target_language: str = "english",
        art_style: str = "cinematic"
    ) -> Tuple[str, str, str]:
        """
        Analyze novel and extract scenes.
        """
        lang_instruction = "使用中文" if target_language == "chinese" else "Use English"
        
        prompt = f"""{lang_instruction}分析以下小说文本，提取{num_scenes}个关键场景用于制作漫剧视频。

对于每个场景，提供以下信息：
1. scene_number: 场景编号
2. title: 场景标题
3. description: 场景描述（包含人物、动作、环境、情感）
4. characters: 出场人物列表
5. mood: 场景氛围（emotional/suspenseful/romantic/action/peaceful/dramatic/melancholic/upbeat/tense）
6. dialogue: 关键对话或内心独白（用于配音，包含情感标签如 (laughs), (sighs)）
7. visual_prompt: 用于生成图像的详细英文提示词，{art_style} style
8. camera_movement: 建议的镜头运动

小说文本：
{novel_text}

请以JSON数组格式返回场景列表。"""
        
        schema = {
            "type": "object",
            "properties": {
                "scenes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "scene_number": {"type": "integer"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "characters": {"type": "array", "items": {"type": "string"}},
                            "mood": {"type": "string"},
                            "dialogue": {"type": "string"},
                            "visual_prompt": {"type": "string"},
                            "camera_movement": {"type": "string"}
                        }
                    }
                },
                "summary": {"type": "string"}
            }
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "novel_scenes",
                    "schema": schema
                }
            }
        }
        
        response = make_request("/v1/chat/completions", api_key, payload)
        
        text = response["choices"][0]["message"]["content"]
        data = json.loads(text)
        
        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        cost = estimate_cost(model, input_tokens, output_tokens)
        
        summary = data.get("summary", "")
        
        return (text, summary, f"${cost:.6f}")


class OptimizedImageGeneratorNode:
    """
    Optimized image generator with api_key input support.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scenes_json": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "multiline": False, "forceInput": True}),
                "image_model": (["flux-pro", "ideogram-v3", "kling-v2", "dall-e-3"], {"default": "flux-pro"}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "max_scenes": ("INT", {"default": 10, "min": 1, "max": 50}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("images_json", "summary")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Workflow/Optimized"
    
    def generate(
        self,
        scenes_json: str,
        api_key: str = "",
        image_model: str = "flux-pro",
        aspect_ratio: str = "16:9",
        max_scenes: int = 10
    ) -> Tuple[str, str]:
        """Generate images for all scenes."""
        from .workflow_nodes import SceneImageGeneratorNode
        
        node = SceneImageGeneratorNode()
        return node.generate(
            api_key=api_key,
            scenes_json=scenes_json,
            image_model=image_model,
            aspect_ratio=aspect_ratio,
            max_scenes=max_scenes
        )


class OptimizedVideoGeneratorNode:
    """
    Optimized video generator with api_key input support.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_json": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "multiline": False, "forceInput": True}),
                "video_model": (["kling-v2", "veo-3.1", "vidu2", "hailuo"], {"default": "kling-v2"}),
                "duration": (["5", "10"], {"default": "5"}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("videos_json", "summary")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Workflow/Optimized"
    
    def generate(
        self,
        images_json: str,
        api_key: str = "",
        video_model: str = "kling-v2",
        duration: str = "5",
        aspect_ratio: str = "16:9"
    ) -> Tuple[str, str]:
        """Generate videos for all scenes."""
        from .workflow_nodes import SceneVideoGeneratorNode
        
        node = SceneVideoGeneratorNode()
        return node.generate(
            api_key=api_key,
            images_json=images_json,
            video_model=video_model,
            duration=duration,
            aspect_ratio=aspect_ratio
        )


class OptimizedAudioGeneratorNode:
    """
    Optimized audio generator with api_key input support.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scenes_json": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "multiline": False, "forceInput": True}),
                "voice_id": ("STRING", {"default": "male-qn-jingying", "multiline": False}),
                "generate_music": ("BOOLEAN", {"default": True}),
                "max_scenes": ("INT", {"default": 10, "min": 1, "max": 50}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("audio_json", "summary")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Workflow/Optimized"
    
    def generate(
        self,
        scenes_json: str,
        api_key: str = "",
        voice_id: str = "male-qn-jingying",
        generate_music: bool = True,
        max_scenes: int = 10
    ) -> Tuple[str, str]:
        """Generate audio for all scenes."""
        from .workflow_nodes import SceneAudioGeneratorNode
        
        node = SceneAudioGeneratorNode()
        return node.generate(
            api_key=api_key,
            scenes_json=scenes_json,
            voice_id=voice_id,
            generate_music=generate_music,
            max_scenes=max_scenes
        )


NODE_CLASS_MAPPINGS = {
    "OptimizedNovelAnalyzerNode": OptimizedNovelAnalyzerNode,
    "OptimizedImageGeneratorNode": OptimizedImageGeneratorNode,
    "OptimizedVideoGeneratorNode": OptimizedVideoGeneratorNode,
    "OptimizedAudioGeneratorNode": OptimizedAudioGeneratorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OptimizedNovelAnalyzerNode": "Optimized Novel Analyzer",
    "OptimizedImageGeneratorNode": "Optimized Image Generator",
    "OptimizedVideoGeneratorNode": "Optimized Video Generator",
    "OptimizedAudioGeneratorNode": "Optimized Audio Generator",
}
