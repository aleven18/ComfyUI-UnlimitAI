"""
Image generation nodes for ComfyUI-UnlimitAI.
Includes FLUX, Kling, VEO, Ideogram, and other image models.
"""
import json
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..utils.helpers import make_request, poll_status, download_file

logger = logging.getLogger(__name__)


def url_to_comfy_image(image_url: str):
    """
    Download image from URL and convert to ComfyUI IMAGE format.
    
    Args:
        image_url: URL of the image
    
    Returns:
        ComfyUI IMAGE tensor or None if failed
    """
    if not image_url:
        return None
    
    import urllib.request
    import io
    import torch
    import numpy as np
    from PIL import Image
    
    try:
        with urllib.request.urlopen(image_url) as url_response:
            img_data = url_response.read()
            pil_image = Image.open(io.BytesIO(img_data))
            pil_image = pil_image.convert("RGB")
            img_array = np.array(pil_image).astype(np.float32) / 255.0
            return torch.from_numpy(img_array)[None,]
    except Exception as e:
        logger.error(f"Error loading image: {e}", exc_info=True)
        return None


class FluxProNode:
    """
    FLUX Pro image generation - synchronous, fast, high quality.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "image_size": (["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"], {"default": "landscape_16_9"}),
                "num_inference_steps": ("INT", {"default": 30, "min": 1, "max": 50}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999999}),
                "guidance_scale": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 35.0, "step": 0.1}),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "enable_safety_checker": ("BOOLEAN", {"default": True}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "sync": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "request_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Image/FLUX"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        image_size: str = "landscape_16_9",
        num_inference_steps: int = 30,
        seed: int = 0,
        guidance_scale: float = 3.5,
        num_images: int = 1,
        enable_safety_checker: bool = True,
        output_format: str = "jpeg",
        sync: bool = True
    ) -> Tuple[Any, str, str]:
        """
        Generate image with FLUX Pro.
        """
        payload = {
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": num_inference_steps,
            "seed": seed,
            "guidance_scale": guidance_scale,
            "num_images": num_images,
            "enable_safety_checker": enable_safety_checker,
            "output_format": output_format,
            "sync": sync
        }
        
        response = make_request("/fal-ai/flux-pro", api_key, payload)
        
        request_id = response.get("request_id", "")
        image_url = response.get("images", [{}])[0].get("url", "")
        
        image = url_to_comfy_image(image_url)
        if image_url:
            
            with urllib.request.urlopen(image_url) as url_response:
                img_data = url_response.read()
                pil_image = Image.open(io.BytesIO(img_data))
                pil_image = pil_image.convert("RGB")
                img_array = np.array(pil_image).astype(np.float32) / 255.0
                image = torch.from_numpy(img_array)[None,]
        
        return (image, image_url, request_id)


class FluxProKontextNode:
    """
    FLUX Pro Kontext for image editing.
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
                "num_inference_steps": ("INT", {"default": 30, "min": 1, "max": 50}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999999}),
                "guidance_scale": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 35.0, "step": 0.1}),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "enable_safety_checker": ("BOOLEAN", {"default": True}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "sync": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "request_id")
    FUNCTION = "edit"
    CATEGORY = "UnlimitAI/Image/FLUX"
    
    def edit(
        self,
        api_key: str,
        prompt: str,
        image_url: str,
        num_inference_steps: int = 30,
        seed: int = 0,
        guidance_scale: float = 3.5,
        num_images: int = 1,
        enable_safety_checker: bool = True,
        output_format: str = "jpeg",
        sync: bool = True
    ) -> Tuple[Any, str, str]:
        """
        Edit image with FLUX Pro Kontext.
        """
        payload = {
            "prompt": prompt,
            "image_url": image_url,
            "num_inference_steps": num_inference_steps,
            "seed": seed,
            "guidance_scale": guidance_scale,
            "num_images": num_images,
            "enable_safety_checker": enable_safety_checker,
            "output_format": output_format,
            "sync": sync
        }
        
        response = make_request("/fal-ai/flux-pro/kontext", api_key, payload)
        
        request_id = response.get("request_id", "")
        result_url = response.get("images", [{}])[0].get("url", "")
        
        image = None
        if result_url:
            
            with urllib.request.urlopen(result_url) as url_response:
                img_data = url_response.read()
                pil_image = Image.open(io.BytesIO(img_data))
                pil_image = pil_image.convert("RGB")
                img_array = np.array(pil_image).astype(np.float32) / 255.0
                image = torch.from_numpy(img_array)[None,]
        
        return (image, result_url, request_id)


