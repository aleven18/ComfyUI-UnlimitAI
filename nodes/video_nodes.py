"""
Video generation nodes for ComfyUI-UnlimitAI.
Includes VEO, Kling, Minimax, VIDU, Luma, Runway nodes.
"""
import logging
logger = logging.getLogger(__name__)

import json
import time
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..utils.helpers import make_request, poll_status, download_file


class VEONode:
    """
    VEO 3.1 video generation - highest quality with audio.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["veo-3.1", "veo-3.1-fast", "veo-3", "veo-3-fast"], {"default": "veo-3.1"}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "duration": (["5s", "10s"], {"default": "5s"}),
                "audio": ("BOOLEAN", {"default": True}),
                "resolution": (["1080p", "4k"], {"default": "1080p"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("video_url", "request_id", "status_url")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/VEO"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        model: str = "veo-3.1",
        aspect_ratio: str = "16:9",
        duration: str = "5s",
        audio: bool = True,
        resolution: str = "1080p"
    ) -> Tuple[str, str, str]:
        """
        Generate video with VEO.
        """
        payload = {
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
            "duration": duration,
            "audio": audio,
            "resolution": resolution
        }
        
        endpoint = f"/veo/{model}/generate"
        response = make_request(endpoint, api_key, payload)
        
        request_id = response.get("request_id", "")
        status_url = response.get("status_url", "")
        
        if status_url:
            result = poll_status(status_url, api_key, interval=10, max_attempts=180)
            video_url = result.get("video", {}).get("url", "")
        else:
            video_url = ""
        
        return (video_url, request_id, status_url)


class VEONodeFalAI:
    """
    VEO 3 via Fal-ai format (simpler interface).
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "duration": (["5s", "10s"], {"default": "5s"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("video_url", "request_id", "status_url")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/VEO"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration: str = "5s"
    ) -> Tuple[str, str, str]:
        """
        Generate video with VEO via Fal-ai.
        """
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration
        }
        
        response = make_request("/fal-ai/veo-3", api_key, payload)
        
        request_id = response.get("request_id", "")
        response_url = response.get("response_url", "")
        status_url = response.get("status_url", "")
        
        if response_url:
            result_url = response_url.replace("queue.fal.run", "api.unlimitai.org/fal-ai/veo-3/requests")
            result = poll_status(result_url, api_key, interval=10, max_attempts=180)
            video_url = result.get("video", {}).get("url", "")
        else:
            video_url = ""
        
        return (video_url, request_id, status_url)


