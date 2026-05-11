from __future__ import annotations

from pydantic import BaseModel, Field


class VIDUVideoGenRequest(BaseModel):
    model: str = "vidu2"
    prompt: str
    duration: str = "4"
    aspect_ratio: str = "16:9"
    style: str = "general"


class VIDUImageToVideoRequest(BaseModel):
    model: str = "vidu2"
    prompt: str = ""
    image_url: str | None = None
    image: str | None = None
    duration: str = "4"
    aspect_ratio: str = "16:9"


class VIDUTaskData(BaseModel):
    task_id: str = ""
    status: str = ""


class VIDUSubmitResponse(BaseModel):
    data: VIDUTaskData = Field(default_factory=VIDUTaskData)


class VIDUPollResponse(BaseModel):
    data: VIDUTaskData = Field(default_factory=VIDUTaskData)
    video_url: str | None = None


def vidu_status_extractor(response: dict | VIDUPollResponse) -> str | None:
    if isinstance(response, dict):
        data = response.get("data", {})
        return data.get("status") if isinstance(data, dict) else None
    return response.data.status if response.data else None


def vidu_video_url_extractor(response: dict) -> str:
    data = response.get("data", {})
    if isinstance(data, dict):
        return data.get("video_url", "")
    return ""
