import json
import logging
import re
import shutil
import subprocess
import tempfile
from io import BytesIO
from typing import Dict, Any, Optional

from typing_extensions import override

from comfy_api.latest import IO, ComfyExtension, InputImpl

from ..unlimitai_util import (
    ApiEndpoint,
    download_url_as_bytesio,
    download_url_to_video_output,
    poll_op,
    poll_op_raw,
    prepare_image_input,
    sync_op,
    sync_op_raw,
    validate_api_key,
    validate_string,
)
from ..apis.kling import (
    KLING_IMAGE_GEN,
    KLING_IMAGE_GEN_POLL,
    KLING_IMAGE2VIDEO,
    KLING_IMAGE2VIDEO_POLL,
    KLING_TEXT2VIDEO,
    KLING_TEXT2VIDEO_POLL,
    KlingCameraConfig,
    KlingCameraControl,
    KlingImage2VideoRequest,
    KlingImageGenRequest,
    KlingText2VideoRequest,
    KlingMultiPromptItem,
    KlingSubmitResponse,
    KlingPollResponse,
    kling_status_extractor,
)
from ..apis.minimax import MinimaxTTSRequest, MinimaxTTSResponse
from ..apis.text import TextGenerationRequest, TextGenerationResponse, ChatMessage, extract_text_content
from ..utils.smart_skip import SmartSkipper
from ..utils.content_dedup import ContentDeduplicator
from ..utils.progress_tracker import ProgressTracker
from ..utils.json_utils import parse_json_safe
from ..utils.delay import SmartDelay
from ..utils.kling_helpers import (
    generate_storyboard_inputs as _generate_storyboard_inputs,
    parse_camera_control as _parse_camera_control,
    kling_submit_poll_download as _kling_submit_poll_download,
)
from ..unlimitai_util.conversions import audio_bytes_to_audio_input

logger = logging.getLogger(__name__)


class AsyncWorkflowContext:
    """Per-instance async context holding all optimization components for V3 nodes.

    Uses SmartDelay.wait_async() instead of wait() to avoid blocking the event loop.
    SmartSkipper, ContentDeduplicator, and ProgressTracker are pure computation
    and can be called from async code without adaptation.
    """

    def __init__(
        self,
        enable_smart_skip: bool = True,
        enable_dedup: bool = True,
        enable_progress: bool = True,
        base_delay: float = 1.0,
    ):
        self.enable_smart_skip = enable_smart_skip
        self.enable_dedup = enable_dedup
        self.enable_progress = enable_progress

        self.smart_skip = SmartSkipper() if enable_smart_skip else None
        self.content_dedup = ContentDeduplicator() if enable_dedup else None
        self.smart_delay = SmartDelay(initial_delay=base_delay)
        self.progress_trackers: Dict[str, ProgressTracker] = {}

    def should_skip_generation(self, task_type: str, scene: Dict[str, Any]) -> Optional[str]:
        if not self.smart_skip:
            return None

        should_gen = True
        reason = ""

        if task_type == "image":
            should_gen, reason = self.smart_skip.should_generate_image(scene)
        elif task_type == "video":
            should_gen, reason = self.smart_skip.should_generate_video(scene)
        elif task_type == "audio":
            should_gen, reason = self.smart_skip.should_generate_audio(scene)
        elif task_type == "music":
            should_gen, reason = self.smart_skip.should_generate_music(scene)

        if not should_gen:
            logger.info("Smart skip: %s", reason)
            return reason
        return None

    def check_content_duplicate(self, task_type: str, content_key: str) -> Optional[str]:
        if not self.content_dedup:
            return None

        try:
            cached = self.content_dedup.check_exists(content_key, content_type=task_type)
            if cached:
                url = cached.get(f"{task_type}_url") or cached.get("url") or cached.get("image_url") or cached.get("video_url")
                if url:
                    logger.info("Found duplicate content for %s", task_type)
                    return url
        except Exception as e:
            logger.debug("Dedup check failed: %s", e)

        return None

    def store_content_duplicate(self, task_type: str, content_key: str, url: str):
        if not self.content_dedup or not url:
            return

        try:
            self.content_dedup.store(content_key, result={f"{task_type}_url": url}, content_type=task_type)
        except Exception as e:
            logger.debug("Dedup store failed: %s", e)

    async def apply_smart_delay(self, task_type: str = "default", is_last: bool = False):
        if is_last:
            return

        await self.smart_delay.wait_async(operation=task_type)

    def record_result(self, success: bool, is_rate_limit: bool = False):
        if success:
            self.smart_delay.on_success()
        elif is_rate_limit:
            self.smart_delay.on_failure(is_rate_limit=True)
        else:
            self.smart_delay.on_failure()

    def start_progress(self, batch_key: str, total: int, label: str):
        if not self.enable_progress:
            return
        tracker = ProgressTracker(total_tasks=total, stage_name=label)
        tracker.start(f"{label} generation")
        self.progress_trackers[batch_key] = tracker

    def update_progress(self, batch_key: str, task_name: str, completed: int):
        tracker = self.progress_trackers.get(batch_key)
        if tracker:
            tracker.update(task_name, completed=completed)

    def finish_progress(self, batch_key: str):
        tracker = self.progress_trackers.get(batch_key)
        if tracker:
            tracker.finish()
            del self.progress_trackers[batch_key]

    def flush_dedup(self):
        if self.content_dedup:
            try:
                self.content_dedup.flush()
            except Exception as e:
                logger.debug("Dedup flush failed: %s", e)


def _is_rate_limit_error(exc: Exception) -> bool:
    error_str = str(exc).lower()
    return "rate" in error_str or "limit" in error_str or "429" in error_str


class StoryboardComposerV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="StoryboardComposerV3Node",
            display_name="Storyboard Composer [V3]",
            category="api node/workflow/Drama",
            description="Compose storyboard JSON from segments. Output feeds into Kling Video nodes or Scene Video Generator storyboard mode.",
            inputs=[
                IO.Combo.Input("total_duration", options=["5", "10"], default="5"),
                IO.DynamicCombo.Input(
                    "storyboards",
                    options=[
                        IO.DynamicCombo.Option("2 segments", _generate_storyboard_inputs(2)),
                        IO.DynamicCombo.Option("3 segments", _generate_storyboard_inputs(3)),
                        IO.DynamicCombo.Option("4 segments", _generate_storyboard_inputs(4)),
                        IO.DynamicCombo.Option("5 segments", _generate_storyboard_inputs(5)),
                        IO.DynamicCombo.Option("6 segments", _generate_storyboard_inputs(6)),
                    ],
                    tooltip="Storyboard segments. Total segment durations must equal total_duration.",
                ),
            ],
            outputs=[IO.String.Output("storyboard_json")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=False,
        )

    @classmethod
    async def execute(cls, total_duration: str = "5", storyboards: dict | None = None):
        if storyboards is None:
            return IO.NodeOutput("")
        try:
            count = int(storyboards["storyboards"].split()[0])
        except (ValueError, IndexError, TypeError, KeyError):
            return IO.NodeOutput("")
        segments = []
        total = 0
        for i in range(1, count + 1):
            prompt = storyboards.get(f"storyboard_{i}_prompt", "")
            duration = storyboards.get(f"storyboard_{i}_duration", 5)
            if not prompt.strip():
                raise Exception(f"Storyboard segment {i} prompt is empty.")
            if len(prompt) > 512:
                raise Exception(f"Storyboard segment {i} prompt exceeds 512 characters.")
            segments.append({"index": i, "prompt": prompt, "duration": duration})
            total += duration
        if total != int(total_duration):
            raise Exception(
                f"Total segment duration ({total}s) must equal total_duration ({total_duration}s)."
            )
        result = {"total_duration": int(total_duration), "segments": segments}
        return IO.NodeOutput(json.dumps(result, ensure_ascii=False))


