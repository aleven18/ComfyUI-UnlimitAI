import json
import logging
import math

from typing_extensions import override

from comfy_api.latest import IO, ComfyExtension

from ..unlimitai_util import (
    ApiEndpoint,
    download_url_to_video_output,
    poll_op,
    prepare_image_input,
    sync_op,
    sync_op_raw,
    validate_api_key,
    validate_string,
)
from ..apis.kling import (
    KLING_TEXT2VIDEO,
    KLING_TEXT2VIDEO_POLL,
    KLING_IMAGE2VIDEO,
    KLING_IMAGE2VIDEO_POLL,
    KLING_OMNI_VIDEO,
    KLING_OMNI_VIDEO_POLL,
    KLING_MULTI_IMAGE2VIDEO,
    KLING_MULTI_IMAGE2VIDEO_POLL,
    KLING_MULTI_ELEMENTS_INIT,
    KLING_MULTI_ELEMENTS_ADD,
    KLING_MULTI_ELEMENTS_PREVIEW,
    KLING_MULTI_ELEMENTS_GENERATE,
    KLING_MULTI_ELEMENTS_POLL,
    KLING_VIDEO_EXTEND,
    KLING_VIDEO_EXTEND_POLL,
    KLING_EFFECTS,
    KLING_EFFECTS_POLL,
    KLING_AVATAR,
    KLING_AVATAR_POLL,
    KLING_MOTION_CONTROL,
    KLING_MOTION_CONTROL_POLL,
    KLING_IDENTIFY_FACE,
    KLING_LIP_SYNC,
    KLING_LIP_SYNC_POLL,
    KlingSubmitResponse,
    KlingPollResponse,
    KlingText2VideoRequest,
    KlingImage2VideoRequest,
    KlingOmniVideoRequest,
    KlingOmniVideoImageItem,
    KlingOmniVideoVideoItem,
    KlingMultiImage2VideoRequest,
    KlingMultiElementsInitRequest,
    KlingMultiElementsAddSelectionRequest,
    KlingMultiElementsPreviewRequest,
    KlingMultiElementsGenerateRequest,
    KlingVideoExtendRequest,
    KlingEffectsRequest,
    KlingAvatarRequest,
    KlingMotionControlRequest,
    KlingLipSyncRequest,
    KlingLipSyncFaceChoose,
    KlingCameraControl,
    kling_status_extractor,
)
from ..apis.veo import VEONodeRequest, VEONodeResponse, VEOFalAIRequest, VEOFalAIResponse, VEOPollResponse, veo_status_extractor
from ..apis.minimax import MinimaxHailuoRequest, MinimaxHailuoSubmitResponse, MinimaxHailuoPollResponse, minimax_status_extractor
from ..apis.vidu import VIDUVideoGenRequest, VIDUImageToVideoRequest, VIDUSubmitResponse, VIDUPollResponse, vidu_status_extractor
from ..apis.luma import LumaVideoGenRequest, LumaSubmitResponse, LumaPollResponse, luma_status_extractor
from ..apis.runway import RunwayGen4Request, RunwaySubmitResponse, RunwayPollResponse, runway_status_extractor
from ..utils.kling_helpers import (
    generate_storyboard_inputs as _generate_storyboard_inputs,
    parse_storyboard as _parse_storyboard,
    parse_camera_control as _parse_camera_control,
    kling_submit_poll_download as _kling_submit_poll_download,
)

logger = logging.getLogger(__name__)

KLING_SOUND_SUPPORTED_MODELS = {"kling-v2-5-turbo", "kling-v2-6", "kling-v3", "kling-v3-omni", "kling-video-o1"}


def _validate_kling_sound(sound: str, model_name: str, node_name: str) -> str | None:
    if sound == "off":
        return None
    if model_name not in KLING_SOUND_SUPPORTED_MODELS:
        logger.warning("[%s] sound='on' is not supported by model '%s'; ignoring. Supported: %s", node_name, model_name, sorted(KLING_SOUND_SUPPORTED_MODELS))
        return None
    return sound


