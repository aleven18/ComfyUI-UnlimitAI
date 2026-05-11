import base64
import math
import uuid
from io import BytesIO

import numpy as np
import torch
from PIL import Image

from comfy.utils import common_upscale

from ._helpers import mimetype_to_extension


def bytesio_to_image_tensor(image_bytesio: BytesIO, mode: str = "RGB") -> torch.Tensor:
    image = Image.open(image_bytesio)
    image = image.convert(mode)
    image_array = np.array(image).astype(np.float32) / 255.0
    return torch.from_numpy(image_array).unsqueeze(0)


def image_tensor_pair_to_batch(image1: torch.Tensor, image2: torch.Tensor) -> torch.Tensor:
    if image1.shape[1:] != image2.shape[1:]:
        image2 = common_upscale(
            image2.movedim(-1, 1),
            image1.shape[2],
            image1.shape[1],
            "bilinear",
            "center",
        ).movedim(1, -1)
    return torch.cat((image1, image2), dim=0)


def tensor_to_bytesio(
    image: torch.Tensor,
    *,
    total_pixels: int | None = 2048 * 2048,
    mime_type: str | None = "image/png",
) -> BytesIO:
    if not mime_type:
        mime_type = "image/png"
    pil_image = tensor_to_pil(image, total_pixels=total_pixels)
    img_binary = pil_to_bytesio(pil_image, mime_type=mime_type)
    img_binary.name = f"{uuid.uuid4()}.{mimetype_to_extension(mime_type)}"
    return img_binary


def tensor_to_pil(image: torch.Tensor, total_pixels: int | None = 2048 * 2048) -> Image.Image:
    if len(image.shape) > 3:
        image = image[0]
    input_tensor = image.cpu()
    if total_pixels is not None:
        input_tensor = downscale_image_tensor(input_tensor.unsqueeze(0), total_pixels=total_pixels).squeeze()
    image_np = (input_tensor.numpy() * 255).astype(np.uint8)
    return Image.fromarray(image_np)


def tensor_to_base64_string(
    image_tensor: torch.Tensor,
    total_pixels: int | None = 2048 * 2048,
    mime_type: str = "image/png",
) -> str:
    pil_image = tensor_to_pil(image_tensor, total_pixels=total_pixels)
    img_byte_arr = pil_to_bytesio(pil_image, mime_type=mime_type)
    img_bytes = img_byte_arr.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")


def pil_to_bytesio(img: Image.Image, mime_type: str = "image/png") -> BytesIO:
    if not mime_type:
        mime_type = "image/png"
    img_byte_arr = BytesIO()
    pil_format = mime_type.split("/")[-1].upper()
    if pil_format == "JPG":
        pil_format = "JPEG"
    img.save(img_byte_arr, format=pil_format)
    img_byte_arr.seek(0)
    return img_byte_arr


def _compute_downscale_dims(src_w: int, src_h: int, total_pixels: int) -> tuple[int, int] | None:
    pixels = src_w * src_h
    if pixels <= total_pixels:
        return None
    scale = math.sqrt(total_pixels / pixels)
    new_w = max(2, int(src_w * scale))
    new_h = max(2, int(src_h * scale))
    new_w -= new_w % 2
    new_h -= new_h % 2
    return new_w, new_h


def downscale_image_tensor(image: torch.Tensor, total_pixels: int = 1536 * 1024) -> torch.Tensor:
    samples = image.movedim(-1, 1)
    dims = _compute_downscale_dims(samples.shape[3], samples.shape[2], int(total_pixels))
    if dims is None:
        return image
    new_w, new_h = dims
    return common_upscale(samples, new_w, new_h, "lanczos", "disabled").movedim(1, -1)


def downscale_image_tensor_by_max_side(image: torch.Tensor, *, max_side: int) -> torch.Tensor:
    samples = image.movedim(-1, 1)
    height, width = samples.shape[2], samples.shape[3]
    max_dim = max(width, height)
    if max_dim <= max_side:
        return image
    scale_by = max_side / max_dim
    new_width = round(width * scale_by)
    new_height = round(height * scale_by)
    s = common_upscale(samples, new_width, new_height, "lanczos", "disabled")
    return s.movedim(1, -1)


def tensor_to_data_uri(
    image_tensor: torch.Tensor,
    total_pixels: int | None = 2048 * 2048,
    mime_type: str = "image/png",
) -> str:
    base64_string = tensor_to_base64_string(image_tensor, total_pixels, mime_type)
    return f"data:{mime_type};base64,{base64_string}"


def _f32_pcm(wav: torch.Tensor) -> torch.Tensor:
    if wav.dtype.is_floating_point:
        return wav
    elif wav.dtype == torch.int16:
        return wav.float() / (2**15)
    elif wav.dtype == torch.int32:
        return wav.float() / (2**31)
    raise ValueError(f"Unsupported wav dtype: {wav.dtype}")


def audio_bytes_to_audio_input(audio_bytes: bytes) -> dict:
    import av

    with av.open(BytesIO(audio_bytes)) as af:
        if not af.streams.audio:
            raise ValueError("No audio stream found in response.")
        stream = af.streams.audio[0]
        in_sr = int(stream.codec_context.sample_rate)
        out_sr = in_sr
        frames: list[torch.Tensor] = []
        n_channels = stream.channels or 1
        for frame in af.decode(streams=stream.index):
            arr = frame.to_ndarray()
            buf = torch.from_numpy(arr)
            if buf.ndim == 1:
                buf = buf.unsqueeze(0)
            elif buf.shape[0] != n_channels and buf.shape[-1] == n_channels:
                buf = buf.transpose(0, 1).contiguous()
            elif buf.shape[0] != n_channels:
                buf = buf.reshape(-1, n_channels).t().contiguous()
            frames.append(buf)
    if not frames:
        raise ValueError("Decoded zero audio frames.")
    wav = torch.cat(frames, dim=1)
    wav = _f32_pcm(wav)
    return {"waveform": wav.unsqueeze(0).contiguous(), "sample_rate": out_sr}


def resize_mask_to_image(
    mask: torch.Tensor,
    image: torch.Tensor,
    upscale_method="nearest-exact",
    crop="disabled",
    allow_gradient=True,
    add_channel_dim=False,
):
    _, height, width, _ = image.shape
    mask = mask.unsqueeze(-1)
    mask = mask.movedim(-1, 1)
    mask = common_upscale(mask, width=width, height=height, upscale_method=upscale_method, crop=crop)
    mask = mask.movedim(1, -1)
    if not add_channel_dim:
        mask = mask.squeeze(-1)
    if not allow_gradient:
        mask = (mask > 0.5).float()
    return mask


def convert_mask_to_image(mask: torch.Tensor) -> torch.Tensor:
    mask = mask.unsqueeze(-1)
    return torch.cat([mask] * 3, dim=-1)
