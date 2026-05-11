# ComfyUI-UnlimitAI - 项目概览

## 项目统计

- **总代码行数**: 3,685 行 Python 代码
- **节点总数**: 40 个自定义节点
- **API 覆盖**: 238+ UnlimitAI API 端点
- **文档**: 中英文双语

## 文件结构

```
ComfyUI-UnlimitAI/
├── __init__.py                    # 主入口文件
├── README.md                      # 中英文文档
├── requirements.txt               # Python 依赖
├── utils/
│   └── helpers.py                 # 工具函数 (311 行)
├── nodes/
│   ├── text_nodes.py              # 文本节点 (316 行)
│   ├── image_nodes.py             # 图像节点 (612 行)
│   ├── video_nodes.py             # 视频节点 (587 行)
│   ├── audio_nodes.py             # 音频节点 (507 行)
│   ├── music_nodes.py             # 音乐节点 (391 行)
│   └── workflow_nodes.py          # 工作流节点 (961 行)
└── workflows/
    └── novel_to_drama_workflow.json  # 示例工作流
```

## 节点清单

### 文本节点 (6 个)
1. **UnlimitAITextNode** - OpenAI/Claude/DeepSeek 通用文本生成
2. **GPT5ReasoningNode** - GPT-5 推理节点
3. **DeepSeekThinkingNode** - DeepSeek 思考节点
4. **StructuredOutputNode** - 结构化输出 (JSON Schema)
5. **NovelAnalyzerNode** - 小说场景提取
6. **SceneTranslatorNode** - 场景翻译 (中→英)

### 图像节点 (7 个)
1. **FluxProNode** - FLUX Pro 文生图
2. **FluxProKontextNode** - FLUX Pro Kontext 图像编辑
3. **IdeogramV3Node** - Ideogram V3 文字渲染
4. **KlingImageGenNode** - Kling 图像生成
5. **GPTImageNode** - DALL-E 3 图像生成
6. **Imagen4Node** - Google Imagen 4
7. **RecraftV3Node** - Recraft V3 矢量/位图

### 视频节点 (10 个)
1. **VEONode** - VEO 3.1 文生视频
2. **VEONodeFalAI** - VEO 3 Fal-ai 格式
3. **KlingVideoGenNode** - Kling 文生视频
4. **KlingImageToVideoNode** - Kling 图生视频
5. **KlingDigitalHumanNode** - Kling 数字人
6. **MinimaxHailuoNode** - Minimax 海螺视频
7. **VIDUVideoGenNode** - VIDU 文生视频
8. **VIDUImageToVideoNode** - VIDU 图生视频
9. **LumaVideoGenNode** - Luma 视频生成
10. **RunwayGen4Node** - Runway Gen-4 Turbo

### 音频节点 (7 个)
1. **MinimaxTTSNode** - Minimax TTS (中文最佳)
2. **MinimaxTTSAsyncNode** - Minimax TTS 异步
3. **MinimaxVoiceCloneNode** - Minimax 语音克隆
4. **OpenAITTSNode** - OpenAI TTS (英文最佳)
5. **OpenAIWhisperNode** - OpenAI Whisper 语音识别
6. **KlingAudioGenNode** - Kling 音效生成
7. **DialogueGeneratorNode** - 漫剧对话生成

### 音乐节点 (6 个)
1. **SunoInspirationModeNode** - Suno 灵感模式
2. **SunoCustomModeNode** - Suno 自定义模式
3. **SunoLyricsGeneratorNode** - Suno 歌词生成
4. **SunoExtendNode** - Suno 歌曲续写
5. **BackgroundMusicGeneratorNode** - 漫剧背景音乐
6. **SoundtrackComposerNode** - 多场景配乐

### 工作流节点 (5 个)
1. **NovelToDramaWorkflowNode** - 小说转漫剧完整流程
2. **SceneImageGeneratorNode** - 批量场景图像生成
3. **SceneVideoGeneratorNode** - 批量场景视频生成
4. **SceneAudioGeneratorNode** - 批量场景音频生成
5. **DramaManifestNode** - 漫剧资源清单生成

## 核心功能

### 1. 小说转漫剧完整工作流

**输入**: 中文小说文本 (任意长度)

**处理流程**:
1. 小说分析 → 提取场景、对话、视觉提示词
2. 场景翻译 → 中文翻译为英文
3. 图像生成 → 为每个场景生成高质量图像
4. 视频生成 → 将图像动画化为视频
5. 音频生成 → 生成对话配音和背景音乐
6. 资源整合 → 生成完整的资源清单

**输出**: 
- scenes.json - 场景数据
- images.json - 图像资源
- videos.json - 视频资源
- audio.json - 音频资源
- manifest.json - 完整清单

### 2. 支持的 API 平台

**文本 AI**:
- OpenAI (GPT-4, GPT-4o, GPT-5)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
- DeepSeek (Chat, Reasoner)

