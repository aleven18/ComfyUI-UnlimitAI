"""
Audio and speech nodes for ComfyUI-UnlimitAI.
Includes TTS, voice cloning, and STT nodes.
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


class MinimaxTTSNode:
    """
    Minimax TTS - best for Chinese voice synthesis.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "text": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["speech-01-turbo", "speech-01-hd"], {"default": "speech-01-turbo"}),
                "voice": ([
                    "male-qn-qingse",
                    "male-qn-jingying",
                    "female-shaonv",
                    "female-yujie",
                    "presenter_male",
                    "presenter_female",
                    "audiobook_male_1",
                    "audiobook_male_2"
                ], {"default": "male-qn-jingying"}),
                "emotion": (["neutral", "happy", "sad", "angry", "fearful", "surprised"], {"default": "neutral"}),
                "speed": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.0, "step": 0.1}),
                "format": (["mp3", "wav", "pcm"], {"default": "mp3"}),
                "sample_rate": ([16000, 24000, 32000], {"default": 32000}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("audio_url", "audio_duration_ms", "characters")
    FUNCTION = "synthesize"
    CATEGORY = "UnlimitAI/Audio/TTS"
    
    def synthesize(
        self,
        api_key: str,
        text: str,
        model: str = "speech-01-turbo",
        voice: str = "male-qn-jingying",
        emotion: str = "neutral",
        speed: float = 1.0,
        format: str = "mp3",
        sample_rate: int = 32000
    ) -> Tuple[str, int, int]:
        """
        Synthesize speech with Minimax TTS.
        """
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "speed": speed,
            "audio_setting": {
                "sample_rate": sample_rate,
                "format": format
            }
        }
        
        if emotion != "neutral":
            payload["voice_setting"] = {
                "emotion": emotion
            }
        
        response = make_request("/v1/audio/speech", api_key, payload)
        
        audio_url = response.get("audio_url", "")
        duration_ms = response.get("duration_ms", 0)
        characters = len(text)
        
        return (audio_url, duration_ms, characters)


class MinimaxTTSAsyncNode:
    """
    Minimax TTS Async V2 - for longer texts.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "text": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["speech-01-turbo", "speech-01-hd"], {"default": "speech-01-turbo"}),
                "voice": ("STRING", {"default": "male-qn-jingying", "multiline": False}),
                "emotion": (["neutral", "happy", "sad", "angry"], {"default": "neutral"}),
                "format": (["mp3", "wav"], {"default": "mp3"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("audio_url", "task_id")
    FUNCTION = "synthesize"
    CATEGORY = "UnlimitAI/Audio/TTS"
    
    def synthesize(
        self,
        api_key: str,
        text: str,
        model: str = "speech-01-turbo",
        voice: str = "male-qn-jingying",
        emotion: str = "neutral",
        format: str = "mp3"
    ) -> Tuple[str, str]:
        """
        Synthesize speech asynchronously.
        """
        payload = {
            "model": model,
            "text": text,
            "voice_setting": {
                "voice_id": voice
            },
            "audio_setting": {
                "format": format
            }
        }
        
        if emotion != "neutral":
            payload["voice_setting"]["emotion"] = emotion
        
        response = make_request("/v1/audio/speech_async_v2", api_key, payload)
        
        task_id = response.get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/v1/audio/speech_async_v2/{task_id}"
            result = poll_status(status_url, api_key, interval=3, max_attempts=60, success_status="completed")
            audio_url = result.get("audio_url", "")
        else:
            audio_url = ""
        
        return (audio_url, task_id)


class MinimaxVoiceCloneNode:
    """
    Minimax voice cloning.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "audio_file_path": ("STRING", {"default": "", "multiline": False}),
                "voice_name": ("STRING", {"default": "my_voice", "multiline": False}),
            },
            "optional": {
                "text": ("STRING", {"default": "", "multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("voice_id", "voice_name")
    FUNCTION = "clone"
    CATEGORY = "UnlimitAI/Audio/VoiceClone"
    
    def clone(
        self,
        api_key: str,
        audio_file_path: str,
        voice_name: str,
        text: str = ""
    ) -> Tuple[str, str]:
        """
        Clone voice from audio file.
        """
        import urllib.request
        import base64
        import hashlib
        
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
        
        boundary = hashlib.md5(str(time.time()).encode()).hexdigest()
        
        body_parts = []
        body_parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(audio_file_path)}"\r\n'
            f'Content-Type: audio/mpeg\r\n\r\n'
        )
        body_parts.append(audio_data)
        body_parts.append(b'\r\n')
        
        body_parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="voice_name"\r\n\r\n'
            f'{voice_name}\r\n'
        )
        
        if text:
            body_parts.append(
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="text"\r\n\r\n'
                f'{text}\r\n'
            )
        
        body_parts.append(f'--{boundary}--\r\n')
        
        body = b''.join(
            part.encode('utf-8') if isinstance(part, str) else part
            for part in body_parts
        )
        
        url = "https://api.unlimitai.org/v1/voice_clone"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
        
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=60) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
        
        voice_id = result.get("voice_id", "")
        
        return (voice_id, voice_name)


