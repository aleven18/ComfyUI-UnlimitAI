"""
Text processing nodes for ComfyUI-UnlimitAI.
Includes OpenAI, Claude, and DeepSeek nodes.
"""
import logging
logger = logging.getLogger(__name__)

import json
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..utils.helpers import make_request, estimate_cost


class UnlimitAITextNode:
    """
    Base class for text processing nodes.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "model": (cls.get_model_choices(), {"default": cls.get_default_model()}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "system_prompt": ("STRING", {"default": "", "multiline": True}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 4096, "min": 1, "max": 128000}),
                "top_p": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "INT", "FLOAT")
    RETURN_NAMES = ("response", "input_tokens", "output_tokens", "cost")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Text"
    
    @staticmethod
    def get_model_choices() -> List[str]:
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "deepseek-chat",
            "deepseek-reasoner"
        ]
    
    @staticmethod
    def get_default_model() -> str:
        return "gpt-4o"
    
    def generate(
        self,
        api_key: str,
        model: str,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        top_p: float = 1.0
    ) -> Tuple[str, int, int, float]:
        """
        Generate text completion.
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }
        
        response = make_request("/v1/chat/completions", api_key, payload)
        
        text = response["choices"][0]["message"]["content"]
        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        cost = estimate_cost(model, input_tokens, output_tokens)
        
        return (text, input_tokens, output_tokens, cost)


class GPT5ReasoningNode:
    """
    GPT-5 reasoning node for complex analysis tasks.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "system_prompt": ("STRING", {"default": "You are a helpful assistant.", "multiline": True}),
                "reasoning_effort": (["low", "medium", "high"], {"default": "medium"}),
                "max_tokens": ("INT", {"default": 16384, "min": 1, "max": 128000}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "FLOAT")
    RETURN_NAMES = ("response", "reasoning", "input_tokens", "output_tokens", "cost")
    FUNCTION = "reason"
    CATEGORY = "UnlimitAI/Text"
    
    def reason(
        self,
        api_key: str,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        reasoning_effort: str = "medium",
        max_tokens: int = 16384
    ) -> Tuple[str, str, int, int, float]:
        """
        Generate reasoned response with GPT-5.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        payload = {
            "model": "gpt-5",
            "messages": messages,
            "reasoning_effort": reasoning_effort,
            "max_tokens": max_tokens
        }
        
        response = make_request("/v1/chat/completions", api_key, payload)
        
        message = response["choices"][0]["message"]
        text = message["content"]
        reasoning = message.get("reasoning_content", "")
        
        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        cost = estimate_cost("gpt-5", input_tokens, output_tokens)
        
        return (text, reasoning, input_tokens, output_tokens, cost)


class DeepSeekThinkingNode:
    """
    DeepSeek thinking node for cost-effective reasoning.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "system_prompt": ("STRING", {"default": "", "multiline": True}),
                "max_tokens": ("INT", {"default": 8192, "min": 1, "max": 128000}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "FLOAT")
    RETURN_NAMES = ("response", "thinking", "input_tokens", "output_tokens", "cost")
    FUNCTION = "think"
    CATEGORY = "UnlimitAI/Text"
    
    def think(
        self,
        api_key: str,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 8192
    ) -> Tuple[str, str, int, int, float]:
        """
        Generate thinking response with DeepSeek.
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "deepseek-reasoner",
            "messages": messages,
            "max_tokens": max_tokens
        }
        
        response = make_request("/v1/chat/completions", api_key, payload)
        
        message = response["choices"][0]["message"]
        text = message["content"]
        thinking = message.get("reasoning_content", "")
        
        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        cost = estimate_cost("deepseek-reasoner", input_tokens, output_tokens)
        
        return (text, thinking, input_tokens, output_tokens, cost)


