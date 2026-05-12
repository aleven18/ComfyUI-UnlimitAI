from __future__ import annotations

from pydantic import BaseModel, Field


RECRAFT_V3_GENERATE = "/v1/images/generations"


class RecraftV3Request(BaseModel):
    prompt: str
    model: str = "recraftv3"
    style: str | None = None
    n: int = Field(default=1, ge=1, le=4)
    size: str = "1024x1024"
    output_format: str = "jpeg"


class RecraftImageItem(BaseModel):
    url: str = ""
    b64_json: str | None = None


class RecraftV3Response(BaseModel):
    created: int | None = None
    data: list[RecraftImageItem] = Field(default_factory=list)


def recraft_image_url_extractor(response: dict | RecraftV3Response) -> str:
    if isinstance(response, dict):
        data = response.get("data", [])
        return data[0].get("url", "") if data else ""
    if response.data:
        return response.data[0].url
    return ""