class OpenAITTSNode:
    """
    OpenAI TTS - best for English voice synthesis.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "text": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "model": (["tts-1", "tts-1-hd"], {"default": "tts-1-hd"}),
                "voice": (["alloy", "echo", "fable", "onyx", "nova", "shimmer"], {"default": "nova"}),
                "response_format": (["mp3", "opus", "aac", "flac"], {"default": "mp3"}),
                "speed": ("FLOAT", {"default": 1.0, "min": 0.25, "max": 4.0, "step": 0.05}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("audio_url",)
    FUNCTION = "synthesize"
    CATEGORY = "UnlimitAI/Audio/TTS"
    
    def synthesize(
        self,
        api_key: str,
        text: str,
        model: str = "tts-1-hd",
        voice: str = "nova",
        response_format: str = "mp3",
        speed: float = 1.0
    ) -> Tuple[str]:
        """
        Synthesize speech with OpenAI TTS.
        """
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "response_format": response_format,
            "speed": speed
        }
        
        response = make_request("/v1/audio/speech", api_key, payload)
        
        audio_url = response.get("audio_url", "")
        
        return (audio_url,)


class OpenAIWhisperNode:
    """
    OpenAI Whisper speech recognition.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "audio_file_path": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "language": (["zh", "en", "ja", "ko", "auto"], {"default": "auto"}),
                "response_format": (["json", "text", "srt", "vtt"], {"default": "json"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("transcription", "language", "duration")
    FUNCTION = "transcribe"
    CATEGORY = "UnlimitAI/Audio/STT"
    
    def transcribe(
        self,
        api_key: str,
        audio_file_path: str,
        language: str = "auto",
        response_format: str = "json"
    ) -> Tuple[str, str, float]:
        """
        Transcribe audio with Whisper.
        """
        import urllib.request
        import hashlib
        
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
        
        boundary = hashlib.md5(str(time.time()).encode()).hexdigest()
        
        body_parts = []
        body_parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(audio_file_path)}"\r\n'
            f'Content-Type: audio/mpeg\r\n\r\n'
        )
        body_parts.append(audio_data)
        body_parts.append(b'\r\n')
        
        body_parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="model"\r\n\r\n'
            f'whisper-1\r\n'
        )
        
        if language != "auto":
            body_parts.append(
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="language"\r\n\r\n'
                f'{language}\r\n'
            )
        
        body_parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="response_format"\r\n\r\n'
            f'{response_format}\r\n'
        )
        
        body_parts.append(f'--{boundary}--\r\n')
        
        body = b''.join(
            part.encode('utf-8') if isinstance(part, str) else part
            for part in body_parts
        )
        
        url = "https://api.unlimitai.org/v1/audio/transcriptions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
        
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=120) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
        
        text = result.get("text", "")
        detected_language = result.get("language", "")
        duration = result.get("duration", 0.0)
        
        return (text, detected_language, duration)