class KlingVideoV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingVideoV3Node",
            display_name="Kling Video [V3]",
            category="api node/video/Kling",
            description="Kling text-to-video generation via UnlimitAI. Supports storyboard, camera control, and audio generation.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt. Ignored when storyboards are enabled."),
                IO.Combo.Input("model_name", options=["kling-v1", "kling-v1-6", "kling-v2-master", "kling-v2-1-master", "kling-v2-5-turbo", "kling-v3"], default="kling-v2-master"),
                IO.Combo.Input("duration", options=["5", "10"], default="5"),
                IO.Float.Input("cfg_scale", default=0.5, min=0.0, max=1.0, step=0.1),
                IO.Combo.Input("mode", options=["std", "pro"], default="std"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.String.Input("negative_prompt", multiline=True, default="", optional=True, tooltip="Optional negative prompt."),
                IO.DynamicCombo.Input(
                    "storyboards",
                    options=[
                        IO.DynamicCombo.Option("disabled", []),
                        IO.DynamicCombo.Option("2 storyboards", _generate_storyboard_inputs(2)),
                        IO.DynamicCombo.Option("3 storyboards", _generate_storyboard_inputs(3)),
                        IO.DynamicCombo.Option("4 storyboards", _generate_storyboard_inputs(4)),
                        IO.DynamicCombo.Option("5 storyboards", _generate_storyboard_inputs(5)),
                        IO.DynamicCombo.Option("6 storyboards", _generate_storyboard_inputs(6)),
                    ],
                    tooltip="Storyboard multi-prompt segments. Total duration must equal global duration.",
                    optional=True,
                ),
                IO.Combo.Input("sound", options=["off", "on"], default="off", optional=True, tooltip="Generate audio for the video."),
                IO.String.Input("camera_control_json", multiline=True, default="", optional=True, tooltip="Camera control JSON from Kling Camera Control node."),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", model_name: str = "kling-v2-master", duration: str = "5", aspect_ratio: str = "16:9", cfg_scale: float = 0.5, mode: str = "std", negative_prompt: str = "", storyboards: dict | None = None, sound: str = "off", camera_control_json: str = ""):
        stories_enabled = storyboards is not None and storyboards.get("storyboards") != "disabled"
        if not stories_enabled:
            validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        multi_shot, multi_prompt, shot_type = _parse_storyboard(storyboards, duration, model_name)
        camera_control = _parse_camera_control(camera_control_json)
        effective_sound = _validate_kling_sound(sound, model_name, "KlingVideoV3")
        request = KlingText2VideoRequest(
            model_name=model_name, prompt=prompt, duration=duration,
            aspect_ratio=aspect_ratio, cfg_scale=cfg_scale, mode=mode,
            negative_prompt=negative_prompt or None,
            multi_shot=multi_shot, shot_type=shot_type, multi_prompt=multi_prompt,
            sound=effective_sound,
            camera_control=camera_control,
        )
        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_TEXT2VIDEO, KLING_TEXT2VIDEO_POLL, request, key)
        return IO.NodeOutput(video_output, task_id)


class KlingImageToVideoV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingImageToVideoV3Node",
            display_name="Kling Image-to-Video [V3]",
            category="api node/video/Kling",
            description="Kling image-to-video generation via UnlimitAI. Supports storyboard, camera control, end frame, and audio.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt. Ignored when storyboards are enabled."),
                IO.Image.Input("image", optional=True, tooltip="Input image (first frame)."),
                IO.String.Input("image_url", default="", multiline=False, optional=True, tooltip="Or provide an image URL."),
                IO.Image.Input("image_tail", optional=True, tooltip="End frame image. Cannot be used with storyboards."),
                IO.String.Input("image_tail_url", default="", multiline=False, optional=True, tooltip="Or provide an end frame URL."),
                IO.Combo.Input("model_name", options=["kling-v1", "kling-v1-5", "kling-v1-6", "kling-v2-master", "kling-v2-1", "kling-v2-1-master", "kling-v2-5-turbo", "kling-v2-6", "kling-v3"], default="kling-v2-master"),
                IO.Combo.Input("duration", options=["5", "10"], default="5"),
                IO.Float.Input("cfg_scale", default=0.5, min=0.0, max=1.0, step=0.1),
                IO.Combo.Input("mode", options=["std", "pro"], default="std"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.String.Input("negative_prompt", multiline=True, default="", optional=True, tooltip="Optional negative prompt."),
                IO.Combo.Input("sound", options=["off", "on"], default="off", optional=True, tooltip="Generate audio for the video."),
                IO.DynamicCombo.Input(
                    "storyboards",
                    options=[
                        IO.DynamicCombo.Option("disabled", []),
                        IO.DynamicCombo.Option("2 storyboards", _generate_storyboard_inputs(2)),
                        IO.DynamicCombo.Option("3 storyboards", _generate_storyboard_inputs(3)),
                        IO.DynamicCombo.Option("4 storyboards", _generate_storyboard_inputs(4)),
                        IO.DynamicCombo.Option("5 storyboards", _generate_storyboard_inputs(5)),
                        IO.DynamicCombo.Option("6 storyboards", _generate_storyboard_inputs(6)),
                    ],
                    tooltip="Storyboard multi-prompt segments. Cannot be used with end frame.",
                    optional=True,
                ),
                IO.String.Input("camera_control_json", multiline=True, default="", optional=True, tooltip="Camera control JSON from Kling Camera Control node."),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image=None, image_url: str = "", image_tail=None, image_tail_url: str = "", model_name: str = "kling-v2-master", duration: str = "5", cfg_scale: float = 0.5, mode: str = "std", aspect_ratio: str = "16:9", negative_prompt: str = "", sound: str = "off", storyboards: dict | None = None, camera_control_json: str = ""):
        stories_enabled = storyboards is not None and storyboards.get("storyboards") != "disabled"
        if not stories_enabled:
            validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        resolved_image = prepare_image_input(image=image, image_url=image_url)
        resolved_tail = prepare_image_input(image=image_tail, image_url=image_tail_url)
        if resolved_tail and stories_enabled:
            raise Exception("End frame (image_tail) cannot be used with storyboards.")
        multi_shot, multi_prompt, shot_type = _parse_storyboard(storyboards, duration, model_name)
        camera_control = _parse_camera_control(camera_control_json)
        effective_sound = _validate_kling_sound(sound, model_name, "KlingImageToVideoV3")
        request = KlingImage2VideoRequest(
            model_name=model_name, prompt=prompt, image=resolved_image,
            image_tail=resolved_tail or None, duration=duration,
            cfg_scale=cfg_scale, mode=mode, aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt or None,
            sound=effective_sound,
            multi_shot=multi_shot, shot_type=shot_type, multi_prompt=multi_prompt,
            camera_control=camera_control,
        )
        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_IMAGE2VIDEO, KLING_IMAGE2VIDEO_POLL, request, key)
        return IO.NodeOutput(video_output, task_id)


