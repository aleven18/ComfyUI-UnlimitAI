import os
import asyncio
import time

from comfy.model_management import processing_interrupted
from comfy_api.latest import IO

from .common_exceptions import ProcessingInterrupted


def default_base_url() -> str:
    return os.environ.get("UNLIMITAI_BASE_URL", "https://api.unlimitai.org")


def get_auth_header(api_key: str) -> dict[str, str]:
    if api_key:
        return {"Authorization": f"Bearer {api_key}"}
    return {}


def is_processing_interrupted() -> bool:
    return processing_interrupted()


def get_node_id(node_cls: type[IO.ComfyNode]) -> str:
    return node_cls.hidden.unique_id


async def sleep_with_interrupt(
    seconds: float,
    node_cls: type[IO.ComfyNode] | None = None,
    label: str | None = None,
    start_ts: float | None = None,
    estimated_total: int | None = None,
):
    end = time.monotonic() + seconds
    while True:
        if is_processing_interrupted():
            raise ProcessingInterrupted("Task cancelled")
        now = time.monotonic()
        if now >= end:
            break
        await asyncio.sleep(min(1.0, end - now))


def mimetype_to_extension(mime_type: str) -> str:
    return mime_type.split("/")[-1].lower()