class KlingAudioGenNode:
    """
    Kling text-to-audio generation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "duration": ("FLOAT", {"default": 5.0, "min": 1.0, "max": 30.0}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("audio_url", "task_id")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Audio/Sound"
    
    def generate(
        self,
        api_key: str,
        prompt: str,
        duration: float = 5.0
    ) -> Tuple[str, str]:
        """
        Generate audio from text with Kling.
        """
        payload = {
            "prompt": prompt,
            "duration": duration
        }
        
        response = make_request("/v1/audio/kling/text-to-audio", api_key, payload)
        
        task_id = response.get("data", {}).get("task_id", "")
        
        if task_id:
            status_url = f"https://api.unlimitai.org/v1/audio/kling/{task_id}"
            result = poll_status(status_url, api_key, interval=3, max_attempts=60, success_status="succeed")
            audio_url = result.get("data", {}).get("task_result", {}).get("audio_url", "")
        else:
            audio_url = ""
        
        return (audio_url, task_id)


class DialogueGeneratorNode:
    """
    Specialized node for generating dialogue audio for drama videos.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "dialogue_text": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "voice_id": ("STRING", {"default": "male-qn-jingying", "multiline": False}),
                "emotion": (["neutral", "happy", "sad", "angry", "fearful"], {"default": "neutral"}),
                "speed": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.0}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("audio_url", "emotion_tags_applied", "duration_ms")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Audio/Drama"
    
    def generate(
        self,
        api_key: str,
        dialogue_text: str,
        voice_id: str = "male-qn-jingying",
        emotion: str = "neutral",
        speed: float = 1.0
    ) -> Tuple[str, str, int]:
        """
        Generate dialogue audio with emotion tags support.
        
        Supported emotion tags:
        - (laughs) - laughter
        - (sighs) - sighing
        - (breath) - breathing
        - (coughs) - coughing
        - [laughter] - laughter alternative
        """
        payload = {
            "model": "speech-01-turbo",
            "input": dialogue_text,
            "voice": voice_id,
            "speed": speed,
            "voice_setting": {
                "emotion": emotion
            },
            "audio_setting": {
                "sample_rate": 32000,
                "format": "mp3"
            }
        }
        
        response = make_request("/v1/audio/speech", api_key, payload)
        
        audio_url = response.get("audio_url", "")
        duration_ms = response.get("duration_ms", 0)
        
        emotion_tags = []
        for tag in ["(laughs)", "(sighs)", "(breath)", "(coughs)", "[laughter]"]:
            if tag in dialogue_text:
                emotion_tags.append(tag)
        
        emotion_tags_str = ", ".join(emotion_tags) if emotion_tags else "none"
        
        return (audio_url, emotion_tags_str, duration_ms)


NODE_CLASS_MAPPINGS = {
    "MinimaxTTSNode": MinimaxTTSNode,
    "MinimaxTTSAsyncNode": MinimaxTTSAsyncNode,
    "MinimaxVoiceCloneNode": MinimaxVoiceCloneNode,
    "OpenAITTSNode": OpenAITTSNode,
    "OpenAIWhisperNode": OpenAIWhisperNode,
    "KlingAudioGenNode": KlingAudioGenNode,
    "DialogueGeneratorNode": DialogueGeneratorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MinimaxTTSNode": "Minimax TTS (Chinese Best)",
    "MinimaxTTSAsyncNode": "Minimax TTS Async (Long Text)",
    "MinimaxVoiceCloneNode": "Minimax Voice Clone",
    "OpenAITTSNode": "OpenAI TTS (English)",
    "OpenAIWhisperNode": "OpenAI Whisper (STT)",
    "KlingAudioGenNode": "Kling Audio Generation",
    "DialogueGeneratorNode": "Dialogue Generator (Drama)",
}
