"""
类型定义

定义项目中使用的所有类型别名和类型提示

使用方法:
    from utils.types import (
        ImageType,
        VideoType,
        AudioType,
        CharacterData,
        SceneData
    )
"""

from typing import (
    TypedDict,
    List,
    Dict,
    Optional,
    Union,
    Any,
    Tuple,
    Callable,
    Literal
)
from pathlib import Path
import numpy as np
from PIL import Image


# =============================================================================
# 基础类型
# =============================================================================

# 图像类型（ComfyUI格式）
ImageType = np.ndarray  # [H, W, C] RGB格式

# 文件路径类型
PathType = Union[str, Path]

# JSON数据类型
JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


# =============================================================================
# API响应类型
# =============================================================================

class APIResponse(TypedDict, total=False):
    """API响应"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str]
    message: Optional[str]


class TextGenerationResponse(TypedDict, total=False):
    """文本生成响应"""
    text: str
    model: str
    usage: Dict[str, int]
    timing: Dict[str, float]


class ImageGenerationResponse(TypedDict, total=False):
    """图像生成响应"""
    images: List[Dict[str, Any]]
    model: str
    timing: Dict[str, float]


class VideoGenerationResponse(TypedDict, total=False):
    """视频生成响应"""
    videos: List[Dict[str, Any]]
    model: str
    timing: Dict[str, float]


class AudioGenerationResponse(TypedDict, total=False):
    """音频生成响应"""
    audio_url: str
    model: str
    timing: Dict[str, float]


class MusicGenerationResponse(TypedDict, total=False):
    """音乐生成响应"""
    music_url: str
    model: str
    duration: float
    timing: Dict[str, float]


# =============================================================================
# 角色数据类型
# =============================================================================

class CharacterData(TypedDict, total=False):
    """角色数据"""
    name: str
    age: int
    gender: str
    appearance: str
    personality: str
    description: str
    image_url: Optional[str]
    voice_id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class VoiceConfig(TypedDict, total=False):
    """音色配置"""
    character_name: str
    gender: str
    age: str
    tone: str
    speed: str
    engine: str
    voice_id: Optional[str]


class CharacterImage(TypedDict, total=False):
    """角色图像"""
    character_name: str
    image_url: str
    image_data: Optional[ImageType]
    prompt: Optional[str]
    seed: Optional[int]


# =============================================================================
# 场景数据类型
# =============================================================================

class DialogueLine(TypedDict):
    """对话行"""
    speaker: str
    text: str
    emotion: Optional[str]


class SceneData(TypedDict, total=False):
    """场景数据"""
    scene_id: str
    location: str
    time: str
    weather: Optional[str]
    characters: List[str]
    action: str
    dialogue: List[DialogueLine]
    image_url: Optional[str]
    video_url: Optional[str]
    audio_url: Optional[str]


class StoryboardFrame(TypedDict, total=False):
    """分镜帧"""
    frame_id: str
    scene_id: str
    description: str
    characters: List[str]
    camera_angle: Optional[str]
    camera_movement: Optional[str]
    duration: Optional[float]
    image_url: Optional[str]
    video_url: Optional[str]


# =============================================================================
# 项目数据类型
# =============================================================================

class ProjectData(TypedDict, total=False):
    """项目数据"""
    project_id: str
    name: str
    description: str
    novel_content: str
    characters: List[CharacterData]
    scenes: List[SceneData]
    storyboard: List[StoryboardFrame]
    created_at: Optional[str]
    updated_at: Optional[str]


# =============================================================================
# 工作流类型
# =============================================================================

class WorkflowConfig(TypedDict, total=False):
    """工作流配置"""
    name: str
    description: str
    quality: Literal["low", "medium", "high", "very_high"]
    cost: Literal["low", "medium", "high", "very_high"]
    models: Dict[str, str]


class NodeInput(TypedDict, total=False):
    """节点输入"""
    name: str
    type: str
    required: bool
    default: Optional[Any]
    description: Optional[str]


class NodeOutput(TypedDict, total=False):
    """节点输出"""
    name: str
    type: str
    description: Optional[str]


class NodeConfig(TypedDict, total=False):
    """节点配置"""
    name: str
    display_name: str
    description: str
    category: str
    inputs: List[NodeInput]
    outputs: List[NodeOutput]


# =============================================================================
# 生成参数类型
# =============================================================================

class TextGenerationParams(TypedDict, total=False):
    """文本生成参数"""
    prompt: str
    model: str
    max_tokens: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]
    stream: Optional[bool]


class ImageGenerationParams(TypedDict, total=False):
    """图像生成参数"""
    prompt: str
    model: str
    size: str
    steps: Optional[int]
    guidance: Optional[float]
    seed: Optional[int]
    negative_prompt: Optional[str]


class VideoGenerationParams(TypedDict, total=False):
    """视频生成参数"""
    prompt: str
    model: str
    duration: float
    aspect_ratio: Optional[str]
    image_url: Optional[str]
    seed: Optional[int]


class AudioGenerationParams(TypedDict, total=False):
    """音频生成参数"""
    text: str
    model: str
    voice: str
    speed: Optional[float]
    sample_rate: Optional[int]


class MusicGenerationParams(TypedDict, total=False):
    """音乐生成参数"""
    prompt: str
    model: str
    duration: float
    seed: Optional[int]


# =============================================================================
# 成本和统计类型
# =============================================================================

class CostInfo(TypedDict, total=False):
    """成本信息"""
    total_cost: float
    text_cost: float
    image_cost: float
    video_cost: float
    audio_cost: float
    music_cost: float


class UsageStats(TypedDict, total=False):
    """使用统计"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens: int
    total_cost: float
    average_response_time: float


