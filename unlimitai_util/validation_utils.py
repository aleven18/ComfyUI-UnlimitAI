import logging

import torch

from comfy_api.latest import Input

from .common_exceptions import ValidationError


def validate_api_key(api_key: str | None) -> str:
    if not api_key or not api_key.strip():
        raise ValidationError("API key is required. Please provide a valid UnlimitAI API key.")
    stripped = api_key.strip()
    if len(stripped) < 8:
        raise ValidationError("API key appears too short. Please check your UnlimitAI API key.")
    return stripped


def validate_string(
    string: str | None,
    field_name: str = "prompt",
    *,
    strip_whitespace: bool = True,
    min_length: int | None = None,
    max_length: int | None = None,
) -> str:
    if string is None:
        raise ValidationError(f"Field '{field_name}' cannot be empty.")
    if strip_whitespace:
        string = string.strip()
    if not string:
        raise ValidationError(f"Field '{field_name}' cannot be empty.")
    if min_length and len(string) < min_length:
        raise ValidationError(
            f"Field '{field_name}' cannot be shorter than {min_length} characters; was {len(string)} characters long."
        )
    if max_length and len(string) > max_length:
        raise ValidationError(
            f"Field '{field_name}' cannot be longer than {max_length} characters; was {len(string)} characters long."
        )
    return string


def get_image_dimensions(image: torch.Tensor) -> tuple[int, int]:
    if len(image.shape) == 4:
        return image.shape[1], image.shape[2]
    elif len(image.shape) == 3:
        return image.shape[0], image.shape[1]
    else:
        raise ValueError("Invalid image tensor shape.")


def validate_image_dimensions(
    image: torch.Tensor,
    min_width: int | None = None,
    max_width: int | None = None,
    min_height: int | None = None,
    max_height: int | None = None,
):
    height, width = get_image_dimensions(image)
    if min_width is not None and width < min_width:
        raise ValidationError(f"Image width must be at least {min_width}px, got {width}px")
    if max_width is not None and width > max_width:
        raise ValidationError(f"Image width must be at most {max_width}px, got {width}px")
    if min_height is not None and height < min_height:
        raise ValidationError(f"Image height must be at least {min_height}px, got {height}px")
    if max_height is not None and height > max_height:
        raise ValidationError(f"Image height must be at most {max_height}px, got {height}px")


def validate_image_aspect_ratio(
    image: torch.Tensor,
    min_ratio: tuple[float, float] | None = None,
    max_ratio: tuple[float, float] | None = None,
    *,
    strict: bool = True,
) -> float:
    w, h = get_image_dimensions(image)
    if w <= 0 or h <= 0:
        raise ValidationError(f"Invalid image dimensions: {w}x{h}")
    ar = w / h
    _assert_ratio_bounds(ar, min_ratio=min_ratio, max_ratio=max_ratio, strict=strict)
    return ar


def validate_aspect_ratio_string(
    aspect_ratio: str,
    min_ratio: tuple[float, float] | None = None,
    max_ratio: tuple[float, float] | None = None,
    *,
    strict: bool = False,
) -> float:
    ar = _parse_aspect_ratio_string(aspect_ratio)
    _assert_ratio_bounds(ar, min_ratio=min_ratio, max_ratio=max_ratio, strict=strict)
    return ar


def validate_video_dimensions(
    video: Input.Video,
    min_width: int | None = None,
    max_width: int | None = None,
    min_height: int | None = None,
    max_height: int | None = None,
):
    try:
        width, height = video.get_dimensions()
    except Exception as e:
        logging.error("Error getting dimensions of video: %s", e)
        return
    if min_width is not None and width < min_width:
        raise ValidationError(f"Video width must be at least {min_width}px, got {width}px")
    if max_width is not None and width > max_width:
        raise ValidationError(f"Video width must be at most {max_width}px, got {width}px")
    if min_height is not None and height < min_height:
        raise ValidationError(f"Video height must be at least {min_height}px, got {height}px")
    if max_height is not None and height > max_height:
        raise ValidationError(f"Video height must be at most {max_height}px, got {height}px")


def validate_video_duration(
    video: Input.Video,
    min_duration: float | None = None,
    max_duration: float | None = None,
):
    try:
        duration = video.get_duration()
    except Exception as e:
        logging.error("Error getting duration of video: %s", e)
        return
    epsilon = 0.0001
    if min_duration is not None and min_duration - epsilon > duration:
        raise ValidationError(f"Video duration must be at least {min_duration}s, got {duration}s")
    if max_duration is not None and duration > max_duration + epsilon:
        raise ValidationError(f"Video duration must be at most {max_duration}s, got {duration}s")


def validate_audio_duration(
    audio: Input.Audio,
    min_duration: float | None = None,
    max_duration: float | None = None,
) -> None:
    sr = int(audio["sample_rate"])
    dur = int(audio["waveform"].shape[-1]) / sr
    eps = 1.0 / sr
    if min_duration is not None and dur + eps < min_duration:
        raise ValidationError(f"Audio duration must be at least {min_duration}s, got {dur + eps:.2f}s")
    if max_duration is not None and dur - eps > max_duration:
        raise ValidationError(f"Audio duration must be at most {max_duration}s, got {dur - eps:.2f}s")


def get_number_of_images(images):
    if isinstance(images, torch.Tensor):
        return images.shape[0] if images.ndim >= 4 else 1
    return len(images)


def _ratio_from_tuple(r: tuple[float, float]) -> float:
    a, b = r
    if a <= 0 or b <= 0:
        raise ValueError(f"Ratios must be positive, got {a}:{b}.")
    return a / b


def _assert_ratio_bounds(
    ar: float,
    *,
    min_ratio: tuple[float, float] | None = None,
    max_ratio: tuple[float, float] | None = None,
    strict: bool = True,
) -> None:
    lo = _ratio_from_tuple(min_ratio) if min_ratio is not None else None
    hi = _ratio_from_tuple(max_ratio) if max_ratio is not None else None
    if lo is not None and hi is not None and lo > hi:
        lo, hi = hi, lo
    if lo is not None:
        if (ar <= lo) if strict else (ar < lo):
            op = "<" if strict else "≤"
            raise ValidationError(f"Aspect ratio `{ar:.2g}` must be {op} {lo:.2g}.")
    if hi is not None:
        if (ar >= hi) if strict else (ar > hi):
            op = "<" if strict else "≤"
            raise ValidationError(f"Aspect ratio `{ar:.2g}` must be {op} {hi:.2g}.")


def _parse_aspect_ratio_string(ar_str: str) -> float:
    parts = ar_str.split(":")
    if len(parts) != 2:
        raise ValueError(f"Aspect ratio must be 'X:Y' (e.g., 16:9), got '{ar_str}'.")
    try:
        a = int(parts[0].strip())
        b = int(parts[1].strip())
    except ValueError as exc:
        raise ValueError(f"Aspect ratio must contain integers separated by ':', got '{ar_str}'.") from exc
    if a <= 0 or b <= 0:
        raise ValueError(f"Aspect ratio parts must be positive integers, got {a}:{b}.")
    return a / b
