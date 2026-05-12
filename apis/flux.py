from __future__ import annotations

from pydantic import BaseModel, Field


FLUX_PRO_GENERATE = "/flux/v1/pro"
FLUX_DEV_GENERATE = "/flux/v1/dev"
FLUX_SCHNELL_GENERATE = "/flux/v1/schnell"
FLUX_PRO_KONTEXT = "/flux/v1/pro/kontext"


class FluxProRequest(BaseModel):
    prompt: str
    image_size: str = "landscape_16_9"
    num_inference_steps: int = Field(default=30, ge=1, le=50)
    seed: int = Field(default=0, ge=0)
    guidance_scale: float = Field(default=3.5, ge=0.0, le=35.0)
    num_images: int = Field(default=1, ge=1, le=4)
    enable_safety_checker: bool = True
    output_format: str = "jpeg"
    sync: bool = True


class FluxImageItem(BaseModel):
    url: str = ""
    width: int | None = None
    height: int | None = None
    content_type: str | None = None


class FluxProResponse(BaseModel):
    request_id: str = ""
    images: list[FluxImageItem] = Field(default_factory=list)
    timings: dict | None = None
    seed: int | None = None
    has_nsfw_concepts: list[bool] | None = None


class FluxProKontextRequest(BaseModel):
    prompt: str
    image_url: str | None = None
    image: str | None = None
    num_inference_steps: int = Field(default=30, ge=1, le=50)
    seed: int = Field(default=0, ge=0)
    guidance_scale: float = Field(default=3.5, ge=0.0, le=35.0)
    num_images: int = Field(default=1, ge=1, le=4)
    enable_safety_checker: bool = True
    output_format: str = "jpeg"
    sync: bool = True


class FluxProKontextResponse(FluxProResponse):
    pass


class FluxDevRequest(BaseModel):
    prompt: str
    image_size: str = "landscape_16_9"
    num_inference_steps: int = Field(default=28, ge=1, le=50)
    seed: int = Field(default=0, ge=0)
    guidance_scale: float = Field(default=3.5, ge=0.0, le=35.0)
    num_images: int = Field(default=1, ge=1, le=4)
    enable_safety_checker: bool = True
    output_format: str = "jpeg"
    sync: bool = True


class FluxDevResponse(FluxProResponse):
    pass


class FluxSchnellRequest(BaseModel):
    prompt: str
    image_size: str = "landscape_16_9"
    num_inference_steps: int = Field(default=4, ge=1, le=50)
    seed: int = Field(default=0, ge=0)
    guidance_scale: float = Field(default=3.5, ge=0.0, le=35.0)
    num_images: int = Field(default=1, ge=1, le=4)
    enable_safety_checker: bool = True
    output_format: str = "jpeg"
    sync: bool = True


class FluxSchnellResponse(FluxProResponse):
    pass


def flux_image_url_extractor(response: dict | FluxProResponse) -> str:
    if isinstance(response, dict):
        images = response.get("images", [])
        return images[0]["url"] if images else ""
    if response.images:
        return response.images[0].url
    return ""