class NovelToDramaV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="NovelToDramaV3Node",
            display_name="Novel to Drama [V3]",
            category="api node/workflow/Drama",
            description="Complete workflow: Chinese novel -> English drama scenes with audio.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("novel_text", multiline=True, default="", tooltip="Novel text to analyze."),
                IO.Int.Input("num_scenes", default=10, min=1, max=50, step=1),
                IO.Combo.Input("text_model", options=["deepseek-chat", "gpt-4o", "claude-3-5-sonnet-20241022"], default="deepseek-chat"),
                IO.Combo.Input("target_language", options=["english", "chinese"], default="english"),
                IO.Combo.Input("art_style", options=["cinematic", "anime", "realistic", "artistic"], default="cinematic"),
            ],
            outputs=[IO.String.Output("scenes_json"), IO.String.Output("summary"), IO.Float.Output("total_cost")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", novel_text: str = "", num_scenes: int = 10, text_model: str = "deepseek-chat", target_language: str = "english", art_style: str = "cinematic"):
        validate_string(novel_text, field_name="novel_text")
        key = validate_api_key(api_key)
        lang_instruction = "使用中文" if target_language == "chinese" else "Use English"
        prompt = f"""{lang_instruction}分析以下小说文本，提取{num_scenes}个关键场景用于制作漫剧视频。

对于每个场景，提供：
1. scene_number: 场景编号
2. title: 场景标题
3. description: 场景描述（人物、动作、环境）
4. characters: 出场人物列表
5. mood: 场景氛围（emotional/suspenseful/romantic/action/peaceful/dramatic/melancholic/upbeat/tense）
6. dialogue: 关键对话或独白（用于配音，包含情感标签如 (laughs), (sighs)）
7. visual_prompt: 用于生成图像的详细英文提示词，{art_style} style
8. camera_movement: 镜头运动建议

小说文本：
{novel_text}"""
        schema = {
            "type": "object",
            "properties": {
                "scenes": {"type": "array", "items": {"type": "object", "properties": {"scene_number": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}, "characters": {"type": "array", "items": {"type": "string"}}, "mood": {"type": "string"}, "dialogue": {"type": "string"}, "visual_prompt": {"type": "string"}, "camera_movement": {"type": "string"}}}},
                "summary": {"type": "string"}
            }
        }
        JSON_SCHEMA_MODELS = {"gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "claude-3-5-sonnet-20241022"}
        if text_model in JSON_SCHEMA_MODELS:
            response_format = {"type": "json_schema", "json_schema": {"name": "novel_scenes", "schema": schema}}
        else:
            response_format = {"type": "json_object"}
        request = TextGenerationRequest(model=text_model, messages=[ChatMessage(role="user", content=prompt)], temperature=0.7, response_format=response_format)
        response: TextGenerationResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"), data=request, response_model=TextGenerationResponse, api_key=key, wait_label="Analyzing novel", estimated_duration=20)
        text = extract_text_content(response.choices[0].message.content) if response.choices else ""
        if not text:
            return IO.NodeOutput("", "Empty response from API", 0.0)
        pricing = {"deepseek-chat": {"input": 0.00014, "output": 0.00028}, "gpt-4o": {"input": 0.0025, "output": 0.01}, "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015}}
        rates = pricing.get(text_model, pricing["deepseek-chat"])
        pt = response.usage.prompt_tokens
        ct = response.usage.completion_tokens
        cost = (pt / 1000 * rates["input"]) + (ct / 1000 * rates["output"])
        data = parse_json_safe(text, "scenes")
        summary = data.get("summary", "")
        return IO.NodeOutput(text, summary, cost)


class SceneImageGeneratorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="SceneImageGeneratorV3Node",
            display_name="Scene Image Generator [V3]",
            category="api node/workflow/Drama",
            description="Generate images for all scenes in batch. Supports character consistency with Kling.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("scenes_json", multiline=True, default="", tooltip="Scenes JSON from Novel to Drama."),
                IO.Combo.Input("image_model", options=["flux-pro", "ideogram-v3", "kling-v2", "dall-e-3"], default="flux-pro"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Int.Input("max_scenes", default=10, min=1, max=50, step=1),
                IO.Image.Input("ref_image", optional=True, tooltip="Reference image for character consistency (Kling only)."),
                IO.String.Input("ref_image_url", default="", multiline=False, optional=True, tooltip="Or provide a reference image URL (Kling only)."),
                IO.Combo.Input("image_reference", options=["none", "subject", "face"], default="none", tooltip="Subject: keep character appearance. Face: keep facial features only. Kling only."),
                IO.Float.Input("image_fidelity", default=0.5, min=0.0, max=1.0, step=0.01, tooltip="Reference image intensity. Kling only."),
                IO.Float.Input("human_fidelity", default=0.45, min=0.0, max=1.0, step=0.01, tooltip="Subject similarity strength. Kling only."),
            ],
            outputs=[IO.String.Output("images_json"), IO.String.Output("summary")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", scenes_json: str = "", image_model: str = "flux-pro", aspect_ratio: str = "16:9", max_scenes: int = 10, ref_image=None, ref_image_url: str = "", image_reference: str = "none", image_fidelity: float = 0.5, human_fidelity: float = 0.45):
        key = validate_api_key(api_key)
        scenes_data = parse_json_safe(scenes_json, "scenes_json")
        scenes = scenes_data.get("scenes", [])[:max_scenes]
        if not scenes:
            return IO.NodeOutput(json.dumps({"images": []}), "No scenes to process")

        resolved_ref = None
        if image_model == "kling-v2" and image_reference != "none":
            resolved_ref = prepare_image_input(image=ref_image, image_url=ref_image_url)

        ctx = AsyncWorkflowContext()
        results = []
        total = len(scenes)

        ctx.start_progress("image_batch", total, "image")

        for idx, scene in enumerate(scenes):
            scene_number = scene.get("scene_number", 0)
            prompt = scene.get("visual_prompt", "")
            is_last = (idx == total - 1)

            if not prompt:
                results.append({"scene_number": scene_number, "image_url": "", "visual_prompt": prompt, "status": "skipped", "reason": "no_prompt"})
                ctx.update_progress("image_batch", f"Scene {scene_number}", completed=idx + 1)
                continue

            skip_scene = {
                "scene_number": scene_number,
                "visual_prompt": prompt,
                "image_url": scene.get("image_url", ""),
                "scene_type": scene.get("scene_type", ""),
                "skip_image": scene.get("skip_image", False),
            }
            skip_reason = ctx.should_skip_generation("image", skip_scene)
            if skip_reason:
                results.append({"scene_number": scene_number, "image_url": "", "visual_prompt": prompt, "status": "skipped", "reason": skip_reason})
                ctx.update_progress("image_batch", f"Scene {scene_number}", completed=idx + 1)
                continue

            content_key = f"image:{prompt}:{image_model}:{aspect_ratio}"
            cached_url = ctx.check_content_duplicate("image", content_key)
            if cached_url:
                results.append({"scene_number": scene_number, "image_url": cached_url, "visual_prompt": prompt, "status": "success", "reason": "deduplicated"})
                ctx.update_progress("image_batch", f"Scene {scene_number}", completed=idx + 1)
                continue

            try:
                if image_model == "kling-v2":
                    has_ref = image_reference != "none" and resolved_ref
                    request = KlingImageGenRequest(
                        model_name="kling-v2", prompt=prompt, aspect_ratio=aspect_ratio, n=1,
                        image=resolved_ref if has_ref else None,
                        image_reference=image_reference if has_ref else None,
                        image_fidelity=image_fidelity if has_ref else None,
                        human_fidelity=human_fidelity if has_ref else None,
                    )
                    submit: KlingSubmitResponse = await sync_op(
                        cls, endpoint=ApiEndpoint(path=KLING_IMAGE_GEN, method="POST"),
                        data=request, response_model=KlingSubmitResponse, api_key=key,
                        wait_label=f"Submitting image {idx+1}", estimated_duration=5,
                    )
                    task_id = submit.data.task_id
                    img_url = ""
                    if task_id:
                        poll_response: KlingPollResponse = await poll_op(
                            cls, poll_endpoint=ApiEndpoint(path=KLING_IMAGE_GEN_POLL.format(task_id), method="GET"),
                            response_model=KlingPollResponse, status_extractor=kling_status_extractor,
                            api_key=key, completed_statuses=["succeed"], failed_statuses=["failed"],
                            queued_statuses=["submitted", "processing"], poll_interval=3.0,
                            max_poll_attempts=200, estimated_duration=60,
                        )
                        if poll_response.data and poll_response.data.task_result and poll_response.data.task_result.images:
                            img_url = poll_response.data.task_result.images[0].url
                elif image_model == "flux-pro":
                    payload = {"prompt": prompt, "image_size": "landscape_16_9" if aspect_ratio == "16:9" else "portrait_9_16" if aspect_ratio == "9:16" else "square", "num_images": 1, "enable_safety_checker": True, "output_format": "jpeg", "sync": True}
                    response = await sync_op_raw(cls, endpoint=ApiEndpoint(path="/fal-ai/flux-pro", method="POST"), data=payload, api_key=key, wait_label=f"Image {idx+1}/{total}", estimated_duration=15)
                    images = response.get("images", []) if isinstance(response, dict) else []
                    img_url = images[0].get("url", "") if images and isinstance(images[0], dict) else ""
                elif image_model == "ideogram-v3":
                    _ideo_ar_map = {"16:9": "ASPECT_16_9", "9:16": "ASPECT_9_16", "1:1": "ASPECT_1_1"}
                    payload = {"prompt": prompt, "aspect_ratio": _ideo_ar_map.get(aspect_ratio, "ASPECT_16_9"), "model": "ideogram-v3", "output_format": "jpeg", "enable_safety_checker": True, "sync": True}
                    response = await sync_op_raw(cls, endpoint=ApiEndpoint(path="/v1/ideogram/generate", method="POST"), data=payload, api_key=key, wait_label=f"Image {idx+1}/{total}", estimated_duration=12)
                    data_list = response.get("data", []) if isinstance(response, dict) else []
                    img_url = data_list[0].get("url", "") if data_list and isinstance(data_list[0], dict) else ""
                else:
                    payload = {"prompt": prompt, "model": "dall-e-3", "size": "1792x1024" if aspect_ratio == "16:9" else "1024x1792" if aspect_ratio == "9:16" else "1024x1024"}
                    response = await sync_op_raw(cls, endpoint=ApiEndpoint(path="/v1/images/generations", method="POST"), data=payload, api_key=key, wait_label=f"Image {idx+1}/{total}", estimated_duration=15)
                    data_list = response.get("data", []) if isinstance(response, dict) else []
                    img_url = data_list[0].get("url", "") if data_list and isinstance(data_list[0], dict) else ""

                results.append({"scene_number": scene_number, "image_url": img_url, "visual_prompt": prompt, "status": "success"})
                ctx.store_content_duplicate("image", content_key, img_url)
                ctx.record_result(True)
                await ctx.apply_smart_delay("image", is_last=is_last)

            except Exception as e:
                ctx.record_result(False, is_rate_limit=_is_rate_limit_error(e))
                results.append({"scene_number": scene_number, "image_url": "", "visual_prompt": prompt, "status": f"error: {e}"})

            ctx.update_progress("image_batch", f"Scene {scene_number}", completed=idx + 1)

        ctx.finish_progress("image_batch")
        ctx.flush_dedup()

        successful = sum(1 for r in results if r["status"] == "success" and r.get("reason") != "deduplicated")
        deduplicated = sum(1 for r in results if r.get("reason") == "deduplicated")
        skipped = sum(1 for r in results if "skipped" in r["status"])
        summary = f"Generated {successful}/{len(results)} images (dedup: {deduplicated}, skipped: {skipped})"

        output = json.dumps({"images": results}, ensure_ascii=False, indent=2)
        return IO.NodeOutput(output, summary)


class SceneVideoGeneratorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="SceneVideoGeneratorV3Node",
            display_name="Scene Video Generator [V3]",
            category="api node/workflow/Drama",
            description="Generate videos for all scenes in batch. Supports storyboard combine mode with Kling.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("images_json", multiline=True, default="", tooltip="Images JSON from Scene Image Generator."),
                IO.Combo.Input("video_model", options=["veo-3.1", "kling-v2", "vidu2", "hailuo"], default="kling-v2"),
                IO.Combo.Input("duration", options=["5", "10"], default="5"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Combo.Input("storyboard_mode", options=["disabled", "combine_scenes"], default="disabled", tooltip="combine_scenes: merge all scenes into one Kling storyboard video."),
            ],
            outputs=[IO.String.Output("videos_json"), IO.String.Output("summary")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", images_json: str = "", video_model: str = "kling-v2", duration: str = "5", aspect_ratio: str = "16:9", storyboard_mode: str = "disabled"):
        key = validate_api_key(api_key)
        images_data = parse_json_safe(images_json, "images_json")
        images = images_data.get("images", [])
        if not images:
            return IO.NodeOutput(json.dumps({"videos": []}), "No images to process")

        if storyboard_mode == "combine_scenes" and video_model == "kling-v2":
            return await cls._execute_combine_storyboard(key, images, duration, aspect_ratio)

        if storyboard_mode == "combine_scenes" and video_model != "kling-v2":
            logger.warning(f"[SCENE_VIDEO] storyboard_mode='combine_scenes' requires kling-v2, got '{video_model}'; ignoring storyboard_mode")

        ctx = AsyncWorkflowContext()
        results = []
        total = len(images)

        ctx.start_progress("video_batch", total, "video")

        for idx, img in enumerate(images):
            scene_number = img.get("scene_number", 0)
            image_url = img.get("image_url", "")
            is_last = (idx == total - 1)

            if not image_url:
                results.append({"scene_number": scene_number, "video_url": "", "status": "skipped", "reason": "no_image"})
                ctx.update_progress("video_batch", f"Scene {scene_number}", completed=idx + 1)
                continue

            skip_scene = {
                "scene_number": scene_number,
                "image_url": image_url,
                "video_url": img.get("video_url", ""),
                "scene_type": img.get("scene_type", ""),
                "skip_video": img.get("skip_video", False),
            }
            skip_reason = ctx.should_skip_generation("video", skip_scene)
            if skip_reason:
                results.append({"scene_number": scene_number, "video_url": "", "status": "skipped", "reason": skip_reason})
                ctx.update_progress("video_batch", f"Scene {scene_number}", completed=idx + 1)
                continue

            content_key = f"video:{image_url}:{video_model}:{duration}"
            cached_url = ctx.check_content_duplicate("video", content_key)
            if cached_url:
                results.append({"scene_number": scene_number, "video_url": cached_url, "status": "success", "reason": "deduplicated"})
                ctx.update_progress("video_batch", f"Scene {scene_number}", completed=idx + 1)
                continue

            payload = {"prompt": "Animate this scene with natural movement and atmosphere", "image": image_url, "duration": duration, "aspect_ratio": aspect_ratio}

            try:
                if video_model == "kling-v2":
                    payload["model_name"] = "kling-v2-master"
                    payload["cfg_scale"] = 0.5
                    submit = await sync_op_raw(cls, endpoint=ApiEndpoint(path=KLING_IMAGE2VIDEO, method="POST"), data=payload, api_key=key, wait_label=f"Submitting video {idx+1}", estimated_duration=5)
                    task_data = submit.get("data", {}) if isinstance(submit, dict) else {}
                    task_id = task_data.get("task_id", "") if isinstance(task_data, dict) else ""
                    if task_id:
                        poll_result = await poll_op_raw(cls, poll_endpoint=ApiEndpoint(path=KLING_IMAGE2VIDEO_POLL.format(task_id), method="GET"), status_extractor=lambda r: r.get("data", {}).get("task_status") if isinstance(r, dict) and isinstance(r.get("data"), dict) else None, api_key=key, completed_statuses=["succeed"], failed_statuses=["failed"], queued_statuses=["submitted", "processing"], poll_interval=10.0, max_poll_attempts=120, estimated_duration=120)
                        tr = poll_result.get("data", {}).get("task_result", {}) if isinstance(poll_result, dict) else {}
                        videos = tr.get("videos", []) if isinstance(tr, dict) else []
                        video_url = videos[0].get("url", "") if videos and isinstance(videos[0], dict) else ""
                    else:
                        video_url = ""
                elif video_model == "vidu2":
                    payload["model"] = "vidu2"
                    _vidu_duration_map = {"5": "4", "10": "8"}
                    payload["duration"] = _vidu_duration_map.get(str(payload.get("duration", "5")), "4")
                    _vidu_img = payload.pop("image", "")
                    if _vidu_img:
                        payload["image_url"] = _vidu_img
                    submit = await sync_op_raw(cls, endpoint=ApiEndpoint(path="/v1/videos/vidu/image-to-video", method="POST"), data=payload, api_key=key, wait_label=f"Submitting video {idx+1}", estimated_duration=5)
                    task_data = submit.get("data", {}) if isinstance(submit, dict) else {}
                    task_id = task_data.get("task_id", "") if isinstance(task_data, dict) else ""
                    if task_id:
                        poll_result = await poll_op_raw(cls, poll_endpoint=ApiEndpoint(path=f"/v1/videos/vidu/{task_id}", method="GET"), status_extractor=lambda r: r.get("data", {}).get("task_status") if isinstance(r, dict) and isinstance(r.get("data"), dict) else r.get("status"), api_key=key, completed_statuses=["success", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "created"], poll_interval=10.0, max_poll_attempts=120, estimated_duration=120)
                        video_url = poll_result.get("data", {}).get("video_url", "") if isinstance(poll_result, dict) else ""
                    else:
                        video_url = ""
                elif video_model == "hailuo":
                    payload["model"] = "T2V-01-Director"
                    payload["first_frame_image"] = image_url
                    payload.pop("image", None)
                    payload.pop("duration", None)
                    payload.pop("aspect_ratio", None)
                    submit = await sync_op_raw(cls, endpoint=ApiEndpoint(path="/v1/video/generation", method="POST"), data=payload, api_key=key, wait_label=f"Submitting video {idx+1}", estimated_duration=5)
                    task_id = submit.get("task_id", "") if isinstance(submit, dict) else ""
                    if task_id:
                        poll_result = await poll_op_raw(cls, poll_endpoint=ApiEndpoint(path=f"/v1/video/generation/{task_id}", method="GET"), status_extractor=lambda r: r.get("status") if isinstance(r, dict) else None, api_key=key, completed_statuses=["success", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing"], poll_interval=10.0, max_poll_attempts=120, estimated_duration=120)
                        video_url = poll_result.get("video_url", "") if isinstance(poll_result, dict) else ""
                    else:
                        video_url = ""
                else:
                    payload["aspectRatio"] = aspect_ratio
                    payload.pop("aspect_ratio", None)
                    payload.pop("duration", None)
                    submit = await sync_op_raw(cls, endpoint=ApiEndpoint(path=f"/veo/{video_model}/generate", method="POST"), data=payload, api_key=key, wait_label=f"Submitting video {idx+1}", estimated_duration=5)
                    status_url = submit.get("status_url", "") if isinstance(submit, dict) else ""
                    if status_url:
                        poll_result = await poll_op_raw(cls, poll_endpoint=ApiEndpoint(path=status_url, method="GET"), status_extractor=lambda r: r.get("status") if isinstance(r, dict) else None, api_key=key, completed_statuses=["succeeded", "COMPLETED"], failed_statuses=["failed", "canceled"], queued_statuses=["queued", "processing", "running"], poll_interval=10.0, max_poll_attempts=120, estimated_duration=120)
                        video_url = poll_result.get("video", {}).get("url", "") if isinstance(poll_result, dict) and isinstance(poll_result.get("video"), dict) else ""
                    else:
                        video_url = ""

                results.append({"scene_number": scene_number, "video_url": video_url, "status": "success"})
                ctx.store_content_duplicate("video", content_key, video_url)
                ctx.record_result(True)
                await ctx.apply_smart_delay("video", is_last=is_last)

            except Exception as e:
                ctx.record_result(False, is_rate_limit=_is_rate_limit_error(e))
                results.append({"scene_number": scene_number, "video_url": "", "status": f"error: {e}"})

            ctx.update_progress("video_batch", f"Scene {scene_number}", completed=idx + 1)

        ctx.finish_progress("video_batch")
        ctx.flush_dedup()

        successful = sum(1 for r in results if r["status"] == "success" and r.get("reason") != "deduplicated")
        deduplicated = sum(1 for r in results if r.get("reason") == "deduplicated")
        skipped = sum(1 for r in results if "skipped" in r["status"])
        summary = f"Generated {successful}/{len(results)} videos (dedup: {deduplicated}, skipped: {skipped})"

        output = json.dumps({"videos": results}, ensure_ascii=False, indent=2)
        return IO.NodeOutput(output, summary)

    @classmethod
    async def _execute_combine_storyboard(cls, key: str, images: list, duration: str, aspect_ratio: str):
        num_scenes = len(images)
        total_duration = int(duration)
        seg_duration = total_duration // num_scenes
        if seg_duration < 1:
            raise Exception(f"Duration {total_duration}s too short for {num_scenes} scenes.")
        remainder = total_duration - seg_duration * num_scenes

        multi_prompt = []
        for i, img in enumerate(images):
            prompt = img.get("visual_prompt", "") or f"Scene {img.get('scene_number', i+1)}"
            d = seg_duration + (1 if i < remainder else 0)
            multi_prompt.append(KlingMultiPromptItem(index=i + 1, prompt=prompt[:512], duration=str(d)))

        combined_prompt = " ; ".join(mp.prompt for mp in multi_prompt)
        request = KlingText2VideoRequest(
            model_name="kling-v2-master", prompt=combined_prompt,
            duration=duration, aspect_ratio=aspect_ratio,
            cfg_scale=0.5, mode="std",
            multi_shot=True, shot_type="customize", multi_prompt=multi_prompt,
        )

        submit: KlingSubmitResponse = await sync_op(
            cls, endpoint=ApiEndpoint(path=KLING_TEXT2VIDEO, method="POST"),
            data=request, response_model=KlingSubmitResponse, api_key=key,
            wait_label="Submitting storyboard video", estimated_duration=5,
        )
        task_id = submit.data.task_id
        if not task_id:
            raise Exception(f"Kling storyboard submit failed: {submit}")

        poll_response: KlingPollResponse = await poll_op(
            cls, poll_endpoint=ApiEndpoint(path=KLING_TEXT2VIDEO_POLL.format(task_id), method="GET"),
            response_model=KlingPollResponse, status_extractor=kling_status_extractor,
            api_key=key, completed_statuses=["succeed"], failed_statuses=["failed"],
            queued_statuses=["submitted", "processing"], poll_interval=10.0,
            max_poll_attempts=240, estimated_duration=180,
        )
        video_url = ""
        if poll_response.data and poll_response.data.task_result and poll_response.data.task_result.videos:
            video_url = poll_response.data.task_result.videos[0].url
        if not video_url:
            raise Exception("Kling storyboard task completed but no video URL found.")

        scene_numbers = [img.get("scene_number", i + 1) for i, img in enumerate(images)]
        results = [{"scene_number": sn, "video_url": video_url, "status": "success", "storyboard": True} for sn in scene_numbers]
        summary = f"Combined {num_scenes} scenes into 1 storyboard video"
        return IO.NodeOutput(json.dumps({"videos": results}, ensure_ascii=False, indent=2), summary)


class SceneAudioGeneratorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="SceneAudioGeneratorV3Node",
            display_name="Scene Audio Generator [V3]",
            category="api node/workflow/Drama",
            description="Generate audio (dialogue + music) for all scenes.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("scenes_json", multiline=True, default="", tooltip="Scenes JSON from Novel to Drama."),
                IO.Combo.Input("voice_id", options=["male-qn-qingse", "male-qn-jingying", "female-shaonv", "female-yujie", "presenter_male", "presenter_female"], default="male-qn-jingying"),
                IO.Boolean.Input("generate_music", default=True),
                IO.Int.Input("max_scenes", default=10, min=1, max=50, step=1),
            ],
            outputs=[IO.String.Output("audio_json"), IO.String.Output("summary")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", scenes_json: str = "", voice_id: str = "male-qn-jingying", generate_music: bool = True, max_scenes: int = 10):
        key = validate_api_key(api_key)
        scenes_data = parse_json_safe(scenes_json, "scenes_json")
        scenes = scenes_data.get("scenes", [])[:max_scenes]
        if not scenes:
            return IO.NodeOutput(json.dumps({"audio": []}), "No scenes to process")

        ctx = AsyncWorkflowContext()
        mood_prompts = {"emotional": "emotional piano, touching", "suspenseful": "suspenseful thriller, mysterious", "romantic": "romantic love theme, soft", "action": "action movie, energetic", "peaceful": "peaceful ambient, calm", "dramatic": "dramatic orchestral, cinematic", "melancholic": "melancholic sad, touching", "upbeat": "upbeat energetic, positive", "tense": "tense dramatic, building"}

        results = []
        total = len(scenes)

        ctx.start_progress("audio_batch", total, "audio")

        for idx, scene in enumerate(scenes):
            scene_number = scene.get("scene_number", 0)
            dialogue = scene.get("dialogue", "")
            mood = scene.get("mood", "emotional")
            is_last = (idx == total - 1)

            result = {"scene_number": scene_number, "dialogue_url": "", "music_url": "", "status": "pending"}
            dialogue_outcome = None
            music_outcome = None

            if dialogue:
                skip_scene = {
                    "scene_number": scene_number,
                    "dialogue": dialogue,
                    "audio_url": scene.get("audio_url", ""),
                    "scene_type": scene.get("scene_type", ""),
                    "skip_audio": scene.get("skip_audio", False),
                }
                skip_reason = ctx.should_skip_generation("audio", skip_scene)
                if skip_reason:
                    dialogue_outcome = "skipped"
                else:
                    content_key = f"audio:{dialogue}:{voice_id}"
                    cached_url = ctx.check_content_duplicate("audio", content_key)
                    if cached_url:
                        result["dialogue_url"] = cached_url
                        dialogue_outcome = "dedup"
                    else:
                        try:
                            payload = {"model": "speech-01-turbo", "text": dialogue, "voice": voice_id, "audio_setting": {"sample_rate": 32000, "format": "mp3"}}
                            response = await sync_op_raw(cls, endpoint=ApiEndpoint(path="/v1/audio/speech", method="POST"), data=payload, api_key=key, wait_label=f"Dialogue {idx+1}", estimated_duration=10)
                            result["dialogue_url"] = response.get("audio_url", "") if isinstance(response, dict) else ""
                            ctx.store_content_duplicate("audio", content_key, result["dialogue_url"])
                            ctx.record_result(True)
                            await ctx.apply_smart_delay("audio", is_last=is_last and not generate_music)
                            dialogue_outcome = "generated"
                        except Exception as e:
                            logger.error("Dialogue generation failed for scene %s: %s", scene_number, e)
                            ctx.record_result(False, is_rate_limit=_is_rate_limit_error(e))
                            dialogue_outcome = "error"

            if generate_music:
                prompt = mood_prompts.get(mood, mood_prompts["emotional"])

                skip_scene = {
                    "scene_number": scene_number,
                    "mood": mood,
                    "music_url": scene.get("music_url", ""),
                    "scene_type": scene.get("scene_type", ""),
                    "use_stock_music": scene.get("use_stock_music", False),
                    "skip_music": scene.get("skip_music", False),
                }
                skip_reason = ctx.should_skip_generation("music", skip_scene)
                if skip_reason:
                    music_outcome = "skipped"
                else:
                    content_key = f"music:{prompt}:{mood}"
                    cached_url = ctx.check_content_duplicate("music", content_key)
                    if cached_url:
                        result["music_url"] = cached_url
                        music_outcome = "dedup"
                    else:
                        try:
                            payload = {"prompt": prompt + ", instrumental background music", "mv": "chirp-v3-5", "make_instrumental": True}
                            submit = await sync_op_raw(cls, endpoint=ApiEndpoint(path="/suno/v3/generate", method="POST"), data=payload, api_key=key, wait_label=f"Submitting music {idx+1}", estimated_duration=5)
                            clips = submit.get("clips", []) if isinstance(submit, dict) else []
                            task_id = clips[0].get("id", "") if clips and isinstance(clips[0], dict) else ""
                            if task_id:
                                poll_result = await poll_op_raw(cls, poll_endpoint=ApiEndpoint(path=f"/suno/v3/generate/{task_id}", method="GET"), status_extractor=lambda r: (r.get("clips", [{}])[0].get("status") if isinstance(r, dict) and r.get("clips") and isinstance(r.get("clips", [{}])[0], dict) else None), api_key=key, completed_statuses=["complete", "completed"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "generating"], poll_interval=10.0, max_poll_attempts=60, estimated_duration=60)
                                clips = poll_result.get("clips", []) if isinstance(poll_result, dict) else []
                                result["music_url"] = clips[0].get("audio_url", "") if clips and isinstance(clips[0], dict) else ""
                            ctx.store_content_duplicate("music", content_key, result["music_url"])
                            ctx.record_result(True)
                            await ctx.apply_smart_delay("music", is_last=is_last)
                            music_outcome = "generated"
                        except Exception as e:
                            logger.error("Music generation failed for scene %s: %s", scene_number, e)
                            ctx.record_result(False, is_rate_limit=_is_rate_limit_error(e))
                            music_outcome = "error"

            has_dialogue = bool(result["dialogue_url"])
            has_music = bool(result["music_url"])
            dialogue_errored = dialogue_outcome == "error"
            music_errored = music_outcome == "error"

            if has_dialogue or has_music:
                if dialogue_errored or music_errored:
                    result["status"] = "partial_success"
                else:
                    result["status"] = "success"
            elif dialogue_errored or music_errored:
                result["status"] = "error"
            else:
                result["status"] = "skipped"

            results.append(result)
            ctx.update_progress("audio_batch", f"Scene {scene_number}", completed=idx + 1)

        ctx.finish_progress("audio_batch")
        ctx.flush_dedup()

        successful = sum(1 for r in results if r["status"] in ("success", "partial_success"))
        skipped = sum(1 for r in results if r["status"] == "skipped")
        errors = sum(1 for r in results if r["status"] == "error")
        summary = f"Generated audio for {successful}/{len(results)} scenes (skipped: {skipped}, errors: {errors})"

        output = json.dumps({"audio": results}, ensure_ascii=False, indent=2)
        return IO.NodeOutput(output, summary)


class DramaManifestV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="DramaManifestV3Node",
            display_name="Drama Manifest [V3]",
            category="api node/workflow/Drama",
            description="Create final manifest JSON combining all assets.",
            inputs=[
                IO.String.Input("scenes_json", multiline=True, default="", tooltip="Scenes JSON."),
                IO.String.Input("images_json", multiline=True, default="", tooltip="Images JSON."),
                IO.String.Input("videos_json", multiline=True, default="", tooltip="Videos JSON."),
                IO.String.Input("audio_json", multiline=True, default="", tooltip="Audio JSON."),
                IO.String.Input("title", default="Drama Video", multiline=False),
            ],
            outputs=[IO.String.Output("manifest_json"), IO.String.Output("summary")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=False,
        )

    @classmethod
    async def execute(cls, scenes_json: str = "", images_json: str = "", videos_json: str = "", audio_json: str = "", title: str = "Drama Video"):
        import time
        scenes = parse_json_safe(scenes_json, "scenes_json").get("scenes", [])
        images = parse_json_safe(images_json, "images_json").get("images", [])
        videos = parse_json_safe(videos_json, "videos_json").get("videos", [])
        audio = parse_json_safe(audio_json, "audio_json").get("audio", [])
        image_dict = {img["scene_number"]: img for img in images if isinstance(img, dict) and "scene_number" in img}
        video_dict = {vid["scene_number"]: vid for vid in videos if isinstance(vid, dict) and "scene_number" in vid}
        audio_dict = {aud["scene_number"]: aud for aud in audio if isinstance(aud, dict) and "scene_number" in aud}
        manifest = {"title": title, "created_at": time.strftime("%Y-%m-%d %H:%M:%S"), "total_scenes": len(scenes), "scenes": []}
        for scene in scenes:
            sn = scene.get("scene_number", 0)
            manifest["scenes"].append({"scene_number": sn, "title": scene.get("title", ""), "description": scene.get("description", ""), "characters": scene.get("characters", []), "mood": scene.get("mood", ""), "dialogue": scene.get("dialogue", ""), "visual_prompt": scene.get("visual_prompt", ""), "camera_movement": scene.get("camera_movement", ""), "image_url": image_dict.get(sn, {}).get("image_url", ""), "video_url": video_dict.get(sn, {}).get("video_url", ""), "dialogue_url": audio_dict.get(sn, {}).get("dialogue_url", ""), "music_url": audio_dict.get(sn, {}).get("music_url", "")})
        manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)
        return IO.NodeOutput(manifest_json, f"Manifest created: {len(scenes)} scenes")


class StoryboardVideoV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="StoryboardVideoV3Node",
            display_name="Storyboard Video [V3]",
            category="api node/workflow/Storyboard",
            description="Generate a Kling storyboard video from segment definitions. No image generation step needed.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("segments_json", multiline=True, default="", tooltip='JSON array: [{"prompt":"...","duration":5}, ...]. Total duration must match video duration.'),
                IO.Combo.Input("model_name", options=["kling-v2-master", "kling-v2-1-master", "kling-v2-5-turbo", "kling-v3"], default="kling-v2-master"),
                IO.Combo.Input("duration", options=["5", "10"], default="5", tooltip="Total video duration. Must equal sum of segment durations."),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Float.Input("cfg_scale", default=0.5, min=0.0, max=1.0, step=0.1),
                IO.Combo.Input("mode", options=["std", "pro"], default="std"),
                IO.String.Input("negative_prompt", multiline=True, default="", optional=True, tooltip="Optional negative prompt."),
                IO.String.Input("camera_control_json", multiline=True, default="", optional=True, tooltip="Camera control JSON from Kling Camera Control node."),
            ],
            outputs=[IO.Video.Output("video"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", segments_json: str = "", model_name: str = "kling-v2-master", duration: str = "5", aspect_ratio: str = "16:9", cfg_scale: float = 0.5, mode: str = "std", negative_prompt: str = "", camera_control_json: str = ""):
        validate_string(segments_json, field_name="segments_json")
        key = validate_api_key(api_key)

        try:
            parsed = json.loads(segments_json)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid segments_json: {e}")

        if isinstance(parsed, dict) and "segments" in parsed:
            segments = parsed["segments"]
        elif isinstance(parsed, list):
            segments = parsed
        else:
            raise Exception("segments_json must be a JSON array or a dict with a 'segments' key.")

        if not isinstance(segments, list) or len(segments) < 2:
            raise Exception("segments_json must be a JSON array with at least 2 segments.")
        if len(segments) > 6:
            raise Exception("Maximum 6 storyboard segments allowed.")

        total_sb_duration = 0
        multi_prompt = []
        for i, seg in enumerate(segments):
            if not isinstance(seg, dict):
                raise Exception(f"Segment {i+1} must be a JSON object.")
            prompt = seg.get("prompt", "")
            if not prompt.strip():
                raise Exception(f"Segment {i+1} prompt is empty.")
            if len(prompt) > 512:
                raise Exception(f"Segment {i+1} prompt exceeds 512 characters.")
            d = int(seg.get("duration", 5))
            if d < 1 or d > 15:
                raise Exception(f"Segment {i+1} duration must be 1-15 seconds.")
            multi_prompt.append(KlingMultiPromptItem(index=i + 1, prompt=prompt, duration=str(d)))
            total_sb_duration += d

        if total_sb_duration != int(duration):
            raise Exception(f"Total segment duration ({total_sb_duration}s) must equal video duration ({duration}s).")

        combined_prompt = " ; ".join(mp.prompt for mp in multi_prompt)
        camera_control = _parse_camera_control(camera_control_json)

        request = KlingText2VideoRequest(
            model_name=model_name, prompt=combined_prompt,
            duration=duration, aspect_ratio=aspect_ratio,
            cfg_scale=cfg_scale, mode=mode,
            negative_prompt=negative_prompt or None,
            multi_shot=True, shot_type="customize", multi_prompt=multi_prompt,
            camera_control=camera_control,
        )

        video_output, task_id = await _kling_submit_poll_download(
            cls, KLING_TEXT2VIDEO, KLING_TEXT2VIDEO_POLL, request, key,
            max_poll_attempts=240, estimated_duration=180)
        return IO.NodeOutput(video_output, task_id)


CAMERA_PRESETS: Dict[str, KlingCameraConfig] = {
    "dolly-in": KlingCameraConfig(zoom=-0.3),
    "dolly-out": KlingCameraConfig(zoom=0.3),
    "pan-left": KlingCameraConfig(horizontal=-0.5),
    "pan-right": KlingCameraConfig(horizontal=0.5),
    "tilt-up": KlingCameraConfig(vertical=0.5),
    "tilt-down": KlingCameraConfig(vertical=-0.5),
    "static": KlingCameraConfig(),
    "orbit": KlingCameraConfig(pan=0.3, tilt=0.1),
    "tracking": KlingCameraConfig(horizontal=0.4, zoom=-0.1),
    "handheld": KlingCameraConfig(horizontal=0.1, vertical=0.05, roll=0.02),
    "crane-up": KlingCameraConfig(vertical=0.4, tilt=-0.2),
    "crane-down": KlingCameraConfig(vertical=-0.4, tilt=0.2),
    "zoom-in": KlingCameraConfig(zoom=-0.4),
    "zoom-out": KlingCameraConfig(zoom=0.4),
    "slow-push": KlingCameraConfig(zoom=-0.15),
    "reveal": KlingCameraConfig(pan=0.3, zoom=-0.2),
}

MINIMAX_VOICE_OPTIONS = [
    "minimax-male-qn-qingse",
    "minimax-male-qn-jingying",
    "minimax-female-shaonv",
    "minimax-female-yujie",
    "minimax-presenter_male",
    "minimax-presenter_female",
    "minimax-audiobook_male_1",
    "minimax-audiobook_male_2",
]

ALL_VOICE_OPTIONS = MINIMAX_VOICE_OPTIONS + [
    "kling-alloy", "kling-echo", "kling-fable", "kling-onyx", "kling-nova", "kling-shimmer",
]


def _extract_setting_from_master(master_prompt: str) -> str:
    m_setting = re.search(r'(?:2\.\s*)?SETTING[:\s]*\n(.+?)(?=\n\d\.\s|\Z)', master_prompt, re.DOTALL | re.IGNORECASE)
    m_chars = re.search(r'(?:1\.\s*)?CHARACTERS[:\s]*\n(.+?)(?=\n\d\.\s|\Z)', master_prompt, re.DOTALL | re.IGNORECASE)
    setting = m_setting.group(1).strip()[:256] if m_setting else ""
    chars = m_chars.group(1).strip()[:256] if m_chars else ""
    if setting or chars:
        parts = []
        if setting:
            parts.append(f"Scene setting: {setting}")
        if chars:
            parts.append(f"Characters: {chars}")
        return ". ".join(parts)
    return ""


def _map_camera_text_to_preset(camera_text: str) -> KlingCameraConfig | None:
    if not camera_text:
        return None
    text_lower = camera_text.lower().strip()
    for key, config in CAMERA_PRESETS.items():
        if key.replace("-", " ") in text_lower or key in text_lower:
            return config
    if "dolly" in text_lower and "in" in text_lower:
        return CAMERA_PRESETS["dolly-in"]
    if "dolly" in text_lower and "out" in text_lower:
        return CAMERA_PRESETS["dolly-out"]
    if "track" in text_lower:
        return CAMERA_PRESETS["tracking"]
    if "handheld" in text_lower or "shake" in text_lower:
        return CAMERA_PRESETS["handheld"]
    if "crane" in text_lower and "up" in text_lower:
        return CAMERA_PRESETS["crane-up"]
    if "crane" in text_lower and "down" in text_lower:
        return CAMERA_PRESETS["crane-down"]
    if "zoom" in text_lower and "in" in text_lower:
        return CAMERA_PRESETS["zoom-in"]
    if "zoom" in text_lower and "out" in text_lower:
        return CAMERA_PRESETS["zoom-out"]
    if "pan" in text_lower and "left" in text_lower:
        return CAMERA_PRESETS["pan-left"]
    if "pan" in text_lower and "right" in text_lower:
        return CAMERA_PRESETS["pan-right"]
    if "tilt" in text_lower and "up" in text_lower:
        return CAMERA_PRESETS["tilt-up"]
    if "tilt" in text_lower and "down" in text_lower:
        return CAMERA_PRESETS["tilt-down"]
    if "orbit" in text_lower:
        return CAMERA_PRESETS["orbit"]
    if "reveal" in text_lower:
        return CAMERA_PRESETS["reveal"]
    if "push" in text_lower:
        return CAMERA_PRESETS["slow-push"]
    if "static" in text_lower or "wide" in text_lower or "still" in text_lower:
        return CAMERA_PRESETS["static"]
    return None


def _parse_camera_values_from_segment(seg: dict) -> KlingCameraConfig | None:
    cv = seg.get("camera_values")
    if not cv or not isinstance(cv, dict):
        return None
    try:
        return KlingCameraConfig(
            horizontal=float(cv.get("horizontal", 0.0)),
            vertical=float(cv.get("vertical", 0.0)),
            pan=float(cv.get("pan", 0.0)),
            tilt=float(cv.get("tilt", 0.0)),
            roll=float(cv.get("roll", 0.0)),
            zoom=float(cv.get("zoom", 0.0)),
        )
    except (ValueError, TypeError):
        return None


async def _tts_generate_dialogue(cls, dialogue_text: str, voice: str, api_key: str) -> tuple[bytes, str]:
    if voice.startswith("kling-"):
        voice_id = voice[len("kling-"):]
        from ..apis.kling import KlingTTSRequest as _KlingTTSRequest, KLING_TTS
        request = _KlingTTSRequest(text=dialogue_text[:1000], voice_id=voice_id, voice_language="zh", voice_speed=1.0)
        response_dict = await sync_op_raw(
            cls, endpoint=ApiEndpoint(path=KLING_TTS, method="POST"),
            data=request, api_key=api_key,
            wait_label="Step 4/6: Synthesizing dialogue (Kling)", estimated_duration=10,
        )
        audio_url = ""
        if isinstance(response_dict, dict):
            data = response_dict.get("data", {})
            if isinstance(data, dict):
                audio_url = data.get("url", "")
                if not audio_url:
                    task_result = data.get("task_result", {})
                    if isinstance(task_result, dict):
                        audios = task_result.get("audio", [])
                        if audios and isinstance(audios[0], dict):
                            audio_url = audios[0].get("url", "")
        if not audio_url:
            raise Exception("Kling TTS returned no audio URL.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        return audio_bytesio.getvalue(), audio_url
    else:
        minimax_voice = voice.replace("minimax-", "") if voice.startswith("minimax-") else voice
        request = MinimaxTTSRequest(model="speech-01-turbo", text=dialogue_text, voice=minimax_voice, emotion="neutral", speed=1.0, format="mp3", sample_rate=32000)
        response: MinimaxTTSResponse = await sync_op(
            cls, endpoint=ApiEndpoint(path="/v1/audio/speech", method="POST"),
            data=request, response_model=MinimaxTTSResponse, api_key=api_key,
            wait_label="Step 4/6: Synthesizing dialogue (Minimax)", estimated_duration=10,
        )
        audio_url = response.audio_url
        if not audio_url:
            raise Exception("Minimax TTS returned no audio URL.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        return audio_bytesio.getvalue(), audio_url


def _ffmpeg_mix_video_audio(video_bytes: bytes, audio_bytes: bytes) -> bytes | None:
    if not shutil.which("ffmpeg"):
        logger.warning("[STORYBOARD_PRO] ffmpeg not found, skipping mix")
        return None
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = f"{tmpdir}/video.mp4"
        audio_path = f"{tmpdir}/audio.mp3"
        output_path = f"{tmpdir}/output.mp4"
        with open(video_path, "wb") as f:
            f.write(video_bytes)
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)
        cmd = ["ffmpeg", "-y", "-i", video_path, "-i", audio_path,
               "-c:v", "copy", "-c:a", "aac", "-shortest", output_path]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            if result.returncode != 0:
                logger.warning("[STORYBOARD_PRO] ffmpeg mix failed: %s", result.stderr.decode()[:200])
                return None
            with open(output_path, "rb") as f:
                return f.read()
        except subprocess.TimeoutExpired:
            logger.warning("[STORYBOARD_PRO] ffmpeg mix timed out")
            return None
        except Exception as e:
            logger.warning("[STORYBOARD_PRO] ffmpeg mix error: %s", e)
            return None


class StoryboardProV3Node(IO.ComfyNode):
    META_INSTRUCTION_A = """You are an expert visual director and storyboard supervisor. Analyze the provided reference images and story description, then produce a MASTER PROMPT that serves as the visual bible for an AI-generated storyboard video.

Your output must include these sections:

1. CHARACTERS — For each character visible in the reference images:
   - Name (if known) or descriptive label
   - Detailed physical appearance: gender presentation, age range, body type, skin tone, hair (color, length, style, texture), eye color, distinctive facial features
   - Default outfit/clothing with colors and materials
   - Key accessories or props
   - Personality impression

2. SETTING — The story world:
   - Primary location(s) described
   - Time period and time of day
   - Weather/atmosphere
   - Key environmental details (architecture, vegetation, lighting)
   - Color palette and mood

3. VISUAL STYLE — Cinematic direction:
   - Genre and tone
   - Camera style (handheld documentary / smooth cinematic / etc.)
   - Lighting style (natural / dramatic / noir / high-key)
   - Color grading (warm / cool / desaturated / vibrant)
   - Aspect ratio implications for framing

4. CONTINUITY RULES — What must stay consistent across all segments:
   - Character appearance consistency rules
   - Environmental continuity rules
   - Prop/object continuity rules
   - Lighting direction consistency

5. STORY ARC — Brief 1-sentence summary of each storyboard segment's narrative beat

Be extremely detailed and specific. This MASTER PROMPT will be used to generate video prompts for each storyboard segment. Quality of the final video depends entirely on the precision of this description.

Use English for all visual descriptions. Use Simplified Chinese for any dialogue or audio cues if the story is Chinese."""

    META_INSTRUCTION_B = """You are an expert Storyboard-to-Video Prompt Engineer. Given a MASTER PROMPT (character/scene visual bible), generate detailed video prompts for each storyboard segment.

For each segment, provide:
1. A highly detailed visual prompt (English) describing:
   - Character body motion and micro-expressions (be specific: "slowly raises her right hand", not "moves her hand")
   - Hair and clothing physics (swaying, fluttering, rippling)
   - Environmental dynamics (dust, rain, light changes, background motion)
   - Object interactions if any
   - Facial expression evolution
2. Camera movement (specific: "slow dolly-in from medium to close-up", "static wide shot", "handheld tracking")
3. Duration in seconds (must be realistic for the action described)
4. Negative prompt (artifacts to avoid)
5. Dialogue line (Simplified Chinese, the character's spoken line for this segment, or empty string if no dialogue)

Output a JSON array. Each element must have:
- "prompt": the detailed English visual prompt (max 512 characters)
- "camera": camera movement description
- "duration": integer seconds
- "negative": negative prompt
- "dialogue": character dialogue in Chinese (empty string if none)

Rules:
- Total duration of all segments must exactly equal the video duration
- Character descriptions must stay consistent with the MASTER PROMPT
- Each segment must feel like a natural continuation of the previous one
- Durations should vary based on content complexity (simple reaction: 2-3s, dialogue: 3-5s, action: 4-6s)
- Prompts must be concrete and visual, not vague or literary

Output ONLY the JSON array, no other text."""

    META_INSTRUCTION_B_CUSTOM_CAMERA = """You are an expert Storyboard-to-Video Prompt Engineer. Given a MASTER PROMPT (character/scene visual bible), generate detailed video prompts for each storyboard segment.

For each segment, provide:
1. A highly detailed visual prompt (English) describing:
   - Character body motion and micro-expressions (be specific: "slowly raises her right hand", not "moves her hand")
   - Hair and clothing physics (swaying, fluttering, rippling)
   - Environmental dynamics (dust, rain, light changes, background motion)
   - Object interactions if any
   - Facial expression evolution
2. Camera movement as numeric values:
   - horizontal: left(-) to right(+) typically -1.0 to 1.0
   - vertical: down(-) to up(+) typically -1.0 to 1.0
   - pan: left(-) to right(+) typically -1.0 to 1.0
   - tilt: down(-) to up(+) typically -1.0 to 1.0
   - roll: counter-clockwise(-) to clockwise(+) typically -1.0 to 1.0
   - zoom: zoom-in(-) to zoom-out(+) typically -1.0 to 1.0
3. Duration in seconds (must be realistic for the action described)
4. Negative prompt (artifacts to avoid)
5. Dialogue line (Simplified Chinese, the character's spoken line for this segment, or empty string if none)

Output a JSON array. Each element must have:
- "prompt": the detailed English visual prompt (max 512 characters)
- "camera_values": {"horizontal": 0.0, "vertical": 0.0, "pan": 0.0, "tilt": 0.0, "roll": 0.0, "zoom": 0.0}
- "duration": integer seconds
- "negative": negative prompt
- "dialogue": character dialogue in Chinese (empty string if none)

Rules:
- Total duration of all segments must exactly equal the video duration
- Character descriptions must stay consistent with the MASTER PROMPT
- Each segment must feel like a natural continuation of the previous one
- Durations should vary based on content complexity (simple reaction: 2-3s, dialogue: 3-5s, action: 4-6s)
- Camera values should be subtle; values above 0.5 create very fast movement
- Only the first segment's camera_values will be used as global camera control

Output ONLY the JSON array, no other text."""

    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="StoryboardProV3Node",
            display_name="Storyboard Pro [V3]",
            category="api node/workflow/Storyboard",
            description="One-click storyboard video generation: LLM analyzes characters → generates prompts → creates storyboard image → TTS dialogue → generates video → ffmpeg mix.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("story_description", multiline=True, default="", tooltip="One-sentence story description, e.g. 'A little fox accidentally wanders into a dark magical forest'"),
                IO.String.Input("character_image_urls", multiline=True, default="", tooltip="Character reference image URLs, one per line. From character cards or manual input."),
                IO.Combo.Input("image_reference", options=["subject", "face"], default="subject", tooltip="Subject: keep overall appearance. Face: keep facial features only."),
                IO.Float.Input("image_fidelity", default=0.5, min=0.0, max=1.0, step=0.01, tooltip="Reference image intensity."),
                IO.Float.Input("human_fidelity", default=0.45, min=0.0, max=1.0, step=0.01, tooltip="Subject similarity strength."),
                IO.Combo.Input("text_model", options=["gpt-4o", "gpt-4o-mini", "deepseek-chat", "claude-3-5-sonnet-20241022"], default="gpt-4o", tooltip="LLM model for prompt generation."),
                IO.Combo.Input("image_model", options=["kling-v2", "kling-v3", "flux-pro", "gpt-image"], default="kling-v2", tooltip="Image generation model for storyboard frame."),
                IO.Combo.Input("video_model", options=["kling-v2-master", "kling-v2-1-master", "kling-v2-5-turbo", "kling-v3"], default="kling-v2-master", tooltip="Video generation model."),
                IO.Int.Input("storyboard_count", default=4, min=2, max=6, step=1, tooltip="Number of storyboard segments (2-6)."),
                IO.Combo.Input("duration", options=["5", "10"], default="5", tooltip="Total video duration in seconds."),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Float.Input("cfg_scale", default=0.5, min=0.0, max=1.0, step=0.1),
                IO.Combo.Input("mode", options=["std", "pro"], default="std", tooltip="std=720p, pro=1080p"),
                IO.String.Input("negative_prompt", multiline=True, default="", optional=True, tooltip="Negative prompt for video generation."),
                IO.Combo.Input("sound", options=["off", "on"], default="off", optional=True, tooltip="Generate ambient audio for the video."),
                IO.Combo.Input("camera_style", options=["none", "simple", "custom"], default="none", tooltip="none=no camera control; simple=map LLM camera text to presets; custom=LLM outputs numeric camera values."),
                IO.Combo.Input("voice", options=ALL_VOICE_OPTIONS, default="minimax-male-qn-jingying", tooltip="Voice for dialogue TTS. minimax-* = Minimax voices, kling-* = Kling preset voices."),
                IO.Combo.Input("generate_dialogue", options=["off", "on"], default="off", tooltip="Generate dialogue audio via TTS and mix with video."),
            ],
            outputs=[
                IO.Video.Output("video"),
                IO.String.Output("master_prompt"),
                IO.String.Output("video_prompts"),
                IO.String.Output("storyboard_image_url"),
                IO.Audio.Output("dialogue_audio"),
                IO.String.Output("dialogue_text"),
            ],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", story_description: str = "", character_image_urls: str = "",
                      image_reference: str = "subject", image_fidelity: float = 0.5, human_fidelity: float = 0.45,
                      text_model: str = "gpt-4o", image_model: str = "kling-v2", video_model: str = "kling-v2-master",
                      storyboard_count: int = 4, duration: str = "5", aspect_ratio: str = "16:9",
                      cfg_scale: float = 0.5, mode: str = "std", negative_prompt: str = "", sound: str = "off",
                      camera_style: str = "none", voice: str = "minimax-male-qn-jingying", generate_dialogue: str = "off"):
        validate_string(story_description, field_name="story_description")
        key = validate_api_key(api_key)
        char_urls = [u.strip() for u in character_image_urls.strip().split("\n") if u.strip()]

        VISION_MODELS = {"gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022"}
        effective_text_model = text_model
        if char_urls and text_model not in VISION_MODELS:
            logger.warning(f"[STORYBOARD_PRO] Model '{text_model}' does not support vision; auto-upgrading to 'gpt-4o-mini' for Step 1")
            effective_text_model = "gpt-4o-mini"

        # Step 1/6: LLM analyzes images + story → MASTER PROMPT
        logger.info("[STORYBOARD_PRO] STEP 1/6: Analyzing characters and story...")
        step1_content: str | list[dict]
        if char_urls:
            parts: list[dict] = [{"type": "text", "text": f"{cls.META_INSTRUCTION_A}\n\nStory Description:\n{story_description}"}]
            for url in char_urls:
                parts.append({"type": "image_url", "image_url": {"url": url}})
            step1_content = parts
        else:
            step1_content = f"{cls.META_INSTRUCTION_A}\n\nStory Description:\n{story_description}"

        step1_request = TextGenerationRequest(
            model=effective_text_model,
            messages=[ChatMessage(role="user", content=step1_content)],
            temperature=0.7, max_tokens=4096,
        )
        step1_response: TextGenerationResponse = await sync_op(
            cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"),
            data=step1_request, response_model=TextGenerationResponse, api_key=key,
            wait_label="Step 1/6: Analyzing characters", estimated_duration=20)
        master_prompt = extract_text_content(step1_response.choices[0].message.content) if step1_response.choices else ""

        # Step 2/6: LLM → segment video prompts + dialogue + camera
        logger.info("[STORYBOARD_PRO] STEP 2/6: Generating video script...")
        instruction_b = cls.META_INSTRUCTION_B_CUSTOM_CAMERA if camera_style == "custom" else cls.META_INSTRUCTION_B
        step2_prompt = f"""{instruction_b}

MASTER PROMPT:
{master_prompt}

Generate exactly {storyboard_count} storyboard segments for a {duration}-second video.
Total duration of all segments must equal {duration} seconds.

Output ONLY the JSON array:"""
        step2_request = TextGenerationRequest(
            model=text_model,
            messages=[ChatMessage(role="user", content=step2_prompt)],
            temperature=0.7, max_tokens=4096,
        )
        step2_response: TextGenerationResponse = await sync_op(
            cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"),
            data=step2_request, response_model=TextGenerationResponse, api_key=key,
            wait_label="Step 2/6: Generating video script", estimated_duration=20)
        segments_text = extract_text_content(step2_response.choices[0].message.content) if step2_response.choices else ""

        segments_data = parse_json_safe(segments_text, "segments")
        segments = segments_data if isinstance(segments_data, list) else []
        if not segments:
            segments = [{"prompt": story_description, "duration": int(duration)}]

        total_seg_duration = sum(int(s.get("duration", 0)) for s in segments)
        if total_seg_duration != int(duration):
            base = int(duration) // len(segments)
            remainder = int(duration) - base * len(segments)
            for i, seg in enumerate(segments):
                seg["duration"] = base + (1 if i < remainder else 0)

        # P3: Merge negative prompts from all segments
        all_negatives = []
        seen_negatives = set()
        for seg in segments:
            neg = str(seg.get("negative", "")).strip()
            if neg and neg not in seen_negatives:
                all_negatives.append(neg)
                seen_negatives.add(neg)
        merged_negative = ", ".join(all_negatives)
        final_negative = f"{negative_prompt}, {merged_negative}".strip(", ") if merged_negative else negative_prompt

        video_prompts_json = json.dumps(segments, ensure_ascii=False, indent=2)
        multi_prompt = []
        for i, seg in enumerate(segments):
            prompt_text = str(seg.get("prompt", ""))[:512]
            if not prompt_text.strip():
                prompt_text = f"Scene {i+1}"
            multi_prompt.append(KlingMultiPromptItem(index=i+1, prompt=prompt_text, duration=str(seg.get("duration", 5))))

        # P2: Determine camera_control
        camera_control: KlingCameraControl | None = None
        if camera_style == "simple":
            cam_text = segments[0].get("camera", "") if segments else ""
            cam_config = _map_camera_text_to_preset(cam_text)
            if cam_config:
                camera_control = KlingCameraControl(type="simple", config=cam_config)
                logger.info("[STORYBOARD_PRO] Camera (simple): mapped '%s' → %s", cam_text, cam_config)
        elif camera_style == "custom":
            cam_config = _parse_camera_values_from_segment(segments[0]) if segments else None
            if cam_config:
                camera_control = KlingCameraControl(type="simple", config=cam_config)
                logger.info("[STORYBOARD_PRO] Camera (custom): %s", cam_config)

        # Step 3/6: Generate storyboard image (P1: use SETTING from master_prompt)
        storyboard_image_url = ""
        logger.info("[STORYBOARD_PRO] STEP 3/6: Generating storyboard image...")
        first_prompt = multi_prompt[0].prompt if multi_prompt else story_description
        setting_prompt = _extract_setting_from_master(master_prompt)
        ref_prompt = setting_prompt or first_prompt
        if setting_prompt:
            logger.info("[STORYBOARD_PRO] Using SETTING-based prompt for reference image")
        try:
            ref_url = char_urls[0] if char_urls else ""
            if image_model.startswith("kling"):
                kling_model = image_model
                img_request = KlingImageGenRequest(
                    model_name=kling_model, prompt=ref_prompt, aspect_ratio=aspect_ratio, n=1,
                    image=ref_url if ref_url else None,
                    image_reference=image_reference if ref_url else None,
                    image_fidelity=image_fidelity if ref_url else None,
                    human_fidelity=human_fidelity if ref_url else None,
                )
                img_submit: KlingSubmitResponse = await sync_op(
                    cls, endpoint=ApiEndpoint(path=KLING_IMAGE_GEN, method="POST"),
                    data=img_request, response_model=KlingSubmitResponse, api_key=key,
                    wait_label="Step 3/6: Submitting storyboard image", estimated_duration=5)
                img_task_id = img_submit.data.task_id if img_submit.data else ""
                if img_task_id:
                    img_poll: KlingPollResponse = await poll_op(
                        cls, poll_endpoint=ApiEndpoint(path=KLING_IMAGE_GEN_POLL.format(img_task_id), method="GET"),
                        response_model=KlingPollResponse, status_extractor=kling_status_extractor,
                        api_key=key, completed_statuses=["succeed"], failed_statuses=["failed"],
                        queued_statuses=["submitted", "processing"],
                        poll_interval=3.0, max_poll_attempts=200, estimated_duration=60)
                    img_data = img_poll.data
                    if img_data and img_data.task_result and img_data.task_result.images:
                        storyboard_image_url = img_data.task_result.images[0].url
            elif image_model == "gpt-image":
                from ..apis.openai import GPTImageRequest, GPTImageResponse
                _gpt_size_map = {"16:9": "1536x1024", "9:16": "1024x1536", "1:1": "1024x1024"}
                gpt_img_request = GPTImageRequest(
                    prompt=ref_prompt,
                    size=_gpt_size_map.get(aspect_ratio, "1024x1024"),
                    quality="high", output_format="png",
                )
                gpt_img_response: GPTImageResponse = await sync_op(
                    cls, endpoint=ApiEndpoint(path="/v1/images/generations", method="POST"),
                    data=gpt_img_request, response_model=GPTImageResponse, api_key=key,
                    wait_label="Step 3/6: Generating storyboard image (GPT)", estimated_duration=20)
                storyboard_image_url = gpt_img_response.data[0].url if gpt_img_response.data else ""
            elif image_model == "flux-pro":
                from ..apis.flux import FluxProRequest, FluxProResponse
                _flux_size_map = {"16:9": "landscape_16_9", "9:16": "portrait_9_16", "1:1": "square"}
                flux_request = FluxProRequest(prompt=ref_prompt, image_size=_flux_size_map.get(aspect_ratio, "landscape_16_9"), num_inference_steps=30, seed=0, guidance_scale=3.5, num_images=1, enable_safety_checker=True, output_format="jpeg", sync=True)
                flux_response: FluxProResponse = await sync_op(
                    cls, endpoint=ApiEndpoint(path="/fal-ai/flux-pro", method="POST"),
                    data=flux_request, response_model=FluxProResponse, api_key=key,
                    wait_label="Step 3/6: Generating storyboard image (FLUX)", estimated_duration=15)
                storyboard_image_url = flux_response.images[0].url if flux_response.images else ""
            else:
                logger.warning(f"[STORYBOARD_PRO] Unknown image_model '{image_model}', skipping Step 3")
        except Exception as e:
            logger.warning(f"[STORYBOARD_PRO] Step 3 failed, will use text-to-video: {e}")
            storyboard_image_url = ""

        # Step 4/6: Generate dialogue audio (P4)
        dialogue_audio_output = None
        dialogue_text_str = ""
        audio_bytes_raw = None
        if generate_dialogue == "on":
            all_dialogue = [str(s.get("dialogue", "")).strip() for s in segments if s.get("dialogue")]
            dialogue_text_str = "\n".join(all_dialogue)
            if dialogue_text_str.strip():
                try:
                    logger.info("[STORYBOARD_PRO] STEP 4/6: Generating dialogue audio...")
                    audio_bytes_raw, _audio_url = await _tts_generate_dialogue(cls, dialogue_text_str, voice, key)
                    dialogue_audio_output = audio_bytes_to_audio_input(audio_bytes_raw)
                except Exception as e:
                    logger.warning(f"[STORYBOARD_PRO] Step 4 TTS failed: {e}")
                    dialogue_audio_output = None
                    audio_bytes_raw = None
            else:
                logger.info("[STORYBOARD_PRO] STEP 4/6: No dialogue text extracted, skipping TTS")
        else:
            logger.info("[STORYBOARD_PRO] STEP 4/6: Dialogue generation disabled")

        # Step 5/6: Generate storyboard video
        logger.info("[STORYBOARD_PRO] STEP 5/6: Generating storyboard video...")
        combined_prompt = " ; ".join(mp.prompt for mp in multi_prompt)

        if storyboard_image_url:
            video_request = KlingImage2VideoRequest(
                model_name=video_model, prompt=combined_prompt,
                image=storyboard_image_url, duration=duration,
                aspect_ratio=aspect_ratio, cfg_scale=cfg_scale, mode=mode,
                negative_prompt=final_negative or None,
                sound=sound if sound != "off" else None,
                multi_shot=True, shot_type="customize", multi_prompt=multi_prompt,
                camera_control=camera_control,
            )
            submit_path = KLING_IMAGE2VIDEO
            poll_path = KLING_IMAGE2VIDEO_POLL
        else:
            video_request = KlingText2VideoRequest(
                model_name=video_model, prompt=combined_prompt,
                duration=duration, aspect_ratio=aspect_ratio,
                cfg_scale=cfg_scale, mode=mode,
                negative_prompt=final_negative or None,
                sound=sound if sound != "off" else None,
                multi_shot=True, shot_type="customize", multi_prompt=multi_prompt,
                camera_control=camera_control,
            )
            submit_path = KLING_TEXT2VIDEO
            poll_path = KLING_TEXT2VIDEO_POLL

        video_submit: KlingSubmitResponse = await sync_op(
            cls, endpoint=ApiEndpoint(path=submit_path, method="POST"),
            data=video_request, response_model=KlingSubmitResponse, api_key=key,
            wait_label="Step 5/6: Submitting video", estimated_duration=5)
        video_task_id = video_submit.data.task_id if video_submit.data else ""
        if not video_task_id:
            raise Exception(f"Video submit failed: {video_submit}")

        video_poll: KlingPollResponse = await poll_op(
            cls, poll_endpoint=ApiEndpoint(path=poll_path.format(video_task_id), method="GET"),
            response_model=KlingPollResponse, status_extractor=kling_status_extractor,
            api_key=key, completed_statuses=["succeed"], failed_statuses=["failed"],
            queued_statuses=["submitted", "processing"],
            poll_interval=5.0, max_poll_attempts=240, estimated_duration=180)

        video_url = ""
        if video_poll.data and video_poll.data.task_result and video_poll.data.task_result.videos:
            video_url = video_poll.data.task_result.videos[0].url
        if not video_url:
            raise Exception("Video task completed but no video URL found.")

        # Step 6/6: ffmpeg mix video + dialogue
        final_video_output = None
        if generate_dialogue == "on" and audio_bytes_raw is not None and dialogue_audio_output is not None:
            logger.info("[STORYBOARD_PRO] STEP 6/6: Mixing video and dialogue audio...")
            try:
                video_bytesio = await download_url_as_bytesio(video_url, cls=cls)
                video_bytes_raw = video_bytesio.getvalue()
                mixed_bytes = _ffmpeg_mix_video_audio(video_bytes_raw, audio_bytes_raw)
                if mixed_bytes:
                    final_video_output = InputImpl.VideoFromFile(BytesIO(mixed_bytes))
                    logger.info("[STORYBOARD_PRO] ffmpeg mix successful")
                else:
                    logger.warning("[STORYBOARD_PRO] ffmpeg mix failed, returning video without dialogue")
            except Exception as e:
                logger.warning(f"[STORYBOARD_PRO] Step 6 mix failed: {e}")

        if final_video_output is None:
            final_video_output = await download_url_to_video_output(video_url, cls=cls)

        return IO.NodeOutput(final_video_output, master_prompt, video_prompts_json,
                             storyboard_image_url, dialogue_audio_output, dialogue_text_str)


class UnlimitAIWorkflowV3Extension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        return [StoryboardComposerV3Node, StoryboardVideoV3Node, StoryboardProV3Node, NovelToDramaV3Node, SceneImageGeneratorV3Node, SceneVideoGeneratorV3Node, SceneAudioGeneratorV3Node, DramaManifestV3Node]


async def comfy_entrypoint() -> UnlimitAIWorkflowV3Extension:
    return UnlimitAIWorkflowV3Extension()
