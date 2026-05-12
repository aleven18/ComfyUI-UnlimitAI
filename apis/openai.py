from __future__ import annotations

from pydantic import BaseModel, Field


OPENAI_IMAGE_GENERATIONS = "/v1/images/generations"
OPENAI_TTS = "/v1/audio/speech"
OPENAI_WHISPER = "/v1/audio/transcriptions"
OPENAI_CHAT_COMPLETIONS = "/v1/chat/completions"


class GPTImageRequest(BaseModel):
    prompt: str
    model: str = "gpt-image-1"
    n: int = Field(default=1, ge=1, le=4)
    size: str = "1024x1024"
    quality: str = "auto"
    output_format: str = "png"


class GPTImageItem(BaseModel):
    url: str | None = None
    b64_json: str | None = None
    revised_prompt: str | None = None


class GPTImageResponse(BaseModel):
    created: int | None = None
    data: list[GPTImageItem] = Field(default_factory=list)


class OpenAITTSRequest(BaseModel):
    model: str = "tts-1"
    input: str = ""
    voice: str = "alloy"
    response_format: str = "mp3"
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


class OpenAIWhisperRequest(BaseModel):
    model: str = "whisper-1"
    file: str | None = None
    language: str | None = None
    response_format: str = "verbose_json"


class OpenAIWhisperResponse(BaseModel):
    text: str = ""
    language: str | None = None
    duration: float | None = None
    segments: list[dict] | None = None


class ChatCompletionMessage(BaseModel):
    role: str = "user"
    content: str = ""


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o"
    messages: list[ChatCompletionMessage] = Field(default_factory=list)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = None
    response_format: dict | None = None
    stream: bool = False


class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: ChatCompletionMessage = Field(default_factory=ChatCompletionMessage)
    finish_reason: str | None = None


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    id: str | None = None
    model: str | None = None
    choices: list[ChatCompletionChoice] = Field(default_factory=list)
    usage: UsageInfo = Field(default_factory=UsageInfo)


def openai_image_url_extractor(response: dict | GPTImageResponse) -> str:
    if isinstance(response, dict):
        data = response.get("data", [])
        return data[0].get("url", "") if data else ""
    if response.data:
        return response.data[0].url or ""
    return ""