# =============================================================================
# 缓存类型
# =============================================================================

class CacheEntry(TypedDict, total=False):
    """缓存条目"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    hits: int


# =============================================================================
# 回调函数类型
# =============================================================================

# 进度回调
ProgressCallback = Callable[[float, str], None]

# 完成回调
CompletionCallback = Callable[[Any], None]

# 错误回调
ErrorCallback = Callable[[Exception], None]

# 重试回调
RetryCallback = Callable[[int, Exception], None]


# =============================================================================
# 枚举类型（使用Literal）
# =============================================================================

# 模型类型
ModelType = Literal["text", "image", "video", "audio", "music"]

# 质量等级
QualityLevel = Literal["low", "medium", "high", "very_high"]

# 性别
Gender = Literal["male", "female", "other"]

# 年龄段
AgeGroup = Literal["child", "young", "middle", "old"]

# 情绪
Emotion = Literal[
    "happy", "sad", "angry", "fearful",
    "surprised", "disgusted", "neutral"
]

# 相机角度
CameraAngle = Literal[
    "close_up", "medium_shot", "full_shot",
    "wide_shot", "aerial", "low_angle", "high_angle"
]


# =============================================================================
# 辅助函数
# =============================================================================

def is_valid_image_type(obj: Any) -> bool:
    """检查是否是有效的图像类型"""
    return isinstance(obj, np.ndarray) and obj.ndim == 3


def is_valid_path_type(obj: Any) -> bool:
    """检查是否是有效的路径类型"""
    return isinstance(obj, (str, Path))


def validate_character_data(data: Dict[str, Any]) -> CharacterData:
    """验证角色数据"""
    required_fields = ["name", "gender"]
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必需字段: {field}")
    
    return data  # type: ignore


def validate_scene_data(data: Dict[str, Any]) -> SceneData:
    """验证场景数据"""
    required_fields = ["scene_id", "location"]
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必需字段: {field}")
    
    return data  # type: ignore


# =============================================================================
# 类型转换工具
# =============================================================================

def to_path_type(path: Union[str, Path]) -> Path:
    """转换为Path对象"""
    return Path(path) if isinstance(path, str) else path


def to_image_type(image: Union[Image.Image, np.ndarray]) -> ImageType:
    """转换为图像类型"""
    if isinstance(image, Image.Image):
        return np.array(image)
    elif isinstance(image, np.ndarray):
        return image
    else:
        raise TypeError(f"无法将 {type(image)} 转换为图像类型")


if __name__ == "__main__":
    # 类型检查示例
    print("类型定义模块")
    print("=" * 60)
    
    # 创建角色数据
    character: CharacterData = {
        "name": "小明",
        "age": 18,
        "gender": "male",
        "appearance": "短发，圆脸",
        "personality": "开朗"
    }
    
    print(f"角色数据: {character}")
    
    # 创建场景数据
    scene: SceneData = {
        "scene_id": "scene_001",
        "location": "学校操场",
        "time": "下午",
        "characters": ["小明"],
        "action": "打篮球"
    }
    
    print(f"场景数据: {scene}")