class KlingDigitalHumanV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingDigitalHumanV3Node",
            display_name="Kling Digital Human [V3]",
            category="api node/video/Kling",
            description="Kling digital human / avatar video generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Image.Input("image", optional=True, tooltip="Input face image."),
                IO.String.Input("image_url", default="", multiline=False, optional=True, tooltip="Or provide a face image URL."),
                IO.String.Input("audio_id", default="", multiline=False, optional=True, tooltip="Audio ID from Kling TTS."),
                IO.Combo.Input("mode", options=["std", "pro"], default="std"),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image=None, image_url: str = "", audio_id: str = "", mode: str = "std"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        resolved_image = prepare_image_input(image=image, image_url=image_url)
        if not resolved_image:
            raise Exception("A face image is required for digital human generation.")
        request = KlingAvatarRequest(image=resolved_image, audio_id=audio_id or None, prompt=prompt, mode=mode)
        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_AVATAR, KLING_AVATAR_POLL, request, key,
            max_poll_attempts=300, estimated_duration=180)
        return IO.NodeOutput(video_output, task_id)


class KlingMultiImage2VideoV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingMultiImage2VideoV3Node",
            display_name="Kling Multi-Image to Video [V3]",
            category="api node/video/Kling",
            description="Kling multi-image reference video generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.String.Input("image_urls", default="", multiline=True, tooltip="Image URLs, one per line (1-4 images)."),
                IO.Combo.Input("mode", options=["std", "pro"], default="std"),
                IO.Combo.Input("duration", options=["5", "10"], default="5"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image_urls: str = "", mode: str = "std", duration: str = "5", aspect_ratio: str = "16:9"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        urls = [u.strip() for u in image_urls.strip().split("\n") if u.strip()]
        if not urls:
            raise Exception("At least one image URL is required.")
        request = KlingMultiImage2VideoRequest(image_list=[{"image": u} for u in urls[:4]], prompt=prompt, mode=mode, duration=duration, aspect_ratio=aspect_ratio)
        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_MULTI_IMAGE2VIDEO, KLING_MULTI_IMAGE2VIDEO_POLL, request, key)
        return IO.NodeOutput(video_output, task_id)


class KlingOmniVideoV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingOmniVideoV3Node",
            display_name="Kling Omni-Video [V3]",
            category="api node/video/Kling",
            description="Kling Omni-Video generation via UnlimitAI. Supports storyboard, end frame, reference videos, and audio.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt. Ignored when storyboards are enabled."),
                IO.String.Input("image_urls", default="", multiline=True, optional=True, tooltip="First frame image URLs, one per line."),
                IO.Image.Input("end_frame", optional=True, tooltip="End frame image. Cannot be used with storyboards."),
                IO.String.Input("end_frame_url", default="", multiline=False, optional=True, tooltip="Or provide an end frame URL."),
                IO.String.Input("video_urls", default="", multiline=True, optional=True, tooltip="Reference video URLs, one per line."),
                IO.Combo.Input("model_name", options=["kling-video-o1", "kling-v3-omni"], default="kling-video-o1"),
                IO.Combo.Input("resolution", options=["720p", "1080p", "4k"], default="1080p", tooltip="Resolution maps to mode: 720p=std, 1080p=pro, 4k=4k."),
                IO.Combo.Input("duration", options=["3", "4", "5", "6", "7", "8", "9", "10"], default="5"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Combo.Input("sound", options=["off", "on"], default="off", optional=True, tooltip="Generate audio. Only supported for kling-v3-omni."),
                IO.DynamicCombo.Input(
                    "storyboards",
                    options=[
                        IO.DynamicCombo.Option("disabled", []),
                        IO.DynamicCombo.Option("2 storyboards", _generate_storyboard_inputs(2)),
                        IO.DynamicCombo.Option("3 storyboards", _generate_storyboard_inputs(3)),
                        IO.DynamicCombo.Option("4 storyboards", _generate_storyboard_inputs(4)),
                        IO.DynamicCombo.Option("5 storyboards", _generate_storyboard_inputs(5)),
                        IO.DynamicCombo.Option("6 storyboards", _generate_storyboard_inputs(6)),
                    ],
                    tooltip="Storyboard multi-prompt segments. Only for kling-v3-omni. Cannot be used with end frame.",
                    optional=True,
                ),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image_urls: str = "", end_frame=None, end_frame_url: str = "", video_urls: str = "", model_name: str = "kling-video-o1", resolution: str = "1080p", duration: str = "5", aspect_ratio: str = "16:9", sound: str = "off", storyboards: dict | None = None):
        stories_enabled = storyboards is not None and storyboards.get("storyboards") != "disabled"
        if not stories_enabled:
            validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        resolved_tail = prepare_image_input(image=end_frame, image_url=end_frame_url)
        if resolved_tail and stories_enabled:
            raise Exception("End frame cannot be used with storyboards.")
        if model_name == "kling-video-o1":
            if stories_enabled:
                raise Exception("kling-video-o1 does not support storyboards.")
            if sound == "on":
                raise Exception("kling-video-o1 does not support audio generation.")
            if resolution == "4k":
                raise Exception("kling-video-o1 does not support 4k resolution.")
        mode_map = {"720p": "std", "1080p": "pro", "4k": "4k"}
        mode = mode_map.get(resolution, "pro")
        multi_shot, multi_prompt, shot_type = _parse_storyboard(storyboards, duration, model_name)
        img_list = []
        if image_urls:
            for u in [u.strip() for u in image_urls.strip().split("\n") if u.strip()]:
                img_list.append(KlingOmniVideoImageItem(image_url=u, type="first_frame"))
        if resolved_tail:
            img_list.append(KlingOmniVideoImageItem(image_url=resolved_tail, type="end_frame"))
        vid_list = None
        if video_urls:
            vid_list = [KlingOmniVideoVideoItem(video_url=u.strip()) for u in video_urls.strip().split("\n") if u.strip()]
        effective_sound = _validate_kling_sound(sound, model_name, "KlingOmniVideoV3")
        request = KlingOmniVideoRequest(
            model_name=model_name, prompt=prompt,
            image_list=img_list if img_list else None,
            video_list=vid_list,
            mode=mode, duration=duration, aspect_ratio=aspect_ratio,
            sound=effective_sound,
            multi_shot=multi_shot, shot_type=shot_type, multi_prompt=multi_prompt,
        )
        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_OMNI_VIDEO, KLING_OMNI_VIDEO_POLL, request, key)
        return IO.NodeOutput(video_output, task_id)


