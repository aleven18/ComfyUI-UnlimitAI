from __future__ import annotations

from pydantic import BaseModel, Field

from typing import Literal


IMAGEN4_GENERATE = "/imagen/v4/generate"
IMAGEN4_POLL = "/imagen/v4/generate/{}"


class Imagen4Request(BaseModel):
    prompt: str
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4"] = "1:1"
    output_format: Literal["png", "jpeg"] = "png"
    person_generation: str = "allow_adult"


class Imagen4SubmitResponse(BaseModel):
    id: str = ""
    urls: dict | None = None
    status: str | None = None


class Imagen4OutputItem(BaseModel):
    url: str = ""


class Imagen4PollResponse(BaseModel):
    id: str = ""
    status: str | None = None
    output: list[Imagen4OutputItem] | None = None
    urls: dict | None = None


def imagen_status_extractor(response: dict | Imagen4PollResponse) -> str | None:
    if isinstance(response, dict):
        return response.get("status")
    return response.status


def imagen_image_url_extractor(response: dict | Imagen4PollResponse) -> str:
    if isinstance(response, dict):
        output = response.get("output", [])
        return output[0].get("url", "") if output else ""
    if response.output:
        return response.output[0].url
    return ""
