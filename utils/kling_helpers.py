import json

from comfy_api.latest import IO

from ..apis.kling import (
    KlingCameraConfig,
    KlingCameraControl,
    KlingMultiPromptItem,
    KlingPollResponse,
    KlingSubmitResponse,
    kling_status_extractor,
)
from ..unlimitai_util import (
    ApiEndpoint,
    download_url_to_video_output,
    poll_op,
    sync_op,
    validate_string,
)


def generate_storyboard_inputs(count: int) -> list:
    inputs = []
    for i in range(1, count + 1):
        inputs.extend([
            IO.String.Input(
                f"storyboard_{i}_prompt", multiline=True, default="",
                tooltip=f"Prompt for storyboard segment {i}. Max 512 characters.",
            ),
            IO.Int.Input(
                f"storyboard_{i}_duration", default=5, min=1, max=15,
                tooltip=f"Duration for storyboard segment {i} in seconds.",
            ),
        ])
    return inputs


def parse_storyboard(storyboards: dict | None, duration: str, model_name: str) -> tuple:
    multi_shot = None
    multi_prompt = None
    shot_type = None
    if storyboards is None or storyboards.get("storyboards") == "disabled":
        return multi_shot, multi_prompt, shot_type
    if model_name == "kling-video-o1":
        raise Exception("kling-video-o1 does not support storyboards.")
    label = storyboards.get("storyboards", "")
    parts = label.split()
    if not parts:
        return multi_shot, multi_prompt, shot_type
    count = int(parts[0])
    multi_shot = True
    shot_type = "customize"
    multi_prompt = []
    total_sb_duration = 0
    for i in range(1, count + 1):
        sb_prompt = storyboards.get(f"storyboard_{i}_prompt", "")
        sb_duration = storyboards.get(f"storyboard_{i}_duration", 5)
        if not sb_prompt.strip():
            raise Exception(f"Storyboard segment {i} prompt is empty.")
        if len(sb_prompt) > 512:
            raise Exception(f"Storyboard segment {i} prompt exceeds 512 characters.")
        multi_prompt.append(KlingMultiPromptItem(index=i, prompt=sb_prompt, duration=str(sb_duration)))
        total_sb_duration += sb_duration
    if total_sb_duration != int(duration):
        raise Exception(
            f"Total storyboard duration ({total_sb_duration}s) must equal duration ({duration}s)."
        )
    return multi_shot, multi_prompt, shot_type


def parse_camera_control(camera_control_json: str) -> KlingCameraControl | None:
    if not camera_control_json or not camera_control_json.strip():
        return None
    try:
        cc_data = json.loads(camera_control_json)
    except json.JSONDecodeError:
        raise Exception("Invalid camera_control_json: must be valid JSON.")
    config_raw = cc_data.get("config", {})
    if not isinstance(config_raw, dict):
        raise Exception("camera_control_json 'config' must be a JSON object.")
    return KlingCameraControl(
        type=cc_data.get("type", "simple"),
        config=KlingCameraConfig(**config_raw),
    )


async def kling_submit_poll_download(cls, submit_path: str, poll_path: str,
                                     request, api_key: str,
                                     wait_label: str = "Submitting",
                                     poll_interval: float = 5.0,
                                     max_poll_attempts: int = 240,
                                     estimated_duration: int = 120) -> tuple:
    submit: KlingSubmitResponse = await sync_op(
        cls, endpoint=ApiEndpoint(path=submit_path, method="POST"),
        data=request, response_model=KlingSubmitResponse, api_key=api_key,
        wait_label=wait_label, estimated_duration=5,
    )
    task_id = submit.data.task_id
    if not task_id:
        raise Exception(f"Kling submit failed: {submit}")
    poll_response: KlingPollResponse = await poll_op(
        cls, poll_endpoint=ApiEndpoint(path=poll_path.format(task_id), method="GET"),
        response_model=KlingPollResponse, status_extractor=kling_status_extractor,
        api_key=api_key, completed_statuses=["succeed"], failed_statuses=["failed"],
        queued_statuses=["submitted", "processing"], poll_interval=poll_interval,
        max_poll_attempts=max_poll_attempts, estimated_duration=estimated_duration,
    )
    video_url = ""
    if poll_response.data and poll_response.data.task_result and poll_response.data.task_result.videos:
        video_url = poll_response.data.task_result.videos[0].url
    if not video_url:
        raise Exception("Kling task completed but no video URL found.")
    return await download_url_to_video_output(video_url, cls=cls), task_id