class KlingMultiElementsV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingMultiElementsV3Node",
            display_name="Kling Multi-Elements Edit [V3]",
            category="api node/video/Kling",
            description="Kling multi-modal video editing via UnlimitAI (init -> select -> generate).",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("video_url", default="", multiline=False, tooltip="Video URL to edit."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Edit prompt using templates like <<<video_1>>>, <<<image_1>>>."),
                IO.Combo.Input("edit_mode", options=["addition", "swap", "removal"], default="addition"),
                IO.String.Input("image_urls", default="", multiline=True, optional=True, tooltip="Reference image URLs, one per line."),
                IO.Combo.Input("mode", options=["std", "pro"], default="std"),
                IO.Combo.Input("duration", options=["5", "10"], default="5"),
                IO.Float.Input("selection_x", default=0.5, min=0.0, max=1.0, step=0.01, tooltip="X coordinate of element to select (0-1, relative to frame width)."),
                IO.Float.Input("selection_y", default=0.5, min=0.0, max=1.0, step=0.01, tooltip="Y coordinate of element to select (0-1, relative to frame height)."),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", video_url: str = "", prompt: str = "", edit_mode: str = "addition", image_urls: str = "", mode: str = "std", duration: str = "5", selection_x: float = 0.5, selection_y: float = 0.5):
        validate_string(video_url, field_name="video_url")
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        init_request = KlingMultiElementsInitRequest(video_url=video_url)
        init_response: KlingSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path=KLING_MULTI_ELEMENTS_INIT, method="POST"), data=init_request, response_model=KlingSubmitResponse, api_key=key, wait_label="Initializing", estimated_duration=10)
        session_id = init_response.data.task_id if init_response.data else ""
        if not session_id:
            raise Exception(f"Kling multi-elements init failed: {init_response}")
        add_request = KlingMultiElementsAddSelectionRequest(session_id=session_id, frame_index=1, points=[{"x": selection_x, "y": selection_y}])
        await sync_op(cls, endpoint=ApiEndpoint(path=KLING_MULTI_ELEMENTS_ADD, method="POST"), data=add_request, response_model=KlingSubmitResponse, api_key=key, wait_label="Adding selection", estimated_duration=5)
        preview_request = KlingMultiElementsPreviewRequest(session_id=session_id)
        await sync_op(cls, endpoint=ApiEndpoint(path=KLING_MULTI_ELEMENTS_PREVIEW, method="POST"), data=preview_request, response_model=KlingSubmitResponse, api_key=key, wait_label="Previewing", estimated_duration=5)
        img_urls = [u.strip() for u in image_urls.strip().split("\n") if u.strip()] if image_urls else None
        generate_request = KlingMultiElementsGenerateRequest(
            session_id=session_id, edit_mode=edit_mode,
            image_list=img_urls, prompt=prompt,
            mode=mode, duration=duration,
        )
        submit: KlingSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path=KLING_MULTI_ELEMENTS_GENERATE, method="POST"), data=generate_request, response_model=KlingSubmitResponse, api_key=key, wait_label="Submitting edit", estimated_duration=5)
        task_id = submit.data.task_id
        if not task_id:
            raise Exception(f"Kling multi-elements generate failed: {submit}")
        poll_response: KlingPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=KLING_MULTI_ELEMENTS_POLL.format(task_id), method="GET"), response_model=KlingPollResponse, status_extractor=kling_status_extractor, api_key=key, completed_statuses=["succeed"], failed_statuses=["failed"], queued_statuses=["submitted", "processing"], poll_interval=5.0, max_poll_attempts=240, estimated_duration=180)
        video_url_result = ""
        if poll_response.data and poll_response.data.task_result and poll_response.data.task_result.videos:
            video_url_result = poll_response.data.task_result.videos[0].url
        if not video_url_result:
            raise Exception("Kling multi-elements task completed but no video URL found.")
        return IO.NodeOutput(await download_url_to_video_output(video_url_result, cls=cls), task_id)