class IdeogramV3Node:
    """
    Ideogram V3 for high-quality image generation with text rendering.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "aspect_ratio": (["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"], {"default": "16:9"}),
                "model": (["V_3", "V_3_TURBO"], {"default": "V_3"}),
                "style_type": (["AUTO", "GENERAL", "REALISTIC", "DESIGN", "3D", "ANIME"], {"default": "AUTO"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999999}),
                "magic_prompt_option": (["AUTO", "ON", "OFF"], {"default": "AUTO"}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "request_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Image/Ideogram"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        model: str = "V_3",
        style_type: str = "AUTO",
        seed: int = 0,
        magic_prompt_option: str = "AUTO",
        negative_prompt: str = ""
    ) -> Tuple[Any, str, str]:
        """
        Generate image with Ideogram V3.
        """
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "model": model,
            "style_type": style_type,
            "seed": seed if seed > 0 else None,
            "magic_prompt_option": magic_prompt_option
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        response = make_request("/v1/ideogram/generate", api_key, payload)
        
        request_id = response.get("request_id", "")
        image_url = response.get("data", [{}])[0].get("url", "")
        
        image = url_to_comfy_image(image_url)
        if image_url:
            
            with urllib.request.urlopen(image_url) as url_response:
                img_data = url_response.read()
                pil_image = Image.open(io.BytesIO(img_data))
                pil_image = pil_image.convert("RGB")
                img_array = np.array(pil_image).astype(np.float32) / 255.0
                image = torch.from_numpy(img_array)[None,]
        
        return (image, image_url, request_id)


class KlingImageGenNode:
    """
    Kling image generation.
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
                "aspect_ratio": (["1:1", "16:9", "9:16", "4:3", "3:4"], {"default": "16:9"}),
                "image_reference": ("STRING", {"default": "", "multiline": False}),
                "image_reference_type": (["IMAGE_REFERENCE_TYPE_ALL", "IMAGE_REFERENCE_TYPE_APAINT", "IMAGE_REFERENCE_TYPE_FACE"], {"default": "IMAGE_REFERENCE_TYPE_ALL"}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "n": ("INT", {"default": 1, "min": 1, "max": 9}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 999999999}),
                "callback_url": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Image/Kling"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        model: str = "kling-v2",
        aspect_ratio: str = "16:9",
        image_reference: str = "",
        image_reference_type: str = "IMAGE_REFERENCE_TYPE_ALL",
        negative_prompt: str = "",
        n: int = 1,
        seed: int = -1,
        callback_url: str = ""
    ) -> Tuple[Any, str, str]:
        """
        Generate image with Kling.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "n": n
        }
        
        if image_reference:
            payload["image_reference"] = image_reference
            payload["image_reference_type"] = image_reference_type
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        if seed >= 0:
            payload["seed"] = seed
        
        if callback_url:
            payload["callback_url"] = callback_url
        
        response = make_request("/v1/images/kling", api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        status_url = f"https://api.unlimitai.org/v1/images/kling/{task_id}"
        result = poll_status(status_url, api_key, interval=3, max_attempts=200, success_status="succeed")
        
        task_status = result.get("data", {}).get("task_status", "")
        if task_status != "succeed":
            raise Exception(f"Image generation failed: {task_status}")
        
        image_url = result.get("data", {}).get("task_result", {}).get("images", [{}])[0].get("url", "")
        
        image = url_to_comfy_image(image_url)
        if image_url:
            
            with urllib.request.urlopen(image_url) as url_response:
                img_data = url_response.read()
                pil_image = Image.open(io.BytesIO(img_data))
                pil_image = pil_image.convert("RGB")
                img_array = np.array(pil_image).astype(np.float32) / 255.0
                image = torch.from_numpy(img_array)[None,]
        
        return (image, image_url, task_id)


class GPTImageNode:
    """
    GPT Image generation (DALL-E 3).
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["dall-e-3", "dall-e-2"], {"default": "dall-e-3"}),
                "size": (["1024x1024", "1792x1024", "1024x1792"], {"default": "1792x1024"}),
                "quality": (["standard", "hd"], {"default": "hd"}),
                "style": (["vivid", "natural"], {"default": "vivid"}),
                "n": ("INT", {"default": 1, "min": 1, "max": 1}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "revised_prompt")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Image/OpenAI"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1792x1024",
        quality: str = "hd",
        style: str = "vivid",
        n: int = 1
    ) -> Tuple[Any, str, str]:
        """
        Generate image with GPT Image (DALL-E).
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "style": style,
            "n": n,
            "response_format": "url"
        }
        
        response = make_request("/v1/images/generations", api_key, payload)
        
        image_data = response.get("data", [{}])[0]
        image_url = image_data.get("url", "")
        revised_prompt = image_data.get("revised_prompt", "")
        
        image = url_to_comfy_image(image_url)
        if image_url:
            
            with urllib.request.urlopen(image_url) as url_response:
                img_data = url_response.read()
                pil_image = Image.open(io.BytesIO(img_data))
                pil_image = pil_image.convert("RGB")
                img_array = np.array(pil_image).astype(np.float32) / 255.0
                image = torch.from_numpy(img_array)[None,]
        
        return (image, image_url, revised_prompt)


class Imagen4Node:
    """
    Google Imagen 4 image generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["imagen-4.0-generate-preview-05-20", "imagen-4.0-fast-generate-preview-05-20", "imagen-4.0-ultra-generate-preview-05-20"], {"default": "imagen-4.0-generate-preview-05-20"}),
                "aspect_ratio": (["1:1", "16:9", "9:16", "4:3", "3:4"], {"default": "16:9"}),
                "number_of_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 999999999}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "request_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Image/Google"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        model: str = "imagen-4.0-generate-preview-05-20",
        aspect_ratio: str = "16:9",
        number_of_images: int = 1,
        negative_prompt: str = "",
        seed: int = 0
    ) -> Tuple[Any, str, str]:
        """
        Generate image with Imagen 4.
        """
        payload = {
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
            "numberOfImages": number_of_images
        }
        
        if negative_prompt:
            payload["negativePrompt"] = negative_prompt
        
        if seed > 0:
            payload["seed"] = seed
        
        response = make_request(f"/replicate/v1/models/google/{model}/predictions", api_key, payload)
        
        request_id = response.get("id", "")
        status_url = response.get("urls", {}).get("get", "")
        
        if status_url:
            result = poll_status(status_url, api_key, interval=2, max_attempts=300)
            image_url = result.get("output", [""])[0] if isinstance(result.get("output"), list) else result.get("output", "")
        else:
            image_url = ""
        
        image = url_to_comfy_image(image_url)
        if image_url:
            
            with urllib.request.urlopen(image_url) as url_response:
                img_data = url_response.read()
                pil_image = Image.open(io.BytesIO(img_data))
                pil_image = pil_image.convert("RGB")
                img_array = np.array(pil_image).astype(np.float32) / 255.0
                image = torch.from_numpy(img_array)[None,]
        
        return (image, image_url, request_id)


