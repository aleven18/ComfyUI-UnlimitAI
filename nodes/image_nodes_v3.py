from typing import Optional

import torch
from typing_extensions import override

from comfy_api.latest import IO, ComfyExtension

from ..unlimitai_util import (
    ApiEndpoint,
    download_url_to_image_tensor,
    poll_op,
    prepare_image_input,
    sync_op,
    validate_api_key,
    validate_string,
)
from ..apis.flux import FluxProRequest, FluxProKontextRequest, FluxProResponse
from ..apis.ideogram import IdeogramV3Request, IdeogramV3Response
from ..apis.kling import (
    KLING_IMAGE_GEN,
    KLING_IMAGE_GEN_POLL,
    KLING_MULTI_IMAGE2IMAGE,
    KLING_MULTI_IMAGE2IMAGE_POLL,
    KLING_OMNI_IMAGE,
    KLING_OMNI_IMAGE_POLL,
    KLING_IMAGE_EXPAND,
    KLING_IMAGE_EXPAND_POLL,
    KLING_VIRTUAL_TRY_ON,
    KLING_VIRTUAL_TRY_ON_POLL,
    KlingImageGenRequest,
    KlingMultiImage2ImageRequest,
    KlingOmniImageRequest,
    KlingImageExpandRequest,
    KlingVirtualTryOnRequest,
    KlingSubmitResponse,
    KlingPollResponse,
    kling_status_extractor,
)
from ..apis.openai import GPTImageRequest, GPTImageResponse
from ..apis.imagen import Imagen4Request, Imagen4SubmitResponse, Imagen4PollResponse, imagen_status_extractor
from ..apis.recraft import RecraftV3Request, RecraftV3Response


async def _kling_submit_poll_image(cls, submit_path: str, poll_path: str,
                                    request, api_key: str,
                                    wait_label: str = "Submitting",
                                    poll_interval: float = 3.0,
                                    max_poll_attempts: int = 200,
                                    estimated_duration: int = 60) -> tuple:
    submit_response: KlingSubmitResponse = await sync_op(
        cls, endpoint=ApiEndpoint(path=submit_path, method="POST"),
        data=request, response_model=KlingSubmitResponse, api_key=api_key,
        wait_label=wait_label, estimated_duration=5,
    )
    task_id = submit_response.data.task_id
    if not task_id:
        raise Exception(f"Kling image submit failed: no task_id. Response: {submit_response}")
    poll_response: KlingPollResponse = await poll_op(
        cls, poll_endpoint=ApiEndpoint(path=poll_path.format(task_id), method="GET"),
        response_model=KlingPollResponse, status_extractor=kling_status_extractor,
        api_key=api_key, completed_statuses=["succeed"], failed_statuses=["failed"],
        queued_statuses=["submitted", "processing"], poll_interval=poll_interval,
        max_poll_attempts=max_poll_attempts, estimated_duration=estimated_duration,
    )
    img_url = ""
    if poll_response.data and poll_response.data.task_result and poll_response.data.task_result.images:
        img_url = poll_response.data.task_result.images[0].url
    if not img_url:
        raise Exception("Kling image task completed but no image URL found.")
    image_tensor = await download_url_to_image_tensor(img_url, cls=cls)
    return image_tensor, img_url


class FluxProV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="FluxProV3Node",
            display_name="FLUX Pro [V3]",
            category="api node/image/FLUX",
            description="FLUX Pro image generation via UnlimitAI — synchronous, fast, high quality.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt for image generation."),
                IO.Combo.Input("image_size", options=["square_hd", "square", "portrait_4_3", "portrait_16_9", "landscape_4_3", "landscape_16_9"], default="landscape_16_9"),
                IO.Int.Input("num_inference_steps", default=30, min=1, max=50, step=1),
                IO.Int.Input("seed", default=0, min=0, max=999999999, step=1, control_after_generate=True),
                IO.Float.Input("guidance_scale", default=3.5, min=0.0, max=35.0, step=0.1),
                IO.Int.Input("num_images", default=1, min=1, max=4, step=1),
                IO.Boolean.Input("enable_safety_checker", default=True),
                IO.Combo.Input("output_format", options=["jpeg", "png"], default="jpeg"),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image_size: str = "landscape_16_9", num_inference_steps: int = 30, seed: int = 0, guidance_scale: float = 3.5, num_images: int = 1, enable_safety_checker: bool = True, output_format: str = "jpeg"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = FluxProRequest(prompt=prompt, image_size=image_size, num_inference_steps=num_inference_steps, seed=seed, guidance_scale=guidance_scale, num_images=num_images, enable_safety_checker=enable_safety_checker, output_format=output_format, sync=True)
        response: FluxProResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/fal-ai/flux-pro", method="POST"), data=request, response_model=FluxProResponse, api_key=key, wait_label="Generating image", estimated_duration=15)
        image_url = response.images[0].url if response.images else ""
        image_tensor = await download_url_to_image_tensor(image_url, cls=cls) if image_url else torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        return IO.NodeOutput(image_tensor, image_url)