class KlingVideoExtendV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingVideoExtendV3Node",
            display_name="Kling Video Extend [V3]",
            category="api node/video/Kling",
            description="Kling video extension via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("video_id", default="", multiline=False, tooltip="Kling video ID to extend."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Extension prompt."),
                IO.String.Input("negative_prompt", multiline=True, default="", optional=True, tooltip="Optional negative prompt."),
                IO.Float.Input("cfg_scale", default=0.5, min=0.0, max=1.0, step=0.1),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", video_id: str = "", prompt: str = "", negative_prompt: str = "", cfg_scale: float = 0.5):
        validate_string(video_id, field_name="video_id")
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = KlingVideoExtendRequest(video_id=video_id, prompt=prompt, negative_prompt=negative_prompt or None, cfg_scale=cfg_scale)
        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_VIDEO_EXTEND, KLING_VIDEO_EXTEND_POLL, request, key)
        return IO.NodeOutput(video_output, task_id)


class KlingEffectsV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingEffectsV3Node",
            display_name="Kling Video Effects [V3]",
            category="api node/video/Kling",
            description="Kling video effects via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("effect_scene", default="", multiline=False, tooltip="Effect scene name (e.g. balloon_parade)."),
                IO.Image.Input("image", optional=True, tooltip="Input image for single-person effects."),
                IO.String.Input("image_url", default="", multiline=False, optional=True, tooltip="Or provide an image URL."),
                IO.Combo.Input("duration", options=["5", "10"], default="5"),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", effect_scene: str = "", image=None, image_url: str = "", duration: str = "5"):
        validate_string(effect_scene, field_name="effect_scene")
        key = validate_api_key(api_key)
        resolved_image = prepare_image_input(image=image, image_url=image_url)
        request = KlingEffectsRequest(
            effect_scene=effect_scene,
            input={"image": resolved_image, "duration": duration} if resolved_image else {"duration": duration},
        )
        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_EFFECTS, KLING_EFFECTS_POLL, request, key)
        return IO.NodeOutput(video_output, task_id)


class KlingMotionControlV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingMotionControlV3Node",
            display_name="Kling Motion Control [V3]",
            category="api node/video/Kling",
            description="Kling motion control video generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", optional=True, tooltip="Text prompt."),
                IO.Image.Input("image", optional=True, tooltip="Reference image of the character."),
                IO.String.Input("image_url", default="", multiline=False, optional=True, tooltip="Or provide a character image URL."),
                IO.String.Input("video_url", default="", multiline=False, tooltip="Motion reference video URL."),
                IO.Combo.Input("character_orientation", options=["image", "video"], default="image"),
                IO.Combo.Input("mode", options=["std", "pro"], default="std"),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image=None, image_url: str = "", video_url: str = "", character_orientation: str = "image", mode: str = "std"):
        validate_string(video_url, field_name="video_url")
        key = validate_api_key(api_key)
        resolved_image = prepare_image_input(image=image, image_url=image_url)
        if not resolved_image:
            raise Exception("A reference image is required for motion control.")
        request = KlingMotionControlRequest(prompt=prompt or None, image_url=resolved_image, video_url=video_url, character_orientation=character_orientation, mode=mode)
        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_MOTION_CONTROL, KLING_MOTION_CONTROL_POLL, request, key)
        return IO.NodeOutput(video_output, task_id)


class KlingCameraControlV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingCameraControlV3Node",
            display_name="Kling Camera Control [V3]",
            category="api node/video/Kling",
            description="Configure camera control parameters for Kling video nodes. Output is a JSON string to connect to camera_control_json input.",
            inputs=[
                IO.Combo.Input("camera_type", options=["simple", "down_back", "forward_up", "right_turn_forward", "left_turn_forward"], default="simple", tooltip="Camera movement type. 'simple' uses the sliders below; others are presets."),
                IO.Float.Input("horizontal", default=0.0, min=-10.0, max=10.0, step=0.25, tooltip="Camera horizontal movement. Negative=left, positive=right."),
                IO.Float.Input("vertical", default=0.0, min=-10.0, max=10.0, step=0.25, tooltip="Camera vertical movement. Negative=down, positive=up."),
                IO.Float.Input("pan", default=0.0, min=-10.0, max=10.0, step=0.25, tooltip="Camera rotation in vertical plane. Negative=down, positive=up."),
                IO.Float.Input("tilt", default=0.0, min=-10.0, max=10.0, step=0.25, tooltip="Camera rotation in horizontal plane. Negative=left, positive=right."),
                IO.Float.Input("roll", default=0.0, min=-10.0, max=10.0, step=0.25, tooltip="Camera rolling. Negative=counterclockwise, positive=clockwise."),
                IO.Float.Input("zoom", default=0.0, min=-10.0, max=10.0, step=0.25, tooltip="Camera focal length change. Negative=narrower, positive=wider."),
            ],
            outputs=[IO.String.Output("camera_control_json")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=False,
        )

    @classmethod
    async def execute(cls, camera_type: str = "simple", horizontal: float = 0.0, vertical: float = 0.0, pan: float = 0.0, tilt: float = 0.0, roll: float = 0.0, zoom: float = 0.0):
        if camera_type == "simple" and all(math.isclose(v, 0.0) for v in [horizontal, vertical, pan, tilt, roll, zoom]):
            raise Exception("At least one camera axis value must be non-zero when using 'simple' type.")
        result = {
            "type": camera_type,
            "config": {
                "horizontal": horizontal,
                "vertical": vertical,
                "pan": pan,
                "tilt": tilt,
                "roll": roll,
                "zoom": zoom,
            },
        }
        return IO.NodeOutput(json.dumps(result))


