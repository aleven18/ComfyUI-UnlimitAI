from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="allow")
    role: str = "user"
    content: str | list[dict] = ""
    reasoning_content: str | None = None


def extract_text_content(content: str | list[dict]) -> str:
    if isinstance(content, list):
        return " ".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
    return content


class TextGenerationRequest(BaseModel):
    model: str = "gpt-4o"
    messages: list[ChatMessage] = Field(default_factory=list)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = None
    response_format: dict | None = None


class TextChoice(BaseModel):
    index: int = 0
    message: ChatMessage = Field(default_factory=ChatMessage)
    finish_reason: str | None = None


class TextUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class TextGenerationResponse(BaseModel):
    id: str | None = None
    model: str | None = None
    choices: list[TextChoice] = Field(default_factory=list)
    usage: TextUsage = Field(default_factory=TextUsage)