class StructuredOutputNode:
    """
    Structured output node for JSON schema validation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "json_schema": ("STRING", {"default": "{}", "multiline": True}),
            },
            "optional": {
                "model": (["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "claude-3-5-sonnet-20241022"], {"default": "gpt-4o"}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            }
        }
    
    RETURN_TYPES = ("STRING", "DICT", "INT", "INT", "FLOAT")
    RETURN_NAMES = ("json_string", "json_dict", "input_tokens", "output_tokens", "cost")
    FUNCTION = "generate_structured"
    CATEGORY = "UnlimitAI/Text"
    
    def generate_structured(
        self,
        api_key: str,
        prompt: str,
        json_schema: str,
        model: str = "gpt-4o",
        temperature: float = 0.7
    ) -> Tuple[str, Dict, int, int, float]:
        """
        Generate structured JSON output.
        """
        schema = json.loads(json_schema)
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "structured_output",
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
        
        return (text, data, input_tokens, output_tokens, cost)


class NovelAnalyzerNode:
    """
    Specialized node for analyzing Chinese novels and extracting scenes.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "novel_text": ("STRING", {"default": "", "multiline": True}),
                "num_scenes": ("INT", {"default": 10, "min": 1, "max": 100}),
            },
            "optional": {
                "model": (["deepseek-chat", "gpt-4o", "claude-3-5-sonnet-20241022"], {"default": "deepseek-chat"}),
                "language": (["chinese", "english"], {"default": "chinese"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "FLOAT")
    RETURN_NAMES = ("scenes_json", "scenes_summary", "input_tokens", "output_tokens", "cost")
    FUNCTION = "analyze"
    CATEGORY = "UnlimitAI/Text/Novel"
    
    def analyze(
        self,
        api_key: str,
        novel_text: str,
        num_scenes: int,
        model: str = "deepseek-chat",
        language: str = "chinese"
    ) -> Tuple[str, str, int, int, float]:
        """
        Analyze novel and extract scenes.
        """
        lang_instruction = "使用中文" if language == "chinese" else "Use English"
        
        prompt = f"""{lang_instruction}分析以下小说文本，提取{num_scenes}个关键场景。

对于每个场景，提供以下信息：
1. scene_number: 场景编号
2. title: 场景标题
3. description: 场景描述（包含人物、动作、环境、情感）
4. characters: 出场人物列表
5. mood: 场景氛围（如紧张、温馨、悲伤等）
6. dialogue: 关键对话或内心独白（用于配音）
7. visual_prompt: 用于生成图像的英文提示词
8. camera_movement: 建议的镜头运动（如slow zoom, pan left, close-up等）

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
                            "characters": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "mood": {"type": "string"},
                            "dialogue": {"type": "string"},
                            "visual_prompt": {"type": "string"},
                            "camera_movement": {"type": "string"}
                        },
                        "required": ["scene_number", "title", "description", "characters", "mood", "dialogue", "visual_prompt", "camera_movement"]
                    }
                },
                "summary": {"type": "string"}
            },
            "required": ["scenes", "summary"]
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
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
        
        return (text, data.get("summary", ""), input_tokens, output_tokens, cost)


class SceneTranslatorNode:
    """
    Translate scenes from Chinese to English.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "scenes_json": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["gpt-4o", "deepseek-chat", "claude-3-5-sonnet-20241022"], {"default": "gpt-4o"}),
                "preserve_style": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "INT", "FLOAT")
    RETURN_NAMES = ("translated_json", "input_tokens", "output_tokens", "cost")
    FUNCTION = "translate"
    CATEGORY = "UnlimitAI/Text/Novel"
    
    def translate(
        self,
        api_key: str,
        scenes_json: str,
        model: str = "gpt-4o",
        preserve_style: bool = True
    ) -> Tuple[str, int, int, float]:
        """
        Translate scenes to English.
        """
        style_instruction = "Maintain the literary style and emotional tone of the original text." if preserve_style else ""
        
        prompt = f"""Translate the following Chinese novel scenes to English. 
{style_instruction}

Keep the JSON structure exactly the same, only translate the text content within the fields.
Do not translate the "visual_prompt" field if it's already in English.

Scenes JSON:
{scenes_json}

Return the translated JSON only, no additional text."""
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        
        response = make_request("/v1/chat/completions", api_key, payload)
        
        text = response["choices"][0]["message"]["content"]
        
        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        cost = estimate_cost(model, input_tokens, output_tokens)
        
        return (text, input_tokens, output_tokens, cost)


NODE_CLASS_MAPPINGS = {
    "UnlimitAITextNode": UnlimitAITextNode,
    "GPT5ReasoningNode": GPT5ReasoningNode,
    "DeepSeekThinkingNode": DeepSeekThinkingNode,
    "StructuredOutputNode": StructuredOutputNode,
    "NovelAnalyzerNode": NovelAnalyzerNode,
    "SceneTranslatorNode": SceneTranslatorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UnlimitAITextNode": "UnlimitAI Text (OpenAI/Claude/DeepSeek)",
    "GPT5ReasoningNode": "GPT-5 Reasoning",
    "DeepSeekThinkingNode": "DeepSeek Thinking",
    "StructuredOutputNode": "Structured Output (JSON Schema)",
    "NovelAnalyzerNode": "Novel Analyzer (Scene Extraction)",
    "SceneTranslatorNode": "Scene Translator (Chinese→English)",
}
