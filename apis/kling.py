from __future__ import annotations

from pydantic import BaseModel, Field


KLING_TEXT2VIDEO = "/kling/v1/videos/text2video"
KLING_TEXT2VIDEO_POLL = "/kling/v1/videos/text2video/{}"
KLING_IMAGE2VIDEO = "/kling/v1/videos/image2video"
KLING_IMAGE2VIDEO_POLL = "/kling/v1/videos/image2video/{}"
KLING_OMNI_VIDEO = "/kling/v1/videos/omni-video"
KLING_OMNI_VIDEO_POLL = "/kling/v1/videos/omni-video/{}"
KLING_MULTI_IMAGE2VIDEO = "/kling/v1/videos/multi-image2video"
KLING_MULTI_IMAGE2VIDEO_POLL = "/kling/v1/videos/multi-image2video/{}"
KLING_MULTI_ELEMENTS_INIT = "/kling/v1/videos/multi-elements/init-selection"
KLING_MULTI_ELEMENTS_ADD = "/kling/v1/videos/multi-elements/add-selection"
KLING_MULTI_ELEMENTS_DELETE = "/kling/v1/videos/multi-elements/delete-selection"
KLING_MULTI_ELEMENTS_PREVIEW = "/kling/v1/videos/multi-elements/preview-selection"
KLING_MULTI_ELEMENTS_GENERATE = "/kling/v1/videos/multi-elements"
KLING_MULTI_ELEMENTS_POLL = "/kling/v1/videos/multi-elements/{}"
KLING_VIDEO_EXTEND = "/kling/v1/videos/video-extend"
KLING_VIDEO_EXTEND_POLL = "/kling/v1/videos/video-extend/{}"
KLING_EFFECTS = "/kling/v1/videos/effects"
KLING_EFFECTS_POLL = "/kling/v1/videos/effects/{}"
KLING_AVATAR = "/kling/v1/videos/avatar/image2video"
KLING_AVATAR_POLL = "/kling/v1/videos/avatar/image2video/{}"
KLING_IMAGE_RECOGNIZE = "/kling/v1/videos/image-recognize"
KLING_IDENTIFY_FACE = "/kling/v1/videos/identify-face"
KLING_LIP_SYNC = "/kling/v1/videos/advanced-lip-sync"
KLING_LIP_SYNC_POLL = "/kling/v1/videos/advanced-lip-sync/{}"
KLING_MOTION_CONTROL = "/kling/v1/videos/motion-control"
KLING_MOTION_CONTROL_POLL = "/kling/v1/videos/motion-control/{}"
KLING_IMAGE_GEN = "/kling/v1/images/generations"
KLING_IMAGE_GEN_POLL = "/kling/v1/images/generations/{}"
KLING_MULTI_IMAGE2IMAGE = "/kling/v1/images/multi-image2image"
KLING_MULTI_IMAGE2IMAGE_POLL = "/kling/v1/images/multi-image2image/{}"
KLING_OMNI_IMAGE = "/kling/v1/images/omni-image"
KLING_OMNI_IMAGE_POLL = "/kling/v1/images/omni-image/{}"
KLING_IMAGE_EXPAND = "/kling/v1/images/editing/expand"
KLING_IMAGE_EXPAND_POLL = "/kling/v1/images/editing/expand/{}"
KLING_VIRTUAL_TRY_ON = "/kling/v1/images/kolors-virtual-try-on"
KLING_VIRTUAL_TRY_ON_POLL = "/kling/v1/images/kolors-virtual-try-on/{}"
KLING_TEXT_TO_AUDIO = "/kling/v1/audio/text-to-audio"
KLING_TEXT_TO_AUDIO_POLL = "/kling/v1/audio/text-to-audio/{}"
KLING_VIDEO_TO_AUDIO = "/kling/v1/audio/video-to-audio"
KLING_VIDEO_TO_AUDIO_POLL = "/kling/v1/audio/video-to-audio/{}"
KLING_TTS = "/kling/v1/audio/tts"
KLING_CUSTOM_VOICES = "/kling/v1/general/custom-voices"
KLING_CUSTOM_VOICES_POLL = "/kling/v1/general/custom-voices/{}"
KLING_PRESETS_VOICES = "/kling/v1/general/presets-voices"
KLING_DELETE_VOICES = "/kling/v1/general/delete-voices"
KLING_CUSTOM_ELEMENTS = "/kling/v1/general/custom-elements"


