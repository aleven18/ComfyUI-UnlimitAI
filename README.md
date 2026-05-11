# ComfyUI-UnlimitAI

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-orange.svg)](https://github.com/comfyanonymous/ComfyUI)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-100%2B-brightgreen.svg)](tests/)

**将小说转换为动态漫剧的ComfyUI插件**

基于UnlimitAI API，实现文本、图像、视频、音频、音乐的自动化生成

[English](#english) | [中文文档](#中文文档)

</div>

---

## 中文文档

### 📖 项目简介

**ComfyUI-UnlimitAI** 是一个强大的ComfyUI插件，能够将小说内容自动转换为动态漫剧。通过集成UnlimitAI的多模态AI服务，实现从文本分析到视频生成的全流程自动化。

#### 核心亮点

- 🎯 **一键转换**: 小说 → 漫剧，全自动化流程
- 🎨 **角色一致性**: 智能维护角色外观和音色
- 💰 **成本优化**: 智能模型选择，节省30-61%成本
- ⚡ **高性能**: 并行处理，智能延迟控制
- 🔧 **易扩展**: 模块化设计，自定义工作流

---

### ✨ 功能特性

#### 1. 多模态内容生成

| 模块 | 功能 | 支持模型 |
|------|------|----------|
| 📝 **文本生成** | 小说分析、场景提取、对话生成 | DeepSeek, GPT-4, Claude |
| 🎨 **图像生成** | 角色立绘、场景插画、分镜图 | FLUX, Imagen, Ideogram |
| 🎬 **视频生成** | 场景动画、角色动作、过渡效果 | Kling, Runway Gen-3, Pika |
| 🎙️ **音频生成** | 语音合成、多角色配音 | TTS-1, Minimax TTS |
| 🎵 **音乐生成** | 背景音乐、氛围音效 | MusicGen, Stable Audio |

#### 2. 智能角色管理

- ✅ 角色外观一致性维护
- ✅ 多角色音色定义
- ✅ 角色数据持久化存储
- ✅ 跨场景角色调用

#### 3. 成本优化策略

提供4套预设工作流：

| 工作流 | 质量 | 成本 | 适用场景 |
|--------|------|------|----------|
| **budget** | 低 | 低（节省61%） | 快速预览、原型测试 |
| **balanced** | 中 | 中（节省45%） | 日常使用、平衡性价比 |
| **quality** | 高 | 高（节省30%） | 正式发布、高要求场景 |
| **max_quality** | 极高 | 极高 | 商业项目、顶级质量 |

#### 4. 核心节点（59个）

```
文本节点 (6个)
├── TextGeneratorNode - 文本生成
├── TextParserNode - 文本解析
├── NovelAnalyzerNode - 小说分析
├── SceneExtractorNode - 场景提取
├── DialogueGeneratorNode - 对话生成
└── CharacterExtractorNode - 角色提取

图像节点 (7个)
├── ImageGeneratorNode - 图像生成
├── CharacterImageNode - 角色立绘
├── SceneImageNode - 场景插画
├── StoryboardNode - 分镜生成
├── ImageEditorNode - 图像编辑
├── ImageUpscaleNode - 图像放大
└── ImageVariationNode - 图像变体

视频节点 (10个)
├── VideoGeneratorNode - 视频生成
├── SceneVideoNode - 场景视频
├── CharacterActionNode - 角色动作
├── TransitionNode - 过渡效果
├── VideoEditorNode - 视频编辑
└── ...

音频节点 (7个)
音乐节点 (6个)
工作流节点 (5个)
优化节点 (4个)
高级节点 (7个)
角色节点 (4个)
```

---

### 🚀 快速开始

#### 1. 环境要求

- Python 3.8+
- ComfyUI
- UnlimitAI API Key

#### 2. 安装

```bash
# 方法1: 克隆到ComfyUI custom_nodes目录
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/your-repo/ComfyUI-UnlimitAI.git

# 方法2: 直接下载ZIP并解压

# 安装依赖
cd ComfyUI-UnlimitAI
pip install -r requirements.txt

# 配置API Key
cp .env.example .env
# 编辑.env文件，填写你的API Key
```

#### 3. 配置

创建 `.env` 文件：

```bash
# UnlimitAI API Key（必需）
UNITED_API_KEY=your_api_key_here

# 可选配置
LOG_LEVEL=INFO
DEFAULT_TEXT_MODEL=deepseek-chat
DEFAULT_IMAGE_MODEL=flux.1-schnell
DEFAULT_VIDEO_MODEL=kling-video-v2
```

#### 4. 使用

在ComfyUI中加载工作流：

```
workflows/balanced_workflow.json  # 推荐新手使用
```

---

### 📚 使用示例

#### 示例1：简单文本生成

```python
from utils.api_client import UnlimitAIClient

client = UnlimitAIClient(api_key="your_key")

result = client.generate_text(
    prompt="写一段描写春天的文字",
    model="deepseek-chat"
)

print(result)
```

#### 示例2：图像生成

```python
image_url = client.generate_image(
    prompt="一个穿着蓝色裙子的女孩站在樱花树下",
    model="flux.1-schnell",
    size="1024x1024"
)

print(f"图像URL: {image_url}")
```

#### 示例3：视频生成

```python
video_url = client.generate_video(
    prompt="女孩在樱花树下旋转跳舞",
    model="kling-video-v2",
    duration=5.0
)

print(f"视频URL: {video_url}")
```

#### 示例4：完整工作流

```
小说输入 → 文本分析 → 角色提取 → 场景分割
    ↓
角色立绘生成 → 场景插画生成 → 分镜图生成
    ↓
语音合成 → 背景音乐生成
    ↓
场景视频生成 → 视频合成 → 最终输出
```

---

### ⚙️ 配置说明

#### 主配置文件 (config.yaml)

```yaml
# API配置
api:
  api_key: ""
  base_url: "https://api.unlimitai.com"
  timeout: 60
  max_retries: 3

# 默认模型配置
models:
  text:
    default: "deepseek-chat"
  image:
    default: "flux.1-schnell"
  video:
    default: "kling-video-v2"
  audio:
    default: "tts-1"
  music:
    default: "musicgen"

# 生成参数
generation:
  image:
    default_size: "1024x1024"
  video:
    default_duration: 5.0
```

#### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `UNITED_API_KEY` | UnlimitAI API Key | - |
| `LOG_LEVEL` | 日志级别 | INFO |
| `DEFAULT_TEXT_MODEL` | 默认文本模型 | deepseek-chat |
| `DEFAULT_IMAGE_MODEL` | 默认图像模型 | flux.1-schnell |
| `DEFAULT_VIDEO_MODEL` | 默认视频模型 | kling-video-v2 |
| `API_TIMEOUT` | API超时时间(秒) | 60 |
| `MAX_RETRIES` | 最大重试次数 | 3 |

---

### 📖 API文档

详细API文档请参考：[API Reference](docs/api_reference.md)

#### 核心类

##### UnlimitAIClient

```python
from utils.api_client import UnlimitAIClient

# 初始化
client = UnlimitAIClient(
    api_key="your_key",
    base_url="https://api.unlimitai.com",
    timeout=60,
    max_retries=3
)

# 文本生成
text = client.generate_text(prompt="...", model="deepseek-chat")

# 图像生成
image_url = client.generate_image(prompt="...", size="1024x1024")

# 视频生成
video_url = client.generate_video(prompt="...", duration=5.0)

# 音频生成
audio_url = client.generate_audio(text="...", voice="alloy")

# 音乐生成
music_url = client.generate_music(prompt="...", duration=30.0)
```

---

### 🧪 测试

```bash
# 安装测试依赖
pip install -r requirements-dev.txt

# 运行所有测试
python run_tests.py

# 或使用pytest
pytest tests/ -v

# 运行带覆盖率的测试
pytest tests/ --cov=. --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

---

### 🐛 常见问题

#### Q1: 如何获取UnlimitAI API Key？

1. 访问 [UnlimitAI官网](https://unlimitai.com)
2. 注册账号
3. 在控制台获取API Key

#### Q2: 支持哪些模型？

**文本模型**:
- DeepSeek Chat (推荐，性价比高)
- GPT-4, GPT-4 Turbo
- Claude 3 Opus, Claude 3 Sonnet

**图像模型**:
- FLUX.1 Schnell (快速)
- FLUX.1 Dev (高质量)
- Imagen 3.0
- Ideogram V2

**视频模型**:
- Kling Video V2 (推荐)
- Runway Gen-3 Turbo
- Pika 2.0

**音频模型**:
- TTS-1, TTS-1 HD
- Minimax TTS

**音乐模型**:
- MusicGen
- Stable Audio 2.0

#### Q3: 如何选择合适的工作流？

- **快速测试**: `budget_workflow.json`
- **日常使用**: `balanced_workflow.json` (推荐)
- **高质量输出**: `quality_workflow.json`
- **商业项目**: `max_quality_workflow.json`

#### Q4: 如何降低成本？

1. 使用DeepSeek代替GPT-4（文本成本降低99%）
2. 使用FLUX Schnell代替FLUX Dev（图像成本降低70%）
3. 使用budget工作流（总成本降低61%）
4. 启用缓存功能

#### Q5: 角色一致性如何保证？

1. 使用CharacterImageLoader节点加载参考图
2. 使用VoiceDefinition节点定义音色
3. 使用CharacterManager节点统一管理
4. 数据自动持久化到本地

---

### 🤝 贡献指南

我们欢迎所有形式的贡献！

#### 如何贡献

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

#### 开发指南

详细开发指南请参考：[DEVELOPMENT.md](DEVELOPMENT.md)

#### 代码规范

- 使用Black格式化代码
- 使用isort排序导入
- 使用mypy进行类型检查
- 编写单元测试

---

### 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

### 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/your-repo/ComfyUI-UnlimitAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/ComfyUI-UnlimitAI/discussions)
- **Email**: your.email@example.com

---

### 🙏 致谢

感谢以下项目和服务：

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - 强大的Stable Diffusion UI
- [UnlimitAI](https://unlimitai.com) - 提供优秀的AI API服务
- 所有贡献者和用户

---

## English

### 📖 Introduction

**ComfyUI-UnlimitAI** is a powerful ComfyUI plugin that automatically converts novels into dynamic comic dramas. By integrating UnlimitAI's multimodal AI services, it achieves full automation from text analysis to video generation.

### ✨ Features

- 🎯 **One-Click Conversion**: Novel → Comic Drama, fully automated
- 🎨 **Character Consistency**: Intelligent maintenance of character appearance and voice
- 💰 **Cost Optimization**: Smart model selection, save 30-61% cost
- ⚡ **High Performance**: Parallel processing, intelligent delay control
- 🔧 **Easy Extension**: Modular design, custom workflows

### 🚀 Quick Start

```bash
# Clone to ComfyUI custom_nodes
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/your-repo/ComfyUI-UnlimitAI.git

# Install dependencies
pip install -r requirements.txt

# Configure API Key
cp .env.example .env
# Edit .env file with your API key
```

### 📚 Documentation

For detailed documentation, please see:
- [Development Guide](DEVELOPMENT.md)
- [API Reference](docs/api_reference.md)

### 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star！**

Made with ❤️ by the ComfyUI-UnlimitAI Team

</div>
