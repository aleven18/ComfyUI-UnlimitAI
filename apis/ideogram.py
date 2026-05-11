from __future__ import annotations

from pydantic import BaseModel, Field


class IdeogramV3Request(BaseModel):
    prompt: str
    aspect_ratio: str = "ASPECT_16_9"
    model: str = "ideogram-v3"
    style_type: str = "AUTO"
    magic_prompt_option: str = "AUTO"
    seed: int | None = None
    output_format: str = "jpeg"
    n: int = Field(default=1, ge=1, le=4)


class IdeogramImageItem(BaseModel):
    url: str = ""
    width: int | None = None
    height: int | None = None


class IdeogramV3Response(BaseModel):
    created: int | None = None
    data: list[IdeogramImageItem] = Field(default_factory=list)
