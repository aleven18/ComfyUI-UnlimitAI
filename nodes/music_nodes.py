"""
Music generation nodes for ComfyUI-UnlimitAI.
Includes Suno music generation nodes.
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


class SunoInspirationModeNode:
    """
    Suno inspiration mode - simple prompt to music.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["chirp-v3-0", "chirp-v3-5", "chirp-v4-5", "chirp-v5"], {"default": "chirp-v3-5"}),
                "make_instrumental": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("audio_url", "title", "task_id", "status")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Music/Suno"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        model: str = "chirp-v3-5",
        make_instrumental: bool = False
    ) -> Tuple[str, str, str, str]:
        """
        Generate music with Suno inspiration mode.
        """
        payload = {
            "prompt": prompt,
            "mv": model,
            "make_instrumental": make_instrumental
        }
        
        if model in ["chirp-v4-5", "chirp-v5"]:
            endpoint = f"/suno/{model.replace('chirp-', '')}/generate"
        else:
            endpoint = "/suno/v3/generate"
        
        response = make_request(endpoint, api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/suno/v3/generate/{task_id}"
            result = poll_status(status_url, api_key, interval=10, max_attempts=120, success_status="complete")
            
            audio_url = result.get("data", [{}])[0].get("audio_url", "")
            title = result.get("data", [{}])[0].get("title", "")
            status = "complete"
        else:
            audio_url = ""
            title = ""
            status = "failed"
        
        return (audio_url, title, task_id, status)


class SunoCustomModeNode:
    """
    Suno custom mode - full control over lyrics and style.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "title": ("STRING", {"default": "", "multiline": False}),
                "tags": ("STRING", {"default": "", "multiline": False}),
                "lyrics": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["chirp-v3-0", "chirp-v3-5", "chirp-v4-5", "chirp-v5"], {"default": "chirp-v3-5"}),
                "make_instrumental": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("audio_url", "title", "task_id", "status")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Music/Suno"
    
    def generate(
        self,
        api_key: str,
        title: str,
        tags: str,
        lyrics: str,
        model: str = "chirp-v3-5",
        make_instrumental: bool = False
    ) -> Tuple[str, str, str, str]:
        """
        Generate music with Suno custom mode.
        """
        payload = {
            "prompt": "",
            "title": title,
            "tags": tags,
            "lyrics": lyrics,
            "mv": model,
            "make_instrumental": make_instrumental
        }
        
        if model in ["chirp-v4-5", "chirp-v5"]:
            endpoint = f"/suno/{model.replace('chirp-', '')}/generate"
        else:
            endpoint = "/suno/v3/generate"
        
        response = make_request(endpoint, api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/suno/v3/generate/{task_id}"
            result = poll_status(status_url, api_key, interval=10, max_attempts=120, success_status="complete")
            
            audio_url = result.get("data", [{}])[0].get("audio_url", "")
            returned_title = result.get("data", [{}])[0].get("title", title)
            status = "complete"
        else:
            audio_url = ""
            returned_title = title
            status = "failed"
        
        return (audio_url, returned_title, task_id, status)


class SunoLyricsGeneratorNode:
    """
    Suno lyrics generator.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "topic": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "style": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("lyrics", "suggested_title")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Music/Suno"
    
    def generate(
        self,
        api_key: str,
        topic: str,
        style: str = ""
    ) -> Tuple[str, str]:
        """
        Generate lyrics with Suno.
        """
        payload = {
            "prompt": topic
        }
        
        if style:
            payload["style"] = style
        
        response = make_request("/suno/v3/generate/lyrics", api_key, payload)
        
        lyrics = response.get("data", {}).get("lyrics", "")
        title = response.get("data", {}).get("title", "")
        
        return (lyrics, title)


class SunoExtendNode:
    """
    Suno extend existing song.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "audio_id": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "continue_at": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0}),
                "model": (["chirp-v3-0", "chirp-v3-5"], {"default": "chirp-v3-5"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("audio_url", "task_id")
    FUNCTION = "extend"
    CATEGORY = "UnlimitAI/Music/Suno"
    
    def extend(
        self,
        api_key: str,
        audio_id: str,
        prompt: str = "",
        continue_at: float = 0.0,
        model: str = "chirp-v3-5"
    ) -> Tuple[str, str]:
        """
        Extend existing song.
        """
        payload = {
            "audio_id": audio_id,
            "mv": model
        }
        
        if prompt:
            payload["prompt"] = prompt
        
        if continue_at > 0:
            payload["continue_at"] = continue_at
        
        response = make_request("/suno/v3/extend", api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/suno/v3/generate/{task_id}"
            result = poll_status(status_url, api_key, interval=10, max_attempts=120, success_status="complete")
            audio_url = result.get("data", [{}])[0].get("audio_url", "")
        else:
            audio_url = ""
        
        return (audio_url, task_id)


class BackgroundMusicGeneratorNode:
    """
    Specialized node for generating background music for drama videos.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "scene_mood": ([
                    "emotional",
                    "suspenseful",
                    "romantic",
                    "action",
                    "peaceful",
                    "dramatic",
                    "melancholic",
                    "upbeat",
                    "tense"
                ], {"default": "emotional"}),
            },
            "optional": {
                "duration_seconds": ("INT", {"default": 30, "min": 10, "max": 180}),
                "style": ("STRING", {"default": "", "multiline": False}),
                "make_instrumental": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("audio_url", "title", "mood")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Music/Drama"
    
    def generate(
        self,
        api_key: str,
        scene_mood: str,
        duration_seconds: int = 30,
        style: str = "",
        make_instrumental: bool = True
    ) -> Tuple[str, str, str]:
        """
        Generate background music for drama scene.
        """
        mood_prompts = {
            "emotional": "emotional piano background music, touching and moving",
            "suspenseful": "suspenseful thriller background music, mysterious and tense",
            "romantic": "romantic love theme, soft and tender background music",
            "action": "action movie background music, energetic and intense",
            "peaceful": "peaceful ambient background music, calm and relaxing",
            "dramatic": "dramatic orchestral background music, cinematic and powerful",
            "melancholic": "melancholic sad background music, emotional and touching",
            "upbeat": "upbeat energetic background music, positive and motivating",
            "tense": "tense dramatic background music, building tension"
        }
        
        prompt = mood_prompts.get(scene_mood, mood_prompts["emotional"])
        
        if style:
            prompt += f", {style}"
        
        payload = {
            "prompt": prompt,
            "mv": "chirp-v3-5",
            "make_instrumental": make_instrumental
        }
        
        response = make_request("/suno/v3/generate", api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/suno/v3/generate/{task_id}"
            result = poll_status(status_url, api_key, interval=10, max_attempts=120, success_status="complete")
            audio_url = result.get("data", [{}])[0].get("audio_url", "")
            title = result.get("data", [{}])[0].get("title", f"{scene_mood} background")
        else:
            audio_url = ""
            title = ""
        
        return (audio_url, title, scene_mood)


class SoundtrackComposerNode:
    """
    Compose complete soundtrack for drama video with multiple moods.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "scenes_json": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "overall_style": ("STRING", {"default": "cinematic", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("soundtrack_json", "summary")
    FUNCTION = "compose"
    CATEGORY = "UnlimitAI/Music/Drama"
    
    def compose(
        self,
        api_key: str,
        scenes_json: str,
        overall_style: str = "cinematic"
    ) -> Tuple[str, str]:
        """
        Compose soundtrack for multiple scenes.
        """
        scenes = json.loads(scenes_json)
        soundtrack = []
        
        for idx, scene in enumerate(scenes.get("scenes", [])):
            mood = scene.get("mood", "emotional")
            
            mood_prompts = {
                "emotional": "emotional piano, touching",
                "suspenseful": "suspenseful thriller, mysterious",
                "romantic": "romantic love theme, soft",
                "action": "action movie, energetic",
                "peaceful": "peaceful ambient, calm",
                "dramatic": "dramatic orchestral, cinematic",
                "melancholic": "melancholic sad, touching",
                "upbeat": "upbeat energetic, positive",
                "tense": "tense dramatic, building"
            }
            
            prompt = mood_prompts.get(mood, mood_prompts["emotional"])
            prompt += f", {overall_style}"
            
            payload = {
                "prompt": prompt,
                "mv": "chirp-v3-5",
                "make_instrumental": True
            }
            
            try:
                response = make_request("/suno/v3/generate", api_key, payload)
                task_id = response.get("data", {}).get("task_id", "")
                
                if task_id:
                    status_url = f"https://api.unlimitai.org/suno/v3/generate/{task_id}"
                    result = poll_status(status_url, api_key, interval=10, max_attempts=120, success_status="complete")
                    audio_url = result.get("data", [{}])[0].get("audio_url", "")
                else:
                    audio_url = ""
            except Exception as e:
                audio_url = ""
            
            soundtrack.append({
                "scene_number": scene.get("scene_number", idx + 1),
                "mood": mood,
                "audio_url": audio_url,
                "scene_title": scene.get("title", "")
            })
        
        result_json = json.dumps({"soundtrack": soundtrack}, ensure_ascii=False, indent=2)
        
        summary = f"Generated {len(soundtrack)} background music tracks for drama scenes"
        
        return (result_json, summary)


NODE_CLASS_MAPPINGS = {
    "SunoInspirationModeNode": SunoInspirationModeNode,
    "SunoCustomModeNode": SunoCustomModeNode,
    "SunoLyricsGeneratorNode": SunoLyricsGeneratorNode,
    "SunoExtendNode": SunoExtendNode,
    "BackgroundMusicGeneratorNode": BackgroundMusicGeneratorNode,
    "SoundtrackComposerNode": SoundtrackComposerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SunoInspirationModeNode": "Suno Inspiration Mode",
    "SunoCustomModeNode": "Suno Custom Mode",
    "SunoLyricsGeneratorNode": "Suno Lyrics Generator",
    "SunoExtendNode": "Suno Extend Song",
    "BackgroundMusicGeneratorNode": "Background Music (Drama)",
    "SoundtrackComposerNode": "Soundtrack Composer (Multi-Scene)",
}