class RecraftV3Node:
    """
    Recraft V3 for vector and raster image generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["recraftv3", "recraftv3-svg"], {"default": "recraftv3"}),
                "style": (["realistic_image", "digital_illustration", "vector_illustration"], {"default": "realistic_image"}),
                "style_type": (["none", "realistic", "digital_illustration", "vector_illustration", "icon"], {"default": "none"}),
                "size": (["1024x1024", "1365x1024", "1024x1365", "1536x1024", "1024x1536"], {"default": "1536x1024"}),
                "controls": ("STRING", {"default": "", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "image_url", "request_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Image/Recraft"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        model: str = "recraftv3",
        style: str = "realistic_image",
        style_type: str = "none",
        size: str = "1536x1024",
        controls: str = ""
    ) -> Tuple[Any, str, str]:
        """
        Generate image with Recraft V3.
        """
        payload = {
            "input": {
                "prompt": prompt,
                "style": style,
                "size": size
            }
        }
        
        if controls:
            try:
                controls_dict = json.loads(controls)
                payload["input"].update(controls_dict)
            except:
                pass
        
        response = make_request(f"/fal-ai/{model}", api_key, payload)
        
        request_id = response.get("request_id", "")
        image_url = response.get("images", [{}])[0].get("url", "")
        
        image = url_to_comfy_image(image_url)
        if image_url:
            
            with urllib.request.urlopen(image_url) as url_response:
                img_data = url_response.read()
                pil_image = Image.open(io.BytesIO(img_data))
                pil_image = pil_image.convert("RGB")
                img_array = np.array(pil_image).astype(np.float32) / 255.0
                image = torch.from_numpy(img_array)[None,]
        
        return (image, image_url, request_id)


NODE_CLASS_MAPPINGS = {
    "FluxProNode": FluxProNode,
    "FluxProKontextNode": FluxProKontextNode,
    "IdeogramV3Node": IdeogramV3Node,
    "KlingImageGenNode": KlingImageGenNode,
    "GPTImageNode": GPTImageNode,
    "Imagen4Node": Imagen4Node,
    "RecraftV3Node": RecraftV3Node,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxProNode": "FLUX Pro (Text-to-Image)",
    "FluxProKontextNode": "FLUX Pro Kontext (Image Edit)",
    "IdeogramV3Node": "Ideogram V3 (Text Render)",
    "KlingImageGenNode": "Kling Image (Generation)",
    "GPTImageNode": "GPT Image (DALL-E 3)",
    "Imagen4Node": "Imagen 4 (Google)",
    "RecraftV3Node": "Recraft V3 (Vector/Raster)",
}