class KlingLipSyncV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingLipSyncV3Node",
            display_name="Kling Lip Sync [V3]",
            category="api node/video/Kling",
            description="Kling lip sync video generation via UnlimitAI. Automatically detects faces and syncs mouth movements to text or audio.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("video_url", default="", multiline=False, tooltip="Video URL (2-10 seconds, 720-1920px height/width)."),
                IO.Combo.Input("lip_sync_mode", options=["text2video", "audio2video"], default="text2video", tooltip="text2video: generate speech from text; audio2video: use provided audio."),
                IO.String.Input("text", multiline=True, default="", optional=True, tooltip="Text for lip sync (max 120 chars, text2video mode)."),
                IO.String.Input("voice_id", default="", multiline=False, optional=True, tooltip="Voice ID from Kling presets (text2video mode)."),
                IO.String.Input("audio_url", default="", multiline=False, optional=True, tooltip="Audio URL for lip sync (audio2video mode)."),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", video_url: str = "", lip_sync_mode: str = "text2video", text: str = "", voice_id: str = "", audio_url: str = ""):
        validate_string(video_url, field_name="video_url")
        key = validate_api_key(api_key)
        identify_response = await sync_op_raw(
            cls, endpoint=ApiEndpoint(path=KLING_IDENTIFY_FACE, method="POST"),
            data={"video_url": video_url}, api_key=key,
            wait_label="Identifying faces", estimated_duration=10,
        )
        session_id = ""
        face_id = ""
        if isinstance(identify_response, dict):
            data = identify_response.get("data", {})
            if isinstance(data, dict):
                session_id = data.get("session_id", "")
                faces = data.get("faces", [])
                if faces and isinstance(faces, list) and isinstance(faces[0], dict):
                    face_id = faces[0].get("face_id", "")
        if not session_id or not face_id:
            raise Exception("No face detected in the video. Ensure the video contains a visible face.")
        face_choose_item = KlingLipSyncFaceChoose(face_id=face_id)
        if lip_sync_mode == "text2video":
            if not text.strip():
                raise Exception("Text is required for text2video lip sync mode.")
            if len(text) > 120:
                raise Exception("Text for lip sync must be 120 characters or less.")
            face_choose_item.audio_id = voice_id or None
        else:
            if not audio_url.strip():
                raise Exception("Audio URL is required for audio2video lip sync mode.")
            face_choose_item.sound_file = audio_url
        request = KlingLipSyncRequest(
            session_id=session_id,
            face_choose=[face_choose_item],
        )
        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_LIP_SYNC, KLING_LIP_SYNC_POLL, request, key,
            max_poll_attempts=120, estimated_duration=120)
        return IO.NodeOutput(video_output, task_id)


class VEOV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="VEOV3Node",
            display_name="VEO [V3]",
            category="api node/video/VEO",
            description="Google VEO video generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("model", options=["veo-3.1", "veo-3.1-fast", "veo-3", "veo-3-fast"], default="veo-3.1"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Combo.Input("duration", options=["5s", "10s"], default="5s"),
                IO.Boolean.Input("audio", default=True),
                IO.Combo.Input("resolution", options=["1080p", "4k"], default="1080p"),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("request_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", model: str = "veo-3.1", aspect_ratio: str = "16:9", duration: str = "5s", audio: bool = True, resolution: str = "1080p"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = VEONodeRequest(prompt=prompt, aspectRatio=aspect_ratio, duration=duration, audio=audio, resolution=resolution)
        submit: VEONodeResponse = await sync_op(cls, endpoint=ApiEndpoint(path=f"/veo/{model}/generate", method="POST"), data=request, response_model=VEONodeResponse, api_key=key, wait_label="Submitting VEO task", estimated_duration=5)
        status_url = submit.status_url
        request_id = submit.request_id
        if not status_url:
            raise Exception(f"VEO submit failed: no status_url. Response: {submit}")
        result: VEOPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=status_url, method="GET"), response_model=VEOPollResponse, status_extractor=veo_status_extractor, api_key=key, completed_statuses=["succeeded", "completed", "COMPLETED"], failed_statuses=["failed", "canceled"], queued_statuses=["queued", "processing", "running"], poll_interval=10.0, max_poll_attempts=180, estimated_duration=300)
        video_url = ""
        if result.video:
            video_url = result.video.url
        elif result.videos:
            video_url = result.videos[0].url
        if not video_url:
            raise Exception("VEO task completed but no video URL found.")
        return IO.NodeOutput(await download_url_to_video_output(video_url, cls=cls), request_id)


