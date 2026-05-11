from __future__ import annotations

from pydantic import BaseModel, Field


class Imagen4Request(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"
    output_format: str = "png"
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