**图像 AI**:
- Black Forest Labs (FLUX Pro, FLUX Pro Kontext)
- Ideogram (V3, V2)
- 字节跳动 (Kling)
- OpenAI (DALL-E 3)
- Google (Imagen 4)
- Recraft (V3)

**视频 AI**:
- Google (VEO 3.1, VEO 3)
- 字节跳动 (Kling v2)
- Minimax (海螺 Hailuo-2.3)
- VIDU (v1.5, v2)
- Luma
- Runway (Gen-4 Turbo)

**音频 AI**:
- Minimax (TTS, Voice Clone)
- OpenAI (TTS, Whisper)
- Kling (Audio Generation)

**音乐 AI**:
- Suno (V3.5, V4.5, V5)

## 技术特点

### 1. 纯 API 调用
- 无需本地 GPU
- 无需下载模型
- 所有 AI 处理通过 UnlimitAI API 完成
- ComfyUI 仅用于工作流编排

### 2. 异步任务处理
- 自动轮询异步任务状态
- 支持回调 URL
- 智能超时处理
- 错误重试机制

### 3. 成本优化
- 默认使用经济高效的模型 (DeepSeek)
- 透明的成本估算
- 批量处理减少 API 调用

### 4. 中文优化
- Minimax TTS 中文语音最佳
- Kling 图像/视频中文场景优化
- 支持中文情感标签
- 中英文双语文档

## 使用示例

### 示例 1: 简单文本生成
```
[UnlimitAI Text Node]
├─ API Key: YOUR_API_KEY
├─ Model: gpt-4o
├─ Prompt: "写一首关于春天的诗"
└─ Output: 生成的诗歌
```

### 示例 2: 图像生成
```
[FLUX Pro Node]
├─ API Key: YOUR_API_KEY
├─ Prompt: "A serene mountain landscape at sunset"
├─ Image Size: landscape_16_9
└─ Output: 生成的图像 URL
```

### 示例 3: 视频生成
```
[Kling Video Node]
├─ API Key: YOUR_API_KEY
├─ Prompt: "A cat playing with a ball"
├─ Duration: 5 seconds
├─ Aspect Ratio: 16:9
└─ Output: 生成的视频 URL
```

### 示例 4: 语音合成
```
[Minimax TTS Node]
├─ API Key: YOUR_API_KEY
├─ Text: "你好，欢迎来到我的频道。(laughs) 今天我们来聊聊AI。"
├─ Voice: male-qn-jingying
├─ Emotion: happy
└─ Output: 生成的音频 URL
```

### 示例 5: 完整小说转漫剧
```
[Novel Text] 
    ↓
[Novel Analyzer] → 提取 10 个场景
    ↓
[Scene Image Generator] → 生成 10 张图像
    ↓
[Scene Video Generator] → 生成 10 个视频
    ↓
[Scene Audio Generator] → 生成 10 个对话 + 10 个背景音乐
    ↓
[Drama Manifest Creator] → 整合所有资源
    ↓
[Final Output: manifest.json]
```

## 成本估算

### 10 场景漫剧示例

| 任务 | 模型 | 成本 |
|------|------|------|
| 小说分析 (10K tokens) | DeepSeek Chat | $0.003 |
| 场景翻译 (5K tokens) | GPT-4o | $0.06 |
| 图像生成 (10 张) | FLUX Pro | $0.30 |
| 视频生成 (10 个) | Kling v2 | $3.00 |
| 对话合成 (10 个) | Minimax TTS | $0.01 |
| 音乐生成 (10 首) | Suno V3.5 | $1.00 |
| **总计** | | **约 $4.40** |

### 成本优化建议

1. 使用 DeepSeek 替代 GPT-4 (节省 95%)
2. 使用 FLUX Pro 同步模式 (更快，成本相同)
3. 批量处理减少 API 调用次数
4. 合理设置 max_tokens 避免浪费

## 下一步计划

### v1.1.0 (计划)
- [ ] 添加更多视频编辑节点 (剪辑、特效)
- [ ] 支持批量并行处理
- [ ] 添加进度显示
- [ ] 支持自定义 API 端点

### v1.2.0 (计划)
- [ ] Web UI 界面
- [ ] 实时预览
- [ ] 资源管理器
- [ ] 成本计算器

### v2.0.0 (计划)
- [ ] 支持本地模型
- [ ] 混合推理 (本地 + API)
- [ ] 分布式处理
- [ ] 高级工作流模板

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件

## 联系方式

- GitHub Issues: https://github.com/your-repo/ComfyUI-UnlimitAI/issues
- UnlimitAI API 文档: https://unlimitai.apifox.cn
- ComfyUI 文档: https://github.com/comfyanonymous/ComfyUI

---

**最后更新**: 2026-05-02
**版本**: 1.0.0
**维护者**: AI Assistant