class VEOFalAIV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="VEOFalAIV3Node",
            display_name="VEO FalAI [V3]",
            category="api node/video/VEO",
            description="Google VEO via Fal-ai format via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Combo.Input("duration", options=["5s", "10s"], default="5s"),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("request_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", aspect_ratio: str = "16:9", duration: str = "5s"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = VEOFalAIRequest(prompt=prompt, aspect_ratio=aspect_ratio, duration=duration)
        submit: VEOFalAIResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/fal-ai/veo-3", method="POST"), data=request, response_model=VEOFalAIResponse, api_key=key, wait_label="Submitting VEO task", estimated_duration=5)
        response_url = submit.response_url
        request_id = submit.request_id
        if not response_url:
            raise Exception(f"VEO FalAI submit failed: no response_url. Response: {submit}")
        poll_url = response_url.replace("queue.fal.run", "api.unlimitai.org/fal-ai/veo-3/requests")
        result: VEOPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=poll_url, method="GET"), response_model=VEOPollResponse, status_extractor=veo_status_extractor, api_key=key, completed_statuses=["succeeded", "completed", "COMPLETED"], failed_statuses=["failed", "canceled"], queued_statuses=["queued", "processing", "IN_QUEUE", "IN_PROGRESS"], poll_interval=10.0, max_poll_attempts=180, estimated_duration=300)
        video_url = ""
        if result.video:
            video_url = result.video.url
        elif result.videos:
            video_url = result.videos[0].url
        if not video_url:
            raise Exception("VEO FalAI task completed but no video URL found.")
        return IO.NodeOutput(await download_url_to_video_output(video_url, cls=cls), request_id)


class MinimaxHailuoV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="MinimaxHailuoV3Node",
            display_name="Minimax Hailuo [V3]",
            category="api node/video/Minimax",
            description="Minimax Hailuo video generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("model", options=["T2V-01", "T2V-01-Director"], default="T2V-01"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", model: str = "T2V-01", aspect_ratio: str = "16:9"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = MinimaxHailuoRequest(model=model, prompt=prompt, aspect_ratio=aspect_ratio)
        submit: MinimaxHailuoSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/video/generation", method="POST"), data=request, response_model=MinimaxHailuoSubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        task_id = submit.task_id
        if not task_id:
            raise Exception(f"Minimax submit failed: no task_id. Response: {submit}")
        result: MinimaxHailuoPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=f"/v1/video/generation/{task_id}", method="GET"), response_model=MinimaxHailuoPollResponse, status_extractor=minimax_status_extractor, api_key=key, completed_statuses=["success", "Success", "succeeded"], failed_statuses=["failed", "Fail"], queued_statuses=["queued", "processing", "Processing"], poll_interval=10.0, max_poll_attempts=180, estimated_duration=120)
        video_url = result.video_url or ""
        if not video_url:
            raise Exception("Minimax task completed but no video URL found.")
        return IO.NodeOutput(await download_url_to_video_output(video_url, cls=cls), task_id)


class VIDUVideoV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="VIDUVideoV3Node",
            display_name="VIDU Video [V3]",
            category="api node/video/VIDU",
            description="VIDU text-to-video generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("model", options=["vidu2", "vidu2.5"], default="vidu2"),
                IO.Combo.Input("duration", options=["4", "8"], default="4"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", model: str = "vidu2", duration: str = "4", aspect_ratio: str = "16:9"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = VIDUVideoGenRequest(model=model, prompt=prompt, duration=duration, aspect_ratio=aspect_ratio)
        submit: VIDUSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/videos/vidu", method="POST"), data=request, response_model=VIDUSubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        task_id = submit.data.task_id
        if not task_id:
            raise Exception(f"VIDU submit failed: no task_id. Response: {submit}")
        result: VIDUPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=f"/v1/videos/vidu/{task_id}", method="GET"), response_model=VIDUPollResponse, status_extractor=vidu_status_extractor, api_key=key, completed_statuses=["success", "Success", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "created"], poll_interval=5.0, max_poll_attempts=180, estimated_duration=120)
        video_url = result.video_url or ""
        if not video_url:
            raw = result.model_dump() if hasattr(result, "model_dump") else {}
            data = raw.get("data", {})
            video_url = data.get("video_url", "") if isinstance(data, dict) else ""
        if not video_url:
            raise Exception("VIDU task completed but no video URL found.")
        return IO.NodeOutput(await download_url_to_video_output(video_url, cls=cls), task_id)