class KlingVideoGenNode:
    """
    Kling video generation with rich features.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["kling-v1", "kling-v1-5", "kling-v2"], {"default": "kling-v2"}),
                "duration": (["5", "10"], {"default": "5"}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "cfg_scale": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1}),
                "mode": (["std", "pro"], {"default": "std"}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/Kling"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        model: str = "kling-v2",
        duration: str = "5",
        aspect_ratio: str = "16:9",
        cfg_scale: float = 0.5,
        mode: str = "std",
        negative_prompt: str = ""
    ) -> Tuple[str, str]:
        """
        Generate video with Kling.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "cfg_scale": cfg_scale,
            "mode": mode
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        response = make_request("/v1/videos/kling", api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/v1/videos/kling/{task_id}"
            result = poll_status(status_url, api_key, interval=5, max_attempts=240, success_status="succeed")
            
            task_status = result.get("data", {}).get("task_status", "")
            if task_status == "succeed":
                video_url = result.get("data", {}).get("task_result", {}).get("videos", [{}])[0].get("url", "")
            else:
                raise Exception(f"Video generation failed: {task_status}")
        else:
            video_url = ""
        
        return (video_url, task_id)


class KlingImageToVideoNode:
    """
    Kling image-to-video generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "image_url": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "model": (["kling-v1", "kling-v1-5", "kling-v2"], {"default": "kling-v2"}),
                "duration": (["5", "10"], {"default": "5"}),
                "cfg_scale": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/Kling"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        image_url: str,
        model: str = "kling-v2",
        duration: str = "5",
        cfg_scale: float = 0.5
    ) -> Tuple[str, str]:
        """
        Generate video from image with Kling.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "image": image_url,
            "duration": duration,
            "cfg_scale": cfg_scale
        }
        
        response = make_request("/v1/videos/kling/image-to-video", api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/v1/videos/kling/{task_id}"
            result = poll_status(status_url, api_key, interval=5, max_attempts=240, success_status="succeed")
            
            task_status = result.get("data", {}).get("task_status", "")
            if task_status == "succeed":
                video_url = result.get("data", {}).get("task_result", {}).get("videos", [{}])[0].get("url", "")
            else:
                raise Exception(f"Video generation failed: {task_status}")
        else:
            video_url = ""
        
        return (video_url, task_id)


class KlingDigitalHumanNode:
    """
    Kling digital human generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "image_url": ("STRING", {"default": "", "multiline": False}),
                "text": ("STRING", {"default": "", "multiline": True}),
                "voice_id": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "model": (["kling-v1"], {"default": "kling-v1"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/Kling"
    
    def generate(
        self,
        api_key: str,
        image_url: str,
        text: str,
        voice_id: str,
        model: str = "kling-v1"
    ) -> Tuple[str, str]:
        """
        Generate digital human video.
        """
        payload = {
            "model": model,
            "input": {
                "image": image_url,
                "text": text,
                "voice_id": voice_id
            }
        }
        
        response = make_request("/v1/videos/kling/digital-human", api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/v1/videos/kling/{task_id}"
            result = poll_status(status_url, api_key, interval=5, max_attempts=300, success_status="succeed")
            
            task_status = result.get("data", {}).get("task_status", "")
            if task_status == "succeed":
                video_url = result.get("data", {}).get("task_result", {}).get("videos", [{}])[0].get("url", "")
            else:
                raise Exception(f"Digital human generation failed: {task_status}")
        else:
            video_url = ""
        
        return (video_url, task_id)


class MinimaxHailuoNode:
    """
    Minimax Hailuo video generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["video-01", "T2V-01", "T2V-01-Director"], {"default": "T2V-01-Director"}),
                "first_frame_image": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/Minimax"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        model: str = "T2V-01-Director",
        first_frame_image: str = ""
    ) -> Tuple[str, str]:
        """
        Generate video with Minimax Hailuo.
        """
        payload = {
            "model": model,
            "prompt": prompt
        }
        
        if first_frame_image:
            payload["first_frame_image"] = first_frame_image
        
        response = make_request("/v1/video/generation", api_key, payload)
        
        task_id = response.get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/v1/video/generation/{task_id}"
            result = poll_status(status_url, api_key, interval=10, max_attempts=180, success_status="success")
            video_url = result.get("video_url", "")
        else:
            video_url = ""
        
        return (video_url, task_id)