class FluxProKontextV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="FluxProKontextV3Node",
            display_name="FLUX Pro Kontext [V3]",
            category="api node/image/FLUX",
            description="FLUX Pro Kontext image editing via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Edit prompt."),
                IO.Image.Input("image", optional=True, tooltip="Input image to edit."),
                IO.String.Input("image_url", default="", multiline=False, tooltip="Or provide an image URL.", optional=True),
                IO.Int.Input("num_inference_steps", default=30, min=1, max=50, step=1),
                IO.Int.Input("seed", default=0, min=0, max=999999999, step=1, control_after_generate=True),
                IO.Float.Input("guidance_scale", default=3.5, min=0.0, max=35.0, step=0.1),
                IO.Int.Input("num_images", default=1, min=1, max=4, step=1),
                IO.Boolean.Input("enable_safety_checker", default=True),
                IO.Combo.Input("output_format", options=["jpeg", "png"], default="jpeg"),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image: Optional[torch.Tensor] = None, image_url: str = "", num_inference_steps: int = 30, seed: int = 0, guidance_scale: float = 3.5, num_images: int = 1, enable_safety_checker: bool = True, output_format: str = "jpeg"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        resolved_image = prepare_image_input(image=image, image_url=image_url)
        request = FluxProKontextRequest(prompt=prompt, image_url=resolved_image if resolved_image and resolved_image.startswith("http") else None, image=resolved_image if resolved_image and resolved_image.startswith("data:") else None, num_inference_steps=num_inference_steps, seed=seed, guidance_scale=guidance_scale, num_images=num_images, enable_safety_checker=enable_safety_checker, output_format=output_format, sync=True)
        response: FluxProResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/fal-ai/flux-pro/kontext", method="POST"), data=request, response_model=FluxProResponse, api_key=key, wait_label="Editing image", estimated_duration=20)
        img_url = response.images[0].url if response.images else ""
        image_tensor = await download_url_to_image_tensor(img_url, cls=cls) if img_url else torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        return IO.NodeOutput(image_tensor, img_url)


class IdeogramV3V3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="IdeogramV3V3Node",
            display_name="Ideogram V3 [V3]",
            category="api node/image/Ideogram",
            description="Ideogram V3 image generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("aspect_ratio", options=["ASPECT_1_1", "ASPECT_16_9", "ASPECT_9_16", "ASPECT_4_3", "ASPECT_3_4"], default="ASPECT_16_9"),
                IO.Combo.Input("style_type", options=["AUTO", "GENERAL", "REALISTIC", "DESIGN"], default="AUTO"),
                IO.Int.Input("seed", default=0, min=0, max=2147483647, step=1, control_after_generate=True, optional=True),
                IO.Combo.Input("output_format", options=["jpeg", "png", "webp"], default="jpeg"),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", aspect_ratio: str = "ASPECT_16_9", style_type: str = "AUTO", seed: int = 0, output_format: str = "jpeg"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = IdeogramV3Request(prompt=prompt, aspect_ratio=aspect_ratio, style_type=style_type, seed=seed if seed != 0 else None, output_format=output_format)
        response: IdeogramV3Response = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/ideogram/generate", method="POST"), data=request, response_model=IdeogramV3Response, api_key=key, wait_label="Generating image", estimated_duration=12)
        img_url = response.data[0].url if response.data else ""
        image_tensor = await download_url_to_image_tensor(img_url, cls=cls) if img_url else torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        return IO.NodeOutput(image_tensor, img_url)