class VIDUImageToVideoV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="VIDUImageToVideoV3Node",
            display_name="VIDU Image-to-Video [V3]",
            category="api node/video/VIDU",
            description="VIDU image-to-video generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Image.Input("image", optional=True, tooltip="Input image."),
                IO.String.Input("image_url", default="", multiline=False, optional=True, tooltip="Or provide an image URL."),
                IO.Combo.Input("model", options=["vidu2", "vidu2.5"], default="vidu2"),
                IO.Combo.Input("duration", options=["4", "8"], default="4"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image=None, image_url: str = "", model: str = "vidu2", duration: str = "4", aspect_ratio: str = "16:9"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        resolved_image = prepare_image_input(image=image, image_url=image_url)
        if not resolved_image:
            raise Exception("An image is required for VIDU image-to-video generation.")
        if resolved_image.startswith(("http://", "https://")):
            request = VIDUImageToVideoRequest(model=model, prompt=prompt, image_url=resolved_image, duration=duration, aspect_ratio=aspect_ratio)
        else:
            request = VIDUImageToVideoRequest(model=model, prompt=prompt, image=resolved_image, duration=duration, aspect_ratio=aspect_ratio)
        submit: VIDUSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/videos/vidu/image-to-video", method="POST"), data=request, response_model=VIDUSubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        task_id = submit.data.task_id
        if not task_id:
            raise Exception(f"VIDU i2v submit failed: no task_id. Response: {submit}")
        result: VIDUPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=f"/v1/videos/vidu/{task_id}", method="GET"), response_model=VIDUPollResponse, status_extractor=vidu_status_extractor, api_key=key, completed_statuses=["success", "Success", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "created"], poll_interval=5.0, max_poll_attempts=180, estimated_duration=120)
        video_url = result.video_url or ""
        if not video_url:
            raw = result.model_dump() if hasattr(result, "model_dump") else {}
            data = raw.get("data", {})
            video_url = data.get("video_url", "") if isinstance(data, dict) else ""
        if not video_url:
            raise Exception("VIDU i2v task completed but no video URL found.")
        return IO.NodeOutput(await download_url_to_video_output(video_url, cls=cls), task_id)


class LumaVideoV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="LumaVideoV3Node",
            display_name="Luma Video [V3]",
            category="api node/video/Luma",
            description="Luma video generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Boolean.Input("loop", default=False, tooltip="Enable seamless loop."),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", aspect_ratio: str = "16:9", loop: bool = False):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = LumaVideoGenRequest(prompt=prompt, aspect_ratio=aspect_ratio, loop=loop)
        submit: LumaSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/luma/v2/video/generation", method="POST"), data=request, response_model=LumaSubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        status_url = submit.status_url
        task_id = submit.id
        if not status_url:
            raise Exception(f"Luma submit failed: no status_url. Response: {submit}")
        result: LumaPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=status_url, method="GET"), response_model=LumaPollResponse, status_extractor=luma_status_extractor, api_key=key, completed_statuses=["completed", "succeeded"], failed_statuses=["failed", "canceled"], queued_statuses=["queued", "processing", "dreaming"], poll_interval=5.0, max_poll_attempts=180, estimated_duration=120)
        video_url = ""
        if result.video:
            video_url = result.video.url or result.video.download_url or ""
        if not video_url:
            raise Exception("Luma task completed but no video URL found.")
        return IO.NodeOutput(await download_url_to_video_output(video_url, cls=cls), task_id)


class RunwayGen4V3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="RunwayGen4V3Node",
            display_name="Runway Gen-4 [V3]",
            category="api node/video/Runway",
            description="Runway Gen-4 video generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Image.Input("image", optional=True, tooltip="Input image (optional reference)."),
                IO.String.Input("image_url", default="", multiline=False, optional=True, tooltip="Or provide an image URL."),
                IO.Combo.Input("model", options=["gen4_turbo", "gen4"], default="gen4_turbo"),
                IO.Combo.Input("ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Int.Input("duration", default=5, min=5, max=10, step=5),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image=None, image_url: str = "", model: str = "gen4_turbo", ratio: str = "16:9", duration: int = 5):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        resolved_image = prepare_image_input(image=image, image_url=image_url)
        if image_url and not resolved_image and not image:
            raise Exception(f"image_url does not appear to be a valid URL (must start with http://, https://, or data:): {image_url[:80]}")
        request = RunwayGen4Request(prompt=prompt, model=model, ratio=ratio, duration=duration, image_url=resolved_image)
        submit: RunwaySubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/runway/v1/image_to_video", method="POST"), data=request, response_model=RunwaySubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        status_url = submit.status_url
        task_id = submit.id
        if not status_url:
            raise Exception(f"Runway submit failed: no status_url. Response: {submit}")
        result: RunwayPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=status_url, method="GET"), response_model=RunwayPollResponse, status_extractor=runway_status_extractor, api_key=key, completed_statuses=["SUCCEEDED", "succeeded", "completed"], failed_statuses=["FAILED", "failed", "canceled"], queued_statuses=["PENDING", "RUNNING", "queued", "processing"], poll_interval=5.0, max_poll_attempts=180, estimated_duration=120)
        video_url = ""
        if result.output:
            video_url = result.output[0] if isinstance(result.output[0], str) else str(result.output[0])
        if not video_url:
            raise Exception("Runway task completed but no video URL found.")
        return IO.NodeOutput(await download_url_to_video_output(video_url, cls=cls), task_id)


class UnlimitAIVideoV3Extension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        return [
            KlingVideoV3Node, KlingImageToVideoV3Node, KlingDigitalHumanV3Node,
            KlingMultiImage2VideoV3Node, KlingOmniVideoV3Node,
            KlingMultiElementsV3Node, KlingVideoExtendV3Node,
            KlingEffectsV3Node, KlingMotionControlV3Node,
            KlingCameraControlV3Node, KlingLipSyncV3Node,
            VEOV3Node, VEOFalAIV3Node,
            MinimaxHailuoV3Node,
            VIDUVideoV3Node, VIDUImageToVideoV3Node,
            LumaVideoV3Node, RunwayGen4V3Node,
        ]


async def comfy_entrypoint() -> UnlimitAIVideoV3Extension:
    return UnlimitAIVideoV3Extension()
