from __future__ import annotations

import logging
from io import BytesIO

import torch

from comfy_api.latest import IO, Input

from .conversions import (
    audio_bytes_to_audio_input,
    tensor_to_data_uri,
    tensor_to_pil,
)

logger = logging.getLogger(__name__)


def prepare_image_input(
    image: torch.Tensor | None = None,
    image_url: str | None = None,
    *,
    total_pixels: int | None = 2048 * 2048,
    mime_type: str = "image/png",
) -> str | None:
    """Resolve an image input to a string the UnlimitAI gateway can consume.

    Priority:
      1. If *image_url* is provided and looks like a URL, return it as-is.
      2. If *image* tensor is provided, encode it as a base64 data-URI.
      3. Return ``None`` when neither is supplied.
    """
    if image_url:
        stripped = image_url.strip()
        if stripped.startswith(("http://", "https://", "data:")):
            return stripped
    if image is not None:
        return tensor_to_data_uri(image, total_pixels=total_pixels, mime_type=mime_type)
    return None


def prepare_image_inputs(
    images: list[torch.Tensor] | torch.Tensor | None = None,
    image_urls: list[str] | str | None = None,
    *,
    total_pixels: int | None = 2048 * 2048,
    mime_type: str = "image/png",
) -> list[str]:
    """Batch version of :func:`prepare_image_input`.

    Accepts a batched tensor ``[B, H, W, C]``, a list of tensors, or
    a list of URL strings. Returns a list of data-URI / URL strings.
    """
    results: list[str] = []
    if image_urls is not None:
        url_list = [image_urls] if isinstance(image_urls, str) else image_urls
        for u in url_list:
            resolved = prepare_image_input(image_url=u)
            if resolved is not None:
                results.append(resolved)
    if images is not None:
        if isinstance(images, torch.Tensor):
            if images.ndim == 4:
                for i in range(images.shape[0]):
                    results.append(tensor_to_data_uri(images[i], total_pixels=total_pixels, mime_type=mime_type))
            else:
                results.append(tensor_to_data_uri(images, total_pixels=total_pixels, mime_type=mime_type))
        elif isinstance(images, list):
            for img in images:
                results.append(tensor_to_data_uri(img, total_pixels=total_pixels, mime_type=mime_type))
    return results


def prepare_video_input(
    video: Input.Video | None = None,
    video_url: str | None = None,
) -> str | None:
    """Resolve a video input for the UnlimitAI gateway.

    The gateway does not accept raw video uploads — it only takes URLs.
    If the caller supplies a ``video_url``, return it as-is.
    A Comfy ``VIDEO`` input is currently not uploadable directly (no
    presigned endpoint), so we log a warning and return ``None``.
    """
    if video_url:
        stripped = video_url.strip()
        if stripped.startswith(("http://", "https://")):
            return stripped
    if video is not None:
        logger.warning(
            "UnlimitAI gateway has no video upload endpoint. "
            "Please pass a video_url instead of a VIDEO input."
        )
    return None


def prepare_audio_input(
    audio: Input.Audio | None = None,
    audio_url: str | None = None,
) -> str | None:
    """Resolve an audio input for the UnlimitAI gateway.

    Similar to video — only URLs are accepted by the gateway.
    """
    if audio_url:
        stripped = audio_url.strip()
        if stripped.startswith(("http://", "https://")):
            return stripped
    if audio is not None:
        logger.warning(
            "UnlimitAI gateway has no audio upload endpoint. "
            "Please pass an audio_url instead of an AUDIO input."
        )
    return None