class KlingImageGenV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingImageGenV3Node",
            display_name="Kling Image Gen [V3]",
            category="api node/image/Kling",
            description="Kling image generation via UnlimitAI. Supports character consistency with subject/face reference.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.String.Input("negative_prompt", multiline=True, default="", optional=True, tooltip="Negative prompt."),
                IO.Combo.Input("model_name", options=["kling-v1", "kling-v1-5", "kling-v2", "kling-v2-new", "kling-v2-1", "kling-v3"], default="kling-v2"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9"], default="16:9"),
                IO.Int.Input("n", default=1, min=1, max=9, step=1),
                IO.Image.Input("ref_image", optional=True, tooltip="Reference image for character consistency."),
                IO.String.Input("ref_image_url", default="", multiline=False, optional=True, tooltip="Or provide a reference image URL."),
                IO.Combo.Input("image_reference", options=["none", "subject", "face"], default="none", tooltip="Subject: keep character appearance. Face: keep facial features only."),
                IO.Float.Input("image_fidelity", default=0.5, min=0.0, max=1.0, step=0.01, tooltip="Reference image intensity."),
                IO.Float.Input("human_fidelity", default=0.45, min=0.0, max=1.0, step=0.01, tooltip="Subject similarity strength."),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", negative_prompt: str = "", model_name: str = "kling-v2", aspect_ratio: str = "16:9", n: int = 1, ref_image=None, ref_image_url: str = "", image_reference: str = "none", image_fidelity: float = 0.5, human_fidelity: float = 0.45):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        resolved_ref = prepare_image_input(image=ref_image, image_url=ref_image_url)
        has_ref = image_reference != "none" and resolved_ref
        request = KlingImageGenRequest(
            model_name=model_name, prompt=prompt, aspect_ratio=aspect_ratio, n=n,
            negative_prompt=negative_prompt or None,
            image=resolved_ref if has_ref else None,
            image_reference=image_reference if has_ref else None,
            image_fidelity=image_fidelity if has_ref else None,
            human_fidelity=human_fidelity if has_ref else None,
        )
        image_tensor, img_url = await _kling_submit_poll_image(
            cls, KLING_IMAGE_GEN, KLING_IMAGE_GEN_POLL, request, key)
        return IO.NodeOutput(image_tensor, img_url)


class KlingMultiImage2ImageV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingMultiImage2ImageV3Node",
            display_name="Kling Multi-Image to Image [V3]",
            category="api node/image/Kling",
            description="Kling multi-image reference image generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.String.Input("subject_image_urls", default="", multiline=True, tooltip="Subject image URLs, one per line (1-4 images)."),
                IO.String.Input("scene_image_url", default="", multiline=False, optional=True, tooltip="Scene reference image URL."),
                IO.String.Input("style_image_url", default="", multiline=False, optional=True, tooltip="Style reference image URL."),
                IO.Combo.Input("model_name", options=["kling-v2", "kling-v2-1"], default="kling-v2"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9"], default="16:9"),
                IO.Int.Input("n", default=1, min=1, max=9, step=1),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", subject_image_urls: str = "", scene_image_url: str = "", style_image_url: str = "", model_name: str = "kling-v2", aspect_ratio: str = "16:9", n: int = 1):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        urls = [u.strip() for u in subject_image_urls.strip().split("\n") if u.strip()]
        if not urls:
            raise Exception("At least one subject image URL is required.")
        request = KlingMultiImage2ImageRequest(
            model_name=model_name, prompt=prompt,
            subject_image_list=[{"subject_image": u} for u in urls[:4]],
            scene_image=scene_image_url or None, style_image=style_image_url or None,
            n=n, aspect_ratio=aspect_ratio,
        )
        image_tensor, img_url = await _kling_submit_poll_image(
            cls, KLING_MULTI_IMAGE2IMAGE, KLING_MULTI_IMAGE2IMAGE_POLL, request, key)
        return IO.NodeOutput(image_tensor, img_url)


class KlingOmniImageV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingOmniImageV3Node",
            display_name="Kling Omni-Image [V3]",
            category="api node/image/Kling",
            description="Kling Omni-Image generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.String.Input("image_urls", default="", multiline=True, optional=True, tooltip="Reference image URLs, one per line."),
                IO.Combo.Input("model_name", options=["kling-image-o1", "kling-v3-omni"], default="kling-image-o1"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9", "auto"], default="16:9"),
                IO.Int.Input("n", default=1, min=1, max=9, step=1),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image_urls: str = "", model_name: str = "kling-image-o1", aspect_ratio: str = "16:9", n: int = 1):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        urls = [u.strip() for u in image_urls.strip().split("\n") if u.strip()] if image_urls else None
        resolved_ratio = None if aspect_ratio == "auto" else aspect_ratio
        request = KlingOmniImageRequest(
            model_name=model_name, prompt=prompt,
            image_list=[{"image": u} for u in urls] if urls else None,
            aspect_ratio=resolved_ratio, n=n,
        )
        image_tensor, img_url = await _kling_submit_poll_image(
            cls, KLING_OMNI_IMAGE, KLING_OMNI_IMAGE_POLL, request, key)
        return IO.NodeOutput(image_tensor, img_url)


class KlingImageExpandV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingImageExpandV3Node",
            display_name="Kling Image Expand [V3]",
            category="api node/image/Kling",
            description="Expand image boundaries via UnlimitAI using Kling.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.Image.Input("image", optional=True, tooltip="Input image to expand."),
                IO.String.Input("image_url", default="", multiline=False, optional=True, tooltip="Or provide an image URL."),
                IO.Float.Input("up_expansion_ratio", default=0.0, min=0.0, max=1.0, step=0.05, tooltip="Upward expansion ratio."),
                IO.Float.Input("down_expansion_ratio", default=0.0, min=0.0, max=1.0, step=0.05, tooltip="Downward expansion ratio."),
                IO.Float.Input("left_expansion_ratio", default=0.0, min=0.0, max=1.0, step=0.05, tooltip="Left expansion ratio."),
                IO.Float.Input("right_expansion_ratio", default=0.0, min=0.0, max=1.0, step=0.05, tooltip="Right expansion ratio."),
                IO.String.Input("prompt", multiline=True, default="", optional=True, tooltip="Optional prompt to guide expansion."),
                IO.Int.Input("n", default=1, min=1, max=9, step=1),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", image=None, image_url: str = "", up_expansion_ratio: float = 0.0, down_expansion_ratio: float = 0.0, left_expansion_ratio: float = 0.0, right_expansion_ratio: float = 0.0, prompt: str = "", n: int = 1):
        key = validate_api_key(api_key)
        resolved_image = prepare_image_input(image=image, image_url=image_url)
        if not resolved_image:
            raise Exception("An input image is required.")
        if all(r == 0.0 for r in [up_expansion_ratio, down_expansion_ratio, left_expansion_ratio, right_expansion_ratio]):
            raise Exception("At least one expansion ratio must be greater than 0.")
        request = KlingImageExpandRequest(
            image=resolved_image,
            up_expansion_ratio=up_expansion_ratio,
            down_expansion_ratio=down_expansion_ratio,
            left_expansion_ratio=left_expansion_ratio,
            right_expansion_ratio=right_expansion_ratio,
            prompt=prompt or None,
            n=n,
        )
        image_tensor, img_url = await _kling_submit_poll_image(
            cls, KLING_IMAGE_EXPAND, KLING_IMAGE_EXPAND_POLL, request, key)
        return IO.NodeOutput(image_tensor, img_url)


class KlingVirtualTryOnV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingVirtualTryOnV3Node",
            display_name="Kling Virtual Try-On [V3]",
            category="api node/image/Kling",
            description="Virtual try-on: place clothing from one image onto a person in another image.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.Image.Input("human_image", optional=True, tooltip="Image of the person."),
                IO.String.Input("human_image_url", default="", multiline=False, optional=True, tooltip="Or provide a person image URL."),
                IO.Image.Input("cloth_image", optional=True, tooltip="Image of the clothing item."),
                IO.String.Input("cloth_image_url", default="", multiline=False, optional=True, tooltip="Or provide a clothing image URL."),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", human_image=None, human_image_url: str = "", cloth_image=None, cloth_image_url: str = ""):
        key = validate_api_key(api_key)
        resolved_human = prepare_image_input(image=human_image, image_url=human_image_url)
        resolved_cloth = prepare_image_input(image=cloth_image, image_url=cloth_image_url)
        if not resolved_human:
            raise Exception("A human image is required.")
        if not resolved_cloth:
            raise Exception("A cloth image is required.")
        request = KlingVirtualTryOnRequest(
            human_image=resolved_human,
            cloth_image=resolved_cloth,
        )
        image_tensor, img_url = await _kling_submit_poll_image(
            cls, KLING_VIRTUAL_TRY_ON, KLING_VIRTUAL_TRY_ON_POLL, request, key,
            estimated_duration=45)
        return IO.NodeOutput(image_tensor, img_url)


class GPTImageV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="GPTImageV3Node",
            display_name="GPT Image [V3]",
            category="api node/image/OpenAI",
            description="GPT Image generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("size", options=["1024x1024", "1536x1024", "1024x1536"], default="1024x1024"),
                IO.Combo.Input("quality", options=["auto", "high", "medium", "low"], default="auto"),
                IO.Combo.Input("output_format", options=["png", "jpeg", "webp"], default="png"),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", size: str = "1024x1024", quality: str = "auto", output_format: str = "png"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = GPTImageRequest(prompt=prompt, size=size, quality=quality, output_format=output_format)
        response: GPTImageResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/images/generations", method="POST"), data=request, response_model=GPTImageResponse, api_key=key, wait_label="Generating image", estimated_duration=20)
        img_url = ""
        if response.data:
            img_url = response.data[0].url or ""
        image_tensor = await download_url_to_image_tensor(img_url, cls=cls) if img_url else torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        return IO.NodeOutput(image_tensor, img_url)


class Imagen4V3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="Imagen4V3Node",
            display_name="Imagen 4 [V3]",
            category="api node/image/Google",
            description="Google Imagen 4 image generation via UnlimitAI — polling based.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("model", options=["imagen-4.0-generate-001", "imagen-4.0-fast-generate-001"], default="imagen-4.0-generate-001"),
                IO.Combo.Input("aspect_ratio", options=["1:1", "16:9", "9:16", "4:3", "3:4"], default="1:1"),
                IO.Combo.Input("output_format", options=["png", "jpeg"], default="png"),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", model: str = "imagen-4.0-generate-001", aspect_ratio: str = "1:1", output_format: str = "png"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = Imagen4Request(prompt=prompt, aspect_ratio=aspect_ratio, output_format=output_format)
        submit_response: Imagen4SubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path=f"/replicate/v1/models/google/{model}/predictions", method="POST"), data=request, response_model=Imagen4SubmitResponse, api_key=key, wait_label="Submitting Imagen task", estimated_duration=5)
        poll_url = ""
        if submit_response.urls and isinstance(submit_response.urls, dict):
            poll_url = submit_response.urls.get("get", "")
        if not poll_url:
            raise Exception(f"Imagen submit failed: no poll URL. Response: {submit_response}")
        poll_response: Imagen4PollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=poll_url, method="GET"), response_model=Imagen4PollResponse, status_extractor=imagen_status_extractor, api_key=key, completed_statuses=["succeeded"], failed_statuses=["failed", "canceled"], queued_statuses=["starting", "processing"], poll_interval=2.0, max_poll_attempts=300, estimated_duration=30)
        img_url = ""
        if poll_response.output:
            img_url = poll_response.output[0].url if hasattr(poll_response.output[0], "url") else str(poll_response.output[0])
        image_tensor = await download_url_to_image_tensor(img_url, cls=cls) if img_url else torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        return IO.NodeOutput(image_tensor, img_url)


