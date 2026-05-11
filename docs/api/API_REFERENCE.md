# API 参考文档

本文档提供ComfyUI-UnlimitAI的完整API参考。

---

## 📋 目录

- [核心客户端](#核心客户端)
- [工具模块](#工具模块)
- [节点API](#节点api)
- [类型定义](#类型定义)

---

## 核心客户端

### UnlimitAIClient

主要的API客户端类，用于调用UnlimitAI的所有服务。

#### 初始化

```python
from utils.api_client import UnlimitAIClient

client = UnlimitAIClient(
    api_key: str,           # UnlimitAI API密钥
    base_url: str = None,   # API基础URL（可选）
    timeout: int = 60,      # 请求超时时间（秒）
    max_retries: int = 3    # 最大重试次数
)
```

#### 方法

##### generate_text()

生成文本内容。

```python
def generate_text(
    prompt: str,                      # 输入提示词
    model: str = "deepseek-chat",     # 模型名称
    max_tokens: int = None,           # 最大token数
    temperature: float = None,        # 温度参数
    top_p: float = None,              # Top-p采样
    **kwargs                          # 其他参数
) -> str                              # 返回生成的文本
```

**示例**:
```python
text = client.generate_text(
    prompt="写一段描写春天的文字",
    model="deepseek-chat",
    max_tokens=500
)
```

---

##### generate_image()

生成图像。

```python
def generate_image(
    prompt: str,                      # 图像描述
    model: str = "flux.1-schnell",    # 模型名称
    size: str = "1024x1024",          # 图像尺寸
    steps: int = None,                # 生成步数
    guidance: float = None,           # 引导强度
    seed: int = None,                 # 随机种子
    negative_prompt: str = None,      # 负面提示词
    **kwargs
) -> str                              # 返回图像URL
```

**示例**:
```python
image_url = client.generate_image(
    prompt="一个穿着蓝色裙子的女孩站在樱花树下",
    model="flux.1-schnell",
    size="1024x1024",
    steps=4
)
```

---

##### generate_video()

生成视频。

```python
def generate_video(
    prompt: str,                        # 视频描述
    model: str = "kling-video-v2",      # 模型名称
    duration: float = 5.0,              # 视频时长（秒）
    aspect_ratio: str = "16:9",         # 宽高比
    image_url: str = None,              # 参考图像URL（图生视频）
    seed: int = None,                   # 随机种子
    **kwargs
) -> str                                # 返回视频URL
```

**示例**:
```python
video_url = client.generate_video(
    prompt="女孩在樱花树下旋转跳舞",
    model="kling-video-v2",
    duration=5.0
)
```

---

##### generate_audio()

生成语音。

```python
def generate_audio(
    text: str,                      # 要转换的文本
    model: str = "tts-1",           # TTS模型
    voice: str = "alloy",           # 音色
    speed: float = 1.0,             # 语速
    **kwargs
) -> str                            # 返回音频URL
```

**示例**:
```python
audio_url = client.generate_audio(
    text="你好，欢迎使用ComfyUI-UnlimitAI",
    model="tts-1",
    voice="alloy"
)
```

---

##### generate_music()

生成音乐。

```python
def generate_music(
    prompt: str,                    # 音乐描述
    model: str = "musicgen",        # 模型名称
    duration: float = 30.0,         # 时长（秒）
    seed: int = None,               # 随机种子
    **kwargs
) -> str                            # 返回音乐URL
```

**示例**:
```python
music_url = client.generate_music(
    prompt="轻快的钢琴曲，适合春天",
    model="musicgen",
    duration=30.0
)
```

---

### InputValidator

输入验证器类。

#### 初始化

```python
from utils.api_client import InputValidator

validator = InputValidator(
    max_prompt_length: int = 10000,    # 最大提示词长度
    max_image_size: int = 2048,        # 最大图像尺寸
    max_video_duration: float = 60.0   # 最大视频时长
)
```

#### 方法

##### validate_prompt()

```python
def validate_prompt(prompt: str) -> str
```

验证提示词是否有效。

---

##### validate_image_size()

```python
def validate_image_size(size: str) -> str
```

验证图像尺寸格式。

---

##### validate_duration()

```python
def validate_duration(duration: float) -> float
```

验证时长是否在有效范围内。

---

## 工具模块

### Logger - 日志系统

```python
from utils.logger import get_logger

logger = get_logger(
    name: str = "UnlimitAI",          # 日志器名称
    level: str = "INFO",              # 日志级别
    log_file: str = None,             # 日志文件路径
    use_colors: bool = True           # 是否使用彩色输出
)
```

**使用方法**:
```python
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息", exc_info=True)
logger.critical("严重错误")
```

---

### Exceptions - 异常处理

#### 基础异常

```python
from utils.exceptions import UnlimitAIError

raise UnlimitAIError(
    message: str,                     # 错误消息
    code: str = "E1000",             # 错误代码
    details: dict = None,            # 详细信息
    cause: Exception = None          # 原始异常
)
```

#### 具体异常类型

- `APIError` - API错误
- `APIConnectionError` - 连接错误
- `APITimeoutError` - 超时错误
- `APIAuthError` - 认证错误
- `APIRateLimitError` - 频率限制错误
- `ValidationError` - 验证错误
- `FileError` - 文件错误
- `ConfigError` - 配置错误

---

### Config - 配置管理

```python
from utils.config import Config

config = Config.load()
```

#### 方法

```python
# 获取配置值
value = config.get("key.path", default=None)

# 设置配置值
config.set("key.path", value)

# 保存配置
config.save(path=None)

# 重新加载
config.reload()
```

---

### Delay - 智能延迟

```python
from utils.delay import SmartDelay, retry_on_failure

# 智能延迟
delay = SmartDelay(
    min_delay: float = 0.1,
    max_delay: float = 60.0,
    initial_delay: float = 1.0
)

delay.wait("operation")
delay.on_success()
delay.on_failure()

# 重试装饰器
@retry_on_failure(max_retries=3, base_delay=1.0)
def risky_function():
    pass
```

---

### Persistent Storage - 持久化存储

```python
from utils.persistent_storage import CharacterDatabase

db = CharacterDatabase(db_path: str = "data/characters.json")

# 保存角色
db.save_character(name: str, data: dict) -> bool

# 加载角色
db.load_character(name: str) -> dict

# 删除角色
db.delete_character(name: str) -> bool

# 列出所有角色
db.list_characters() -> list
```

---

## 节点API

### CharacterImageLoaderNode

加载和管理角色图像。

#### INPUT_TYPES

```python
{
    "required": {
        "character_name": ("STRING", {}),
        "image_source": (["url", "file", "generate"], {}),
    },
    "optional": {
        "image_url": ("STRING", {"default": ""}),
        "file_path": ("STRING", {"default": ""}),
        "style": (["anime", "realistic", "cartoon"], {"default": "anime"}),
    }
}
```

#### RETURN_TYPES

```python
("IMAGE", "CHARACTER", "STRING")
```

---

### TextGeneratorNode

文本生成节点。

#### INPUT_TYPES

```python
{
    "required": {
        "prompt": ("STRING", {"multiline": True}),
        "model": (["deepseek-chat", "gpt-4", "claude-3-opus"], {}),
    },
    "optional": {
        "max_tokens": ("INT", {"default": 4096}),
        "temperature": ("FLOAT", {"default": 0.7}),
    }
}
```

#### RETURN_TYPES

```python
("STRING", "INT", "INT", "FLOAT")  # text, input_tokens, output_tokens, cost
```

---

## 类型定义

### 基础类型

```python
from utils.types import (
    ImageType,           # np.ndarray - [H, W, C] RGB格式
    PathType,            # Union[str, Path]
    JSONType,            # JSON数据类型
)
```

### 数据类型

```python
from utils.types import (
    CharacterData,       # 角色数据
    SceneData,           # 场景数据
    VoiceConfig,         # 音色配置
    ProjectData,         # 项目数据
)
```

### 响应类型

```python
from utils.types import (
    TextGenerationResponse,
    ImageGenerationResponse,
    VideoGenerationResponse,
    AudioGenerationResponse,
    MusicGenerationResponse,
)
```

---

## 完整示例

### 示例1：基础使用

```python
from utils.api_client import UnlimitAIClient
from utils.logger import get_logger

# 初始化
client = UnlimitAIClient(api_key="your_key")
logger = get_logger(__name__)

try:
    # 生成文本
    text = client.generate_text(
        prompt="写一首关于春天的诗",
        model="deepseek-chat"
    )
    logger.info(f"生成文本: {text}")
    
    # 生成图像
    image_url = client.generate_image(
        prompt="春天的花园，樱花盛开",
        model="flux.1-schnell"
    )
    logger.info(f"图像URL: {image_url}")
    
except Exception as e:
    logger.error(f"生成失败: {e}", exc_info=True)
```

---

### 示例2：使用重试机制

```python
from utils.delay import retry_on_failure

@retry_on_failure(max_retries=3, base_delay=1.0)
def generate_with_retry(prompt):
    client = UnlimitAIClient(api_key="your_key")
    return client.generate_text(prompt)

result = generate_with_retry("测试提示词")
```

---

### 示例3：角色管理

```python
from nodes.character_nodes_optimized import CharacterImageLoaderNode

# 创建节点
loader = CharacterImageLoaderNode()

# 加载角色
image, character, description = loader.load_from_url(
    image_url="https://example.com/character.png",
    character_name="主角",
    style="anime"
)
```

---

## 错误处理

### 错误代码

| 代码 | 说明 |
|------|------|
| E1000-E1999 | 通用错误 |
| E2000-E2999 | API错误 |
| E3000-E3999 | 文件错误 |
| E4000-E4999 | 处理错误 |
| E5000-E5999 | 资源错误 |
| E6000-E6999 | 配置错误 |

### 错误处理示例

```python
from utils.exceptions import APIError, ValidationError

try:
    result = client.generate_text(prompt="")
except ValidationError as e:
    print(f"验证错误: {e}")
except APIError as e:
    print(f"API错误: {e}")
```

---

## 性能优化建议

1. **使用缓存**: 避免重复生成相同内容
2. **批量处理**: 使用并行处理提高效率
3. **智能延迟**: 避免触发API频率限制
4. **错误重试**: 使用指数退避重试机制

---

## 更多信息

- [开发指南](../DEVELOPMENT.md)
- [工作流指南](../docs/WORKFLOW_GUIDE.md)
- [项目结构](../docs/PROJECT_STRUCTURE.md)

---

**最后更新**: 2025-01-XX
