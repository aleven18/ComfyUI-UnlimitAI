from __future__ import annotations

from pydantic import BaseModel, Field


class RunwayGen4Request(BaseModel):
    prompt: str
    model: str = "gen4_turbo"
    ratio: str = "16:9"
    duration: int = 5
    image_url: str | None = None


class RunwaySubmitResponse(BaseModel):
    id: str = ""
    status_url: str | None = None


class RunwayPollResponse(BaseModel):
    id: str = ""
    status: str | None = None
    status_url: str | None = None
    output: list[str] | None = None


def runway_status_extractor(response: dict | RunwayPollResponse) -> str | None:
    if isinstance(response, dict):
        return response.get("status")
    return response.status
