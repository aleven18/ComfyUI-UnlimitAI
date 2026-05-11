from __future__ import annotations

from pydantic import BaseModel, Field


class VEONodeRequest(BaseModel):
    prompt: str
    aspectRatio: str = "16:9"
    duration: str = "5s"
    audio: bool = True
    resolution: str = "1080p"


class VEONodeResponse(BaseModel):
    request_id: str = ""
    status_url: str = ""
    video_url: str = ""


class VEOFalAIRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "16:9"
    duration: str = "5s"


class VEOFalAIResponse(BaseModel):
    request_id: str = ""
    response_url: str = ""
    status_url: str = ""


class VEOVideoData(BaseModel):
    url: str = ""


class VEOPollResponse(BaseModel):
    status: str | None = None
    video: VEOVideoData | None = None
    videos: list[VEOVideoData] | None = None


def veo_status_extractor(response: dict | VEOPollResponse) -> str | None:
    if isinstance(response, dict):
        return response.get("status")
    return response.status