class KlingCameraConfig(BaseModel):
    horizontal: float = Field(default=0.0, ge=-1.0, le=1.0)
    vertical: float = Field(default=0.0, ge=-1.0, le=1.0)
    pan: float = Field(default=0.0, ge=-1.0, le=1.0)
    tilt: float = Field(default=0.0, ge=-1.0, le=1.0)
    roll: float = Field(default=0.0, ge=-1.0, le=1.0)
    zoom: float = Field(default=0.0, ge=-10.0, le=10.0)


class KlingCameraControl(BaseModel):
    type: str = "simple"
    config: KlingCameraConfig = Field(default_factory=KlingCameraConfig)


class KlingMultiPromptItem(BaseModel):
    index: int
    prompt: str
    duration: str = "5"
    camera_control: KlingCameraControl | None = None


class KlingWatermarkInfo(BaseModel):
    enabled: bool = False


class KlingVoiceItem(BaseModel):
    voice_id: str = ""


class KlingDynamicMaskTrajectory(BaseModel):
    x: int = 0
    y: int = 0


class KlingDynamicMask(BaseModel):
    mask: str = ""
    trajectories: list[KlingDynamicMaskTrajectory] = Field(default_factory=list)


class KlingVideoItem(BaseModel):
    id: str = ""
    url: str = ""
    duration: str | None = None


class KlingImageItem(BaseModel):
    index: int = 0
    url: str = ""


class KlingTaskResult(BaseModel):
    videos: list[KlingVideoItem] = Field(default_factory=list)
    images: list[KlingImageItem] = Field(default_factory=list)
    audio: list[dict] | None = None


class KlingTaskData(BaseModel):
    task_id: str = ""
    task_status: str = ""
    task_status_msg: str | None = None
    task_info: dict | None = None
    created_at: int | None = None
    updated_at: int | None = None
    task_result: KlingTaskResult | None = None


class KlingSubmitResponse(BaseModel):
    code: int | None = None
    message: str | None = None
    request_id: str | None = None
    data: KlingTaskData = Field(default_factory=KlingTaskData)


class KlingPollResponse(BaseModel):
    code: int | None = None
    message: str | None = None
    request_id: str | None = None
    data: KlingTaskData = Field(default_factory=KlingTaskData)


class KlingText2VideoRequest(BaseModel):
    model_name: str = "kling-v2-master"
    prompt: str = ""
    multi_shot: bool = False
    shot_type: str | None = None
    multi_prompt: list[KlingMultiPromptItem] | None = None
    negative_prompt: str | None = None
    cfg_scale: float = Field(default=0.5, ge=0.0, le=1.0)
    mode: str = "std"
    sound: str | None = None
    camera_control: KlingCameraControl | None = None
    aspect_ratio: str = "16:9"
    duration: str = "5"
    watermark_info: KlingWatermarkInfo | None = None
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingImage2VideoRequest(BaseModel):
    model_name: str = "kling-v2-master"
    image: str = ""
    image_tail: str | None = None
    prompt: str = ""
    negative_prompt: str | None = None
    voice_list: list[KlingVoiceItem] | None = None
    sound: str | None = None
    cfg_scale: float = Field(default=0.5, ge=0.0, le=1.0)
    mode: str = "std"
    aspect_ratio: str = "16:9"
    static_mask: str | None = None
    multi_shot: bool = False
    shot_type: str | None = None
    multi_prompt: list[KlingMultiPromptItem] | None = None
    dynamic_masks: list[KlingDynamicMask] | None = None
    camera_control: KlingCameraControl | None = None
    duration: str = "5"
    watermark_info: KlingWatermarkInfo | None = None
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingOmniVideoImageItem(BaseModel):
    image_url: str = ""
    type: str | None = None


class KlingOmniVideoVideoItem(BaseModel):
    video_url: str = ""
    refer_type: str = "base"
    keep_original_sound: str | None = None


class KlingOmniVideoElementItem(BaseModel):
    element_id: str = ""


