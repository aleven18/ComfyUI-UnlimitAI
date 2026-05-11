from __future__ import annotations

from pydantic import BaseModel, Field


class LumaVideoGenRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "16:9"
    loop: bool = False


class LumaSubmitResponse(BaseModel):
    id: str = ""
    status_url: str = ""
    state: str | None = None


class LumaVideoData(BaseModel):
    url: str = ""
    download_url: str | None = None


class LumaPollResponse(BaseModel):
    id: str = ""
    state: str | None = None
    video: LumaVideoData | None = None
    status_url: str | None = None


def luma_status_extractor(response: dict | LumaPollResponse) -> str | None:
    if isinstance(response, dict):
        return response.get("state")
    return response.state
