"""
Configuration nodes for ComfyUI-UnlimitAI.
Allows users to customize model selection and parameters.
"""
import logging
logger = logging.getLogger(__name__)

import json
from typing import Dict, Any, List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DramaConfigNode:
    """
    Configuration node for drama workflow.
    Allows users to select models and parameters in one place.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "num_scenes": ("INT", {"default": 10, "min": 1, "max": 50}),
                "drama_title": ("STRING", {"default": "我的漫剧作品", "multiline": False}),
            },
            "optional": {
                "text_model": (["deepseek-chat", "gpt-4o", "claude-3-5-sonnet-20241022"], {"default": "deepseek-chat"}),
                "target_language": (["english", "chinese"], {"default": "english"}),
                "art_style": (["cinematic", "anime", "realistic", "artistic"], {"default": "cinematic"}),
                "image_model": (["flux-pro", "ideogram-v3", "kling-v2", "dall-e-3"], {"default": "flux-pro"}),
                "image_aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "video_model": (["kling-v2", "veo-3.1", "vidu2", "hailuo", "luma"], {"default": "kling-v2"}),
                "video_duration": (["5", "10"], {"default": "5"}),
                "video_aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "voice_id": ([
                    "male-qn-qingse",
                    "male-qn-jingying",
                    "female-shaonv",
                    "female-yujie",
                    "presenter_male",
                    "presenter_female"
                ], {"default": "male-qn-jingying"}),
                "generate_music": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "api_key",
        "config_json",
        "text_config",
        "image_config", 
        "video_config",
        "audio_config",
        "num_scenes_str",
        "drama_title"
    )
    FUNCTION = "configure"
    CATEGORY = "UnlimitAI/Config"
    
    def configure(
        self,
        api_key: str,
        num_scenes: int,
        drama_title: str,
        text_model: str = "deepseek-chat",
        target_language: str = "english",
        art_style: str = "cinematic",
        image_model: str = "flux-pro",
        image_aspect_ratio: str = "16:9",
        video_model: str = "kling-v2",
        video_duration: str = "5",
        video_aspect_ratio: str = "16:9",
        voice_id: str = "male-qn-jingying",
        generate_music: bool = True
    ) -> Tuple[str, str, str, str, str, str, str, str]:
        """
        Generate configuration for all nodes.
        """
        config = {
            "api_key": api_key,
            "num_scenes": num_scenes,
            "drama_title": drama_title,
            "text": {
                "model": text_model,
                "target_language": target_language,
                "art_style": art_style
            },
            "image": {
                "model": image_model,
                "aspect_ratio": image_aspect_ratio
            },
            "video": {
                "model": video_model,
                "duration": video_duration,
                "aspect_ratio": video_aspect_ratio
            },
            "audio": {
                "voice_id": voice_id,
                "generate_music": generate_music
            }
        }
        
        config_json = json.dumps(config, ensure_ascii=False, indent=2)
        
        text_config = json.dumps(config["text"], ensure_ascii=False)
        image_config = json.dumps(config["image"], ensure_ascii=False)
        video_config = json.dumps(config["video"], ensure_ascii=False)
        audio_config = json.dumps(config["audio"], ensure_ascii=False)
        
        return (
            api_key,
            config_json,
            text_config,
            image_config,
            video_config,
            audio_config,
            str(num_scenes),
            drama_title
        )


class ModelComparisonNode:
    """
    Compare different models based on quality, cost, and speed.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_type": (["text", "image", "video", "audio"], {"default": "video"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("comparison_table",)
    FUNCTION = "compare"
    CATEGORY = "UnlimitAI/Config"
    
    def compare(self, model_type: str) -> Tuple[str]:
        """
        Generate model comparison table.
        """
        comparisons = {
            "video": """
视频模型对比：

| 模型 | 质量评分 | 成本/视频 | 速度 | 功能 | 推荐场景 |
|------|---------|----------|------|------|---------|
| VEO 3.1 | ⭐⭐⭐⭐⭐ | $0.50 | 中 | 4K+音频 | 商业项目 |
| Kling v2 | ⭐⭐⭐⭐ | $0.30 | 快 | 全功能 | **漫剧推荐** |
| Hailuo-2.3 | ⭐⭐⭐⭐ | $0.35 | 快 | 导演模式 | 创意视频 |
| VIDU v2 | ⭐⭐⭐ | $0.25 | 很快 | 标准 | 快速预览 |
| Luma | ⭐⭐⭐ | $0.30 | 快 | 创意 | 风格化 |

推荐：Kling v2（性价比最高，功能最全）
""",
            "image": """
图像模型对比：

| 模型 | 质量评分 | 成本/张 | 速度 | 特点 | 推荐场景 |
|------|---------|---------|------|------|---------|
| FLUX Pro | ⭐⭐⭐⭐⭐ | $0.03 | 快 | 同步生成 | **通用推荐** |
| Ideogram V3 | ⭐⭐⭐⭐⭐ | $0.05 | 快 | 文字渲染 | 含文字场景 |
| Kling v2 | ⭐⭐⭐⭐ | $0.02 | 中 | 中文优化 | 中国风格 |
| DALL-E 3 | ⭐⭐⭐⭐ | $0.08 | 快 | OpenAI | 创意场景 |
| Imagen 4 | ⭐⭐⭐⭐⭐ | $0.04 | 中 | Google | 写实场景 |
| Recraft V3 | ⭐⭐⭐⭐ | $0.03 | 快 | 矢量输出 | 设计用途 |

推荐：FLUX Pro（质量高、速度快、成本低）
""",
            "text": """
文本模型对比：

| 模型 | 质量评分 | 成本/1K tokens | 推理 | 推荐场景 |
|------|---------|---------------|------|---------|
| GPT-4o | ⭐⭐⭐⭐⭐ | $0.0025/$0.01 | 标准 | 高质量需求 |
| GPT-5 | ⭐⭐⭐⭐⭐ | $0.03/$0.06 | 推理 | 复杂分析 |
| Claude 3.5 | ⭐⭐⭐⭐⭐ | $0.003/$0.015 | 标准 | 文学创作 |
| DeepSeek Chat | ⭐⭐⭐⭐ | $0.00014/$0.00028 | 标准 | **经济推荐** |
| DeepSeek Reasoner | ⭐⭐⭐⭐⭐ | $0.00055/$0.00219 | 推理 | 深度分析 |

推荐：DeepSeek Chat（性价比最高）
""",
            "audio": """
音频模型对比：

| 模型 | 质量评分 | 特点 | 语言 | 推荐场景 |
|------|---------|------|------|---------|
| Minimax TTS | ⭐⭐⭐⭐⭐ | 中文最佳、情感标签 | 中文 | **漫剧推荐** |
| OpenAI TTS | ⭐⭐⭐⭐ | 英文优秀 | 英文 | 英文场景 |
| Kling TTS | ⭐⭐⭐⭐ | 中文优化 | 中文 | 备选 |

音色选择：
- male-qn-jingying: 精英青年男声（推荐）
- male-qn-qingse: 青涩青年男声
- female-shaonv: 少女女声
- female-yujie: 御姐女声

推荐：Minimax TTS + male-qn-jingying
"""
        }
        
        result = comparisons.get(model_type, "未找到该类型的对比信息")
        return (result,)