class KlingOmniVideoRequest(BaseModel):
    model_name: str = "kling-video-o1"
    prompt: str = ""
    multi_shot: bool = False
    shot_type: str | None = None
    multi_prompt: list[KlingMultiPromptItem] | None = None
    sound: str | None = None
    image_list: list[KlingOmniVideoImageItem] | None = None
    video_list: list[KlingOmniVideoVideoItem] | None = None
    element_list: list[KlingOmniVideoElementItem] | None = None
    mode: str = "std"
    aspect_ratio: str = "16:9"
    duration: str = "5"
    watermark_info: KlingWatermarkInfo | None = None
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingMultiImage2VideoImageItem(BaseModel):
    image: str = ""


class KlingMultiImage2VideoRequest(BaseModel):
    model_name: str = "kling-v1-6"
    image_list: list[KlingMultiImage2VideoImageItem] = Field(default_factory=list)
    prompt: str = ""
    negative_prompt: str | None = None
    mode: str = "std"
    duration: str = "5"
    aspect_ratio: str = "16:9"
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingMultiElementsInitRequest(BaseModel):
    video_id: str | None = None
    video_url: str | None = None


class KlingMultiElementsSelectionPoint(BaseModel):
    x: float = 0.5
    y: float = 0.5


class KlingMultiElementsAddSelectionRequest(BaseModel):
    session_id: str = ""
    frame_index: int = 0
    points: list[KlingMultiElementsSelectionPoint] = Field(default_factory=list)


class KlingMultiElementsDeleteSelectionRequest(BaseModel):
    session_id: str = ""
    frame_index: int = 0
    points: list[KlingMultiElementsSelectionPoint] = Field(default_factory=list)


class KlingMultiElementsPreviewRequest(BaseModel):
    session_id: str = ""


class KlingMultiElementsGenerateRequest(BaseModel):
    model_name: str = "kling-v1-6"
    session_id: str = ""
    edit_mode: str = "addition"
    image_list: list[str] | None = None
    prompt: str = ""
    negative_prompt: str | None = None
    mode: str = "std"
    duration: str = "5"
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingVideoExtendRequest(BaseModel):
    video_id: str = ""
    prompt: str = ""
    negative_prompt: str | None = None
    cfg_scale: float = Field(default=0.5, ge=0.0, le=1.0)
    callback_url: str | None = None


class KlingEffectsInput(BaseModel):
    model_name: str | None = None
    mode: str | None = None
    duration: str | None = None
    images: list[str] | None = None
    image: str | None = None


class KlingEffectsRequest(BaseModel):
    effect_scene: str = ""
    input: KlingEffectsInput | None = None
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingAvatarRequest(BaseModel):
    image: str = ""
    audio_id: str | None = None
    sound_file: str | None = None
    prompt: str = ""
    mode: str = "std"
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingIdentifyFaceRequest(BaseModel):
    video_id: str | None = None
    video_url: str | None = None


class KlingLipSyncFaceChoose(BaseModel):
    face_id: str = ""
    audio_id: str | None = None
    sound_file: str | None = None
    sound_start_time: int = 0
    sound_end_time: int = 5000
    sound_insert_time: int = 0
    sound_volume: int = 1
    original_audio_volume: int = 1


class KlingLipSyncRequest(BaseModel):
    session_id: str = ""
    face_choose: list[KlingLipSyncFaceChoose] = Field(default_factory=list)
    external_task_id: str | None = None
    callback_url: str | None = None


class KlingMotionControlRequest(BaseModel):
    prompt: str | None = None
    image_url: str = ""
    video_url: str = ""
    keep_original_sound: str | None = None
    character_orientation: str = "image"
    mode: str = "std"
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingImageGenRequest(BaseModel):
    model_name: str = "kling-v2"
    prompt: str = ""
    negative_prompt: str | None = None
    image: str | None = None
    image_reference: str | None = None
    image_fidelity: float | None = None
    human_fidelity: float | None = None
    resolution: str | None = None
    n: int = Field(default=1, ge=1, le=9)
    aspect_ratio: str = "16:9"
    callback_url: str | None = None


class KlingMultiImage2ImageSubjectItem(BaseModel):
    subject_image: str = ""


