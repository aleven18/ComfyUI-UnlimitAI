"""
API客户端类型存根

为api_client.py提供类型注解
"""

from typing import Dict, List, Optional, Any, Tuple
from utils.types import (
    TextGenerationResponse,
    ImageGenerationResponse,
    VideoGenerationResponse,
    AudioGenerationResponse,
    MusicGenerationResponse
)


class UnlimitAIClient:
    """UnlimitAI API客户端"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = ...,
        timeout: int = ...,
        max_retries: int = ...
    ) -> None: ...
    
    def generate_text(
        self,
        prompt: str,
        model: str = ...,
        max_tokens: Optional[int] = ...,
        temperature: Optional[float] = ...,
        **kwargs: Any
    ) -> str: ...
    
    def generate_image(
        self,
        prompt: str,
        model: str = ...,
        size: str = ...,
        steps: Optional[int] = ...,
        guidance: Optional[float] = ...,
        seed: Optional[int] = ...,
        **kwargs: Any
    ) -> str: ...
    
    def generate_video(
        self,
        prompt: str,
        model: str = ...,
        duration: float = ...,
        image_url: Optional[str] = ...,
        **kwargs: Any
    ) -> str: ...
    
    def generate_audio(
        self,
        text: str,
        model: str = ...,
        voice: str = ...,
        speed: Optional[float] = ...,
        **kwargs: Any
    ) -> str: ...
    
    def generate_music(
        self,
        prompt: str,
        model: str = ...,
        duration: float = ...,
        **kwargs: Any
    ) -> str: ...
    
    def close(self) -> None: ...
    
    def __enter__(self) -> "UnlimitAIClient": ...
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...


class InputValidator:
    """输入验证器"""
    
    def __init__(
        self,
        max_prompt_length: int = ...,
        max_image_size: int = ...,
        max_video_duration: float = ...
    ) -> None: ...
    
    def validate_prompt(self, prompt: str) -> str: ...
    
    def validate_model_name(self, model: str) -> str: ...
    
    def validate_image_size(self, size: str) -> str: ...
    
    def validate_duration(self, duration: float) -> float: ...
    
    def validate_url(self, url: str) -> str: ...


class ErrorHandler:
    """错误处理器"""
    
    def handle(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = ...,
        reraise: bool = ...
    ) -> Optional[Exception]: ...