class CostEstimatorNode:
    """
    Estimate cost for drama generation based on configuration.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "num_scenes": ("INT", {"default": 10, "min": 1, "max": 100}),
            },
            "optional": {
                "text_model": (["deepseek-chat", "gpt-4o", "claude-3-5-sonnet-20241022"], {"default": "deepseek-chat"}),
                "image_model": (["flux-pro", "ideogram-v3", "kling-v2", "dall-e-3"], {"default": "flux-pro"}),
                "video_model": (["kling-v2", "veo-3.1", "vidu2", "hailuo"], {"default": "kling-v2"}),
                "video_duration": (["5", "10"], {"default": "5"}),
                "generate_music": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("cost_breakdown", "total_cost", "recommendation")
    FUNCTION = "estimate"
    CATEGORY = "UnlimitAI/Config"
    
    def estimate(
        self,
        num_scenes: int,
        text_model: str = "deepseek-chat",
        image_model: str = "flux-pro",
        video_model: str = "kling-v2",
        video_duration: str = "5",
        generate_music: bool = True
    ) -> Tuple[str, float, str]:
        """
        Estimate total cost for drama generation.
        """
        # 文本成本（假设平均 10K 输入 + 5K 输出）
        text_pricing = {
            "deepseek-chat": {"input": 0.00014, "output": 0.00028},
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015}
        }
        text_cost = (10 * text_pricing[text_model]["input"] + 
                    5 * text_pricing[text_model]["output"])
        
        # 图像成本
        image_pricing = {
            "flux-pro": 0.03,
            "ideogram-v3": 0.05,
            "kling-v2": 0.02,
            "dall-e-3": 0.08
        }
        image_cost = image_pricing[image_model] * num_scenes
        
        # 视频成本
        video_pricing = {
            "kling-v2": 0.30 if video_duration == "5" else 0.50,
            "veo-3.1": 0.50 if video_duration == "5" else 0.80,
            "vidu2": 0.25,
            "hailuo": 0.35
        }
        video_cost = video_pricing[video_model] * num_scenes
        
        # 音频成本
        audio_cost = 0.01 * num_scenes  # Minimax TTS
        
        # 音乐成本
        music_cost = 0.10 * num_scenes if generate_music else 0
        
        # 总成本
        total = text_cost + image_cost + video_cost + audio_cost + music_cost
        
        # 成本分解
        breakdown = f"""
成本估算（{num_scenes} 场景）：

文本处理 ({text_model}):
  - 小说分析: ${text_cost:.4f}

图像生成 ({image_model}):
  - {num_scenes} 张: ${image_cost:.2f}

视频生成 ({video_model}, {video_duration}秒):
  - {num_scenes} 个: ${video_cost:.2f}

音频生成 (Minimax TTS):
  - {num_scenes} 个对话: ${audio_cost:.2f}

背景音乐 (Suno):
  - {num_scenes if generate_music else 0} 首: ${music_cost:.2f}

━━━━━━━━━━━━━━━━━━━━
总成本: ${total:.2f}
平均每场景: ${total/num_scenes:.2f}
"""
        
        # 推荐
        if total / num_scenes < 0.40:
            recommendation = "经济配置 - 成本低，适合测试和预览"
        elif total / num_scenes < 0.50:
            recommendation = "标准配置 - 推荐使用，性价比最高"
        else:
            recommendation = "高质量配置 - 成本较高，适合专业制作"
        
        return (breakdown, round(total, 2), recommendation)


NODE_CLASS_MAPPINGS = {
    "DramaConfigNode": DramaConfigNode,
    "ModelComparisonNode": ModelComparisonNode,
    "CostEstimatorNode": CostEstimatorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DramaConfigNode": "Drama Configuration (统一配置)",
    "ModelComparisonNode": "Model Comparison (模型对比)",
    "CostEstimatorNode": "Cost Estimator (成本估算)",
}
