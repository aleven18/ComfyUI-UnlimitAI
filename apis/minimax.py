from __future__ import annotations

from pydantic import BaseModel, Field


class MinimaxHailuoRequest(BaseModel):
    model: str = "T2V-01"
    prompt: str
    aspect_ratio: str = "16:9"


class MinimaxHailuoSubmitResponse(BaseModel):
    task_id: str = ""


class MinimaxHailuoPollResponse(BaseModel):
    status: str | None = None
    file_id: str | None = None
    video_url: str | None = None


def minimax_status_extractor(response: dict | MinimaxHailuoPollResponse) -> str | None:
    if isinstance(response, dict):
        status = response.get("status")
        if status:
            return status
        data = response.get("data")
        if isinstance(data, dict):
            return data.get("status")
        return None
    return response.status


class MinimaxTTSRequest(BaseModel):
    model: str = "speech-01-turbo"
    text: str = ""
    voice: str = "male-qn-jingying"
    emotion: str = "neutral"
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    format: str = "mp3"
    sample_rate: int = 32000


class MinimaxTTSResponse(BaseModel):
    audio_url: str = ""
    audio_duration_ms: int = 0
    characters: int = 0


class MinimaxTTSAsyncSubmitResponse(BaseModel):
    task_id: str = ""


class MinimaxTTSAsyncPollResponse(BaseModel):
    status: str | None = None
    audio_url: str | None = None


def minimax_tts_status_extractor(response: dict | MinimaxTTSAsyncPollResponse) -> str | None:
    if isinstance(response, dict):
        status = response.get("status")
        if status:
            return status
        data = response.get("data")
        if isinstance(data, dict):
            return data.get("status")
        return None
    return response.status


class MinimaxVoiceCloneRequest(BaseModel):
    voice_name: str = ""
    audio_url: str | None = None
    description: str | None = None


class MinimaxVoiceCloneResponse(BaseModel):
    voice_id: str = ""
    voice_name: str = ""
