from __future__ import annotations

from pydantic import BaseModel, Field


class SunoInspirationRequest(BaseModel):
    prompt: str
    tags: str = ""
    title: str = ""
    make_instrumental: bool = False
    model: str = "chirp-v3-5"
    mv: str = "chirp-v3-5"


class SunoCustomModeRequest(BaseModel):
    prompt: str
    tags: str = ""
    title: str = ""
    make_instrumental: bool = False
    model: str = "chirp-v3-5"
    mv: str = "chirp-v3-5"
    lyrics: str = ""


class SunoLyricsRequest(BaseModel):
    prompt: str


class SunoExtendRequest(BaseModel):
    audio_url: str | None = None
    prompt: str = ""
    title: str = ""
    tags: str = ""
    continue_at: float = 0.0
    model: str = "chirp-v3-5"
    mv: str = "chirp-v3-5"


class SunoTrackData(BaseModel):
    id: str = ""
    title: str = ""
    audio_url: str = ""
    image_url: str = ""
    status: str = ""
    model: str | None = None


class SunoSubmitResponse(BaseModel):
    clips: list[SunoTrackData] = Field(default_factory=list)


class SunoPollResponse(BaseModel):
    clips: list[SunoTrackData] = Field(default_factory=list)


def suno_status_extractor(response: dict | SunoPollResponse) -> str | None:
    if isinstance(response, dict):
        clips = response.get("clips", [])
        if clips and isinstance(clips, list):
            return clips[0].get("status") if isinstance(clips[0], dict) else None
        return None
    if response.clips:
        return response.clips[0].status
    return None


def suno_audio_url_extractor(response: dict) -> str:
    clips = response.get("clips", [])
    if clips and isinstance(clips, list):
        return clips[0].get("audio_url", "") if isinstance(clips[0], dict) else ""
    return ""