class VIDUVideoGenNode:
    """
    VIDU video generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["vidu1.5", "vidu2"], {"default": "vidu2"}),
                "duration": ([4, 8], {"default": 4}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "style": (["general", "anime"], {"default": "general"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999999}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/VIDU"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        model: str = "vidu2",
        duration: int = 4,
        aspect_ratio: str = "16:9",
        style: str = "general",
        seed: int = 0
    ) -> Tuple[str, str]:
        """
        Generate video with VIDU.
        """
        payload = {
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "style": style
        }
        
        if seed > 0:
            payload["seed"] = seed
        
        response = make_request("/v1/videos/vidu", api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/v1/videos/vidu/{task_id}"
            result = poll_status(status_url, api_key, interval=5, max_attempts=180, success_status="success")
            
            video_url = result.get("data", {}).get("video_url", "")
        else:
            video_url = ""
        
        return (video_url, task_id)


class VIDUImageToVideoNode:
    """
    VIDU image-to-video generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "image_url": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "model": (["vidu1.5", "vidu2"], {"default": "vidu2"}),
                "duration": ([4, 8], {"default": 4}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/VIDU"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        image_url: str,
        model: str = "vidu2",
        duration: int = 4,
        aspect_ratio: str = "16:9"
    ) -> Tuple[str, str]:
        """
        Generate video from image with VIDU.
        """
        payload = {
            "prompt": prompt,
            "image": image_url,
            "model": model,
            "duration": duration,
            "aspect_ratio": aspect_ratio
        }
        
        response = make_request("/v1/videos/vidu/image-to-video", api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/v1/videos/vidu/{task_id}"
            result = poll_status(status_url, api_key, interval=5, max_attempts=180, success_status="success")
            
            video_url = result.get("data", {}).get("video_url", "")
        else:
            video_url = ""
        
        return (video_url, task_id)


class LumaVideoGenNode:
    """
    Luma video generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "loop": ("BOOLEAN", {"default": False}),
                "image_url": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/Luma"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        loop: bool = False,
        image_url: str = ""
    ) -> Tuple[str, str]:
        """
        Generate video with Luma.
        """
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": loop
        }
        
        if image_url:
            payload["image_url"] = image_url
        
        response = make_request("/luma/v2/video/generation", api_key, payload)
        
        task_id = response.get("id", "")
        status_url = response.get("status_url", "")
        
        if status_url:
            result = poll_status(status_url, api_key, interval=5, max_attempts=180)
            video_url = result.get("video", {}).get("url", "")
        else:
            video_url = ""
        
        return (video_url, task_id)


class RunwayGen4Node:
    """
    Runway Gen-4 Turbo video generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "image_url": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "duration": ([5, 10], {"default": 5}),
                "ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999999}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Video/Runway"
    
    def generate(
        self,
        api_key: str,
        image_url: str,
        prompt: str = "",
        duration: int = 5,
        ratio: str = "16:9",
        seed: int = 0
    ) -> Tuple[str, str]:
        """
        Generate video with Runway Gen-4.
        """
        payload = {
            "promptImage": image_url,
            "duration": duration,
            "ratio": ratio
        }
        
        if prompt:
            payload["promptText"] = prompt
        
        if seed > 0:
            payload["seed"] = seed
        
        response = make_request("/runway/v1/image_to_video", api_key, payload)
        
        task_id = response.get("id", "")
        status_url = response.get("status_url", "")
        
        if status_url:
            result = poll_status(status_url, api_key, interval=5, max_attempts=180)
            video_url = result.get("video", [{}])[0] if isinstance(result.get("video"), list) else result.get("video", "")
        else:
            video_url = ""
        
        return (video_url, task_id)


NODE_CLASS_MAPPINGS = {
    "VEONode": VEONode,
    "VEONodeFalAI": VEONodeFalAI,
    "KlingVideoGenNode": KlingVideoGenNode,
    "KlingImageToVideoNode": KlingImageToVideoNode,
    "KlingDigitalHumanNode": KlingDigitalHumanNode,
    "MinimaxHailuoNode": MinimaxHailuoNode,
    "VIDUVideoGenNode": VIDUVideoGenNode,
    "VIDUImageToVideoNode": VIDUImageToVideoNode,
    "LumaVideoGenNode": LumaVideoGenNode,
    "RunwayGen4Node": RunwayGen4Node,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VEONode": "VEO 3.1 (Text-to-Video)",
    "VEONodeFalAI": "VEO 3 (Fal-ai)",
    "KlingVideoGenNode": "Kling Video (Text-to-Video)",
    "KlingImageToVideoNode": "Kling Image-to-Video",
    "KlingDigitalHumanNode": "Kling Digital Human",
    "MinimaxHailuoNode": "Minimax Hailuo (Video)",
    "VIDUVideoGenNode": "VIDU Video (Text-to-Video)",
    "VIDUImageToVideoNode": "VIDU Image-to-Video",
    "LumaVideoGenNode": "Luma Video",
    "RunwayGen4Node": "Runway Gen-4 Turbo",
}