class KlingMultiImage2ImageRequest(BaseModel):
    model_name: str = "kling-v2"
    prompt: str | None = None
    subject_image_list: list[KlingMultiImage2ImageSubjectItem] = Field(default_factory=list)
    scene_image: str | None = None
    style_image: str | None = None
    n: int = Field(default=1, ge=1, le=9)
    aspect_ratio: str = "16:9"
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingOmniImageImageItem(BaseModel):
    image: str = ""


class KlingOmniImageRequest(BaseModel):
    model_name: str = "kling-image-o1"
    prompt: str = ""
    image_list: list[KlingOmniImageImageItem] | None = None
    resolution: str | None = None
    n: int = Field(default=1, ge=1, le=9)
    result_type: str | None = None
    series_amount: int | None = None
    aspect_ratio: str | None = None
    watermark_info: KlingWatermarkInfo | None = None
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingImageExpandRequest(BaseModel):
    image: str = ""
    up_expansion_ratio: float = 0.0
    down_expansion_ratio: float = 0.0
    left_expansion_ratio: float = 0.0
    right_expansion_ratio: float = 0.0
    prompt: str | None = None
    n: int = Field(default=1, ge=1, le=9)
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingVirtualTryOnRequest(BaseModel):
    model_name: str = "kolors-virtual-try-on-v1"
    human_image: str = ""
    cloth_image: str = ""
    callback_url: str | None = None


class KlingTextToAudioRequest(BaseModel):
    prompt: str = ""
    duration: str = "5"
    external_task_id: str | None = None
    callback_url: str | None = None


class KlingVideoToAudioRequest(BaseModel):
    video_id: str | None = None
    video_url: str | None = None
    sound_effect_prompt: str | None = None
    bgm_prompt: str | None = None
    asmr_mode: bool = False
    external_task_id: str | None = None
    callback_url: str | None = None


class KlingTTSRequest(BaseModel):
    text: str = ""
    voice_id: str = ""
    voice_language: str = "zh"
    voice_speed: float = 1.0


class KlingCustomVoiceRequest(BaseModel):
    voice_name: str = ""
    voice_url: str | None = None
    video_id: str | None = None
    callback_url: str | None = None
    external_task_id: str | None = None


class KlingCustomElementsReferItem(BaseModel):
    image_url: str = ""


class KlingCustomElementsRequest(BaseModel):
    element_name: str = ""
    element_description: str = ""
    element_frontal_image: str = ""
    element_refer_list: list[KlingCustomElementsReferItem] = Field(default_factory=list)


class KlingIdentifyFaceFaceItem(BaseModel):
    face_id: str = ""
    face_url: str | None = None


class KlingIdentifyFaceResult(BaseModel):
    session_id: str = ""
    faces: list[KlingIdentifyFaceFaceItem] = Field(default_factory=list)


def kling_status_extractor(response: KlingPollResponse | dict) -> str | None:
    if isinstance(response, dict):
        data = response.get("data", {})
        return data.get("task_status") if isinstance(data, dict) else None
    return response.data.task_status if response.data else None


def kling_video_url_extractor(response: dict) -> str:
    data = response.get("data", {})
    task_result = data.get("task_result", {}) if isinstance(data, dict) else {}
    videos = task_result.get("videos", []) if isinstance(task_result, dict) else []
    if videos and isinstance(videos, list):
        return videos[0].get("url", "") if isinstance(videos[0], dict) else ""
    return ""


def kling_image_url_extractor(response: dict) -> str:
    data = response.get("data", {})
    task_result = data.get("task_result", {}) if isinstance(data, dict) else {}
    images = task_result.get("images", []) if isinstance(task_result, dict) else []
    if images and isinstance(images, list):
        return images[0].get("url", "") if isinstance(images[0], dict) else ""
    return ""


def kling_audio_url_extractor(response: dict) -> str:
    data = response.get("data", {})
    task_result = data.get("task_result", {}) if isinstance(data, dict) else {}
    audios = task_result.get("audio", []) if isinstance(task_result, dict) else []
    if audios and isinstance(audios, list):
        return audios[0].get("url", "") if isinstance(audios[0], dict) else ""
    return ""