class RecraftV3V3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="RecraftV3V3Node",
            display_name="Recraft V3 [V3]",
            category="api node/image/Recraft",
            description="Recraft V3 image generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("model", options=["recraftv3"], default="recraftv3"),
                IO.Combo.Input("size", options=["1024x1024", "1536x1024", "1024x1536", "1365x1024", "1024x1365"], default="1024x1024"),
                IO.Combo.Input("output_format", options=["jpeg", "png", "webp"], default="jpeg"),
            ],
            outputs=[IO.Image.Output("image"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", model: str = "recraftv3", size: str = "1024x1024", output_format: str = "jpeg"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = RecraftV3Request(prompt=prompt, model=model, size=size, output_format=output_format)
        response: RecraftV3Response = await sync_op(cls, endpoint=ApiEndpoint(path=f"/fal-ai/{model}", method="POST"), data=request, response_model=RecraftV3Response, api_key=key, wait_label="Generating image", estimated_duration=15)
        img_url = response.data[0].url if response.data else ""
        image_tensor = await download_url_to_image_tensor(img_url, cls=cls) if img_url else torch.zeros(1, 64, 64, 3, dtype=torch.float32)
        return IO.NodeOutput(image_tensor, img_url)


class UnlimitAIImageV3Extension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        return [
            FluxProV3Node, FluxProKontextV3Node, IdeogramV3V3Node,
            KlingImageGenV3Node, KlingMultiImage2ImageV3Node, KlingOmniImageV3Node,
            KlingImageExpandV3Node, KlingVirtualTryOnV3Node,
            GPTImageV3Node, Imagen4V3Node, RecraftV3V3Node,
        ]


async def comfy_entrypoint() -> UnlimitAIImageV3Extension:
    return UnlimitAIImageV3Extension()
