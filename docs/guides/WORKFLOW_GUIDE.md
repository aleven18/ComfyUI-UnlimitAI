# 小说转漫剧完整工作流指南

## 📋 工作流概述

**功能**: 将中文小说自动转换为英文漫剧视频

**输入**: 中文小说文本（任意长度）

**输出**: 完整的漫剧资源清单（manifest.json）

**处理时间**: 10 场景约 15-30 分钟

**预估成本**: 10 场景约 $4.40

---

## 🎯 工作流步骤

### 步骤 1: 小说分析 (NovelAnalyzerNode)

**节点**: `NovelToDramaWorkflowNode`

**功能**:
- 智能分析小说情节
- 提取关键场景（可配置数量）
- 生成场景描述、对话、视觉提示词
- 识别出场人物
- 标记场景情绪氛围
- 建议镜头运动

**输入参数**:

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| api_key | STRING | UnlimitAI API Key | 必填 |
| novel_text | STRING | 中文小说文本 | 任意长度 |
| num_scenes | INT | 提取场景数量 | 5-20 |
| text_model | CHOICE | 文本模型 | deepseek-chat (经济) / gpt-4o (高质量) |
| target_language | CHOICE | 目标语言 | english / chinese |
| art_style | CHOICE | 艺术风格 | cinematic / anime / realistic / artistic |

**输出**:

| 输出 | 类型 | 说明 |
|------|------|------|
| scenes_json | STRING | 场景 JSON 数据 |
| summary | STRING | 剧情概要 |
| total_cost | STRING | 预估成本 |

**场景 JSON 结构**:

```json
{
  "scenes": [
    {
      "scene_number": 1,
      "title": "春日相遇",
      "description": "林晓薇在街上差点被车撞，被陆晨轩救下",
      "characters": ["林晓薇", "陆晨轩"],
      "mood": "romantic",
      "dialogue": "小心！(breath) 你没事吧？",
      "visual_prompt": "Cinematic shot of a young woman in her 20s on a spring street...",
      "camera_movement": "slow zoom in"
    }
  ],
  "summary": "一个关于爱情与命运的故事..."
}
```

---

### 步骤 2: 批量图像生成 (SceneImageGeneratorNode)

**节点**: `SceneImageGeneratorNode`

**功能**:
- 根据视觉提示词批量生成场景图像
- 支持多种图像模型
- 自动处理图像下载和转换

**输入参数**:

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| api_key | STRING | API Key | 必填 |
| scenes_json | STRING | 来自步骤 1 | 自动连接 |
| image_model | CHOICE | 图像模型 | flux-pro (推荐) / ideogram-v3 / kling-v2 |
| aspect_ratio | CHOICE | 画面比例 | 16:9 (横屏) / 9:16 (竖屏) / 1:1 |
| max_scenes | INT | 最大场景数 | 与步骤 1 相同 |

**模型选择建议**:

| 模型 | 特点 | 成本 | 推荐场景 |
|------|------|------|----------|
| flux-pro | 高质量、快速、同步 | $0.03/张 | 通用推荐 |
| ideogram-v3 | 文字渲染优秀 | $0.05/张 | 含文字场景 |
| kling-v2 | 中文场景优化 | $0.02/张 | 中国风格 |
| dall-e-3 | OpenAI 经典 | $0.08/张 | 创意场景 |

**输出**:

| 输出 | 类型 | 说明 |
|------|------|------|
| images_json | STRING | 图像 URL 列表 |
| summary | STRING | 生成统计 |

**图像 JSON 结构**:

```json
{
  "images": [
    {
      "scene_number": 1,
      "image_url": "https://fal.media/files/abc123.jpg",
      "status": "success"
    }
  ]
}
```

---

### 步骤 3: 批量视频生成 (SceneVideoGeneratorNode)

**节点**: `SceneVideoGeneratorNode`

**功能**:
- 将静态图像动画化为视频
- 支持多种视频模型
- 自动添加自然运动

**输入参数**:

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| api_key | STRING | API Key | 必填 |
| images_json | STRING | 来自步骤 2 | 自动连接 |
| video_model | CHOICE | 视频模型 | kling-v2 (推荐) / veo-3.1 / vidu2 |
| duration | CHOICE | 视频时长 | 5s / 10s |
| aspect_ratio | CHOICE | 画面比例 | 与图像相同 |

**模型选择建议**:

| 模型 | 特点 | 成本 | 时长 | 推荐场景 |
|------|------|------|------|----------|
| kling-v2 | 功能全面、质量高 | $0.30/视频 | 5-10s | 通用推荐 |
| veo-3.1 | 最高质量、带音频 | $0.50/视频 | 5-10s | 专业制作 |
| vidu2 | 快速生成 | $0.25/视频 | 4-8s | 快速预览 |
| hailuo | 创意运动 | $0.35/视频 | 5s | 特效场景 |

**输出**:

| 输出 | 类型 | 说明 |
|------|------|------|
| videos_json | STRING | 视频 URL 列表 |
| summary | STRING | 生成统计 |

**视频 JSON 结构**:

```json
{
  "videos": [
    {
      "scene_number": 1,
      "video_url": "https://example.com/video1.mp4",
      "status": "success"
    }
  ]
}
```

---

### 步骤 4: 批量音频生成 (SceneAudioGeneratorNode)

**节点**: `SceneAudioGeneratorNode`

**功能**:
- 生成对话配音（支持情感标签）
- 生成背景音乐（根据场景情绪）
- 自动匹配场景氛围

**输入参数**:

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| api_key | STRING | API Key | 必填 |
| scenes_json | STRING | 来自步骤 1 | 自动连接 |
| voice_id | STRING | 音色 ID | male-qn-jingying / female-shaonv |
| generate_music | BOOLEAN | 是否生成背景音乐 | true |
| max_scenes | INT | 最大场景数 | 与步骤 1 相同 |

**预设音色列表**:

| 音色 ID | 类型 | 特点 |
|---------|------|------|
| male-qn-qingse | 男声 | 青涩青年 |
| male-qn-jingying | 男声 | 精英青年（推荐） |
| female-shaonv | 女声 | 少女音 |
| female-yujie | 女声 | 御姐音 |
| presenter_male | 男声 | 主持人 |
| presenter_female | 女声 | 主持人 |
| audiobook_male_1 | 男声 | 有声书 |

**情感标签支持**:

对话文本中可以插入以下情感标签：
- `(laughs)` - 笑声
- `(sighs)` - 叹气
- `(breath)` - 呼吸
- `(coughs)` - 咳嗽
- `[laughter]` - 笑声（替代）

**情绪-音乐映射**:

| 场景情绪 | 背景音乐风格 |
|----------|--------------|
| emotional | 感人钢琴曲 |
| suspenseful | 悬疑紧张曲 |
| romantic | 浪漫爱情曲 |
| action | 动作激昂曲 |
| peaceful | 平静氛围曲 |
| dramatic | 戏剧交响曲 |
| melancholic | 忧郁悲伤曲 |
| upbeat | 欢快节奏曲 |
| tense | 紧张压迫曲 |

**输出**:

| 输出 | 类型 | 说明 |
|------|------|------|
| audio_json | STRING | 音频 URL 列表 |
| summary | STRING | 生成统计 |

**音频 JSON 结构**:

```json
{
  "audio": [
    {
      "scene_number": 1,
      "dialogue_url": "https://example.com/dialogue1.mp3",
      "music_url": "https://suno.com/music1.mp3",
      "status": "success"
    }
  ]
}
```

---

### 步骤 5: 整合资源清单 (DramaManifestNode)

**节点**: `DramaManifestNode`

**功能**:
- 整合所有场景数据
- 合并图像、视频、音频资源
- 生成完整的 manifest.json
- 提供最终输出

**输入参数**:

| 参数 | 类型 | 说明 | 来源 |
|------|------|------|------|
| scenes_json | STRING | 场景数据 | 步骤 1 |
| images_json | STRING | 图像数据 | 步骤 2 |
| videos_json | STRING | 视频数据 | 步骤 3 |
| audio_json | STRING | 音频数据 | 步骤 4 |
| title | STRING | 作品标题 | 自定义 |

**输出**:

| 输出 | 类型 | 说明 |
|------|------|------|
| manifest_json | STRING | 完整资源清单 |
| summary | STRING | 工作流总结 |

**Manifest JSON 结构**:

```json
{
  "title": "我的漫剧作品",
  "created_at": "2026-05-02 14:30:00",
  "total_scenes": 10,
  "scenes": [
    {
      "scene_number": 1,
      "title": "春日相遇",
      "description": "林晓薇在街上差点被车撞，被陆晨轩救下",
      "characters": ["林晓薇", "陆晨轩"],
      "mood": "romantic",
      "dialogue": "小心！(breath) 你没事吧？",
      "visual_prompt": "Cinematic shot of a young woman...",
      "camera_movement": "slow zoom in",
      "image_url": "https://fal.media/files/image1.jpg",
      "video_url": "https://example.com/video1.mp4",
      "dialogue_url": "https://example.com/dialogue1.mp3",
      "music_url": "https://suno.com/music1.mp3"
    }
  ]
}
```

---

## 🎨 工作流配置方案

### 方案 1: 经济配置（推荐入门）

**目标**: 最低成本快速生成

**配置**:
- 文本模型: `deepseek-chat` ($0.003)
- 图像模型: `flux-pro` ($0.30)
- 视频模型: `vidu2` ($2.50)
- 音频模型: `minimax-tts` ($0.01)
- 音乐生成: 开启 ($1.00)

**总成本**: 约 **$3.80** / 10 场景

**优点**: 成本低、速度快

**缺点**: 视频质量一般

---

### 方案 2: 标准配置（推荐使用）

**目标**: 平衡质量与成本

**配置**:
- 文本模型: `deepseek-chat` ($0.003)
- 图像模型: `flux-pro` ($0.30)
- 视频模型: `kling-v2` ($3.00)
- 音频模型: `minimax-tts` ($0.01)
- 音乐生成: 开启 ($1.00)

**总成本**: 约 **$4.40** / 10 场景

**优点**: 质量好、功能全

**缺点**: 成本中等

---

### 方案 3: 高质量配置

**目标**: 最高质量输出

**配置**:
- 文本模型: `gpt-4o` ($0.06)
- 图像模型: `ideogram-v3` ($0.50)
- 视频模型: `veo-3.1` ($5.00)
- 音频模型: `minimax-tts` ($0.01)
- 音乐生成: 开启 ($1.00)

**总成本**: 约 **$6.60** / 10 场景

**优点**: 最高质量、带音频

**缺点**: 成本较高

---

### 方案 4: 动漫风格

**目标**: 日系动漫风格

**配置**:
- 文本模型: `gpt-4o` ($0.06)
- 图像模型: `flux-pro` (anime style) ($0.30)
- 视频模型: `kling-v2` ($3.00)
- 音频模型: `minimax-tts` ($0.01)
- 音乐生成: 开启 (anime style) ($1.00)

**总成本**: 约 **$4.40** / 10 场景

**优点**: 动漫风格统一

---

## 📊 成本详细计算

### 10 场景漫剧成本分解

| 任务 | 模型 | 数量 | 单价 | 小计 |
|------|------|------|------|------|
| 小说分析 | DeepSeek Chat | 10K tokens | $0.00014/1K | $0.0014 |
| 场景翻译 | GPT-4o | 5K tokens | $0.0025/1K | $0.0125 |
| 图像生成 | FLUX Pro | 10 张 | $0.03/张 | $0.30 |
| 视频生成 | Kling v2 | 10 个 | $0.30/个 | $3.00 |
| 对话合成 | Minimax TTS | 10 个 | $0.001/个 | $0.01 |
| 音乐生成 | Suno V3.5 | 10 首 | $0.10/首 | $1.00 |
| **总计** | | | | **$4.32** |

### 20 场景漫剧成本

- 使用批量处理可节省约 20%
- 预估成本: **$7.70**

### 50 场景漫剧成本

- 使用批量处理可节省约 30%
- 预估成本: **$17.00**

---

## 🚀 使用步骤

### 1. 准备工作

```bash
# 1. 安装 ComfyUI-UnlimitAI
cp -r ComfyUI-UnlimitAI /path/to/ComfyUI/custom_nodes/

# 2. 重启 ComfyUI

# 3. 获取 UnlimitAI API Key
# 访问 https://unlimitai.org 注册并获取 API Key
```

### 2. 加载工作流

1. 打开 ComfyUI
2. 点击 Load 按钮
3. 选择 `workflows/novel_to_drama_complete_workflow.json`
4. 工作流加载成功

### 3. 配置参数

#### 3.1 填写 API Key

在以下节点中填写相同的 API Key：
- 1. 小说分析
- 2. 批量生成图像
- 3. 批量生成视频
- 4. 批量生成音频

```
api_key: "sk-xxxxxxxxxxxxxxxx"
```

#### 3.2 输入小说文本

在 "1. 小说分析" 节点：
```
novel_text: "粘贴您的中文小说文本..."
```

#### 3.3 调整参数

根据需求调整：
- `num_scenes`: 场景数量（建议 5-20）
- `text_model`: 文本模型
- `image_model`: 图像模型
- `video_model`: 视频模型
- `voice_id`: 音色 ID

### 4. 运行工作流

1. 点击 "Queue Prompt" 按钮
2. 等待处理完成（10 场景约 15-30 分钟）
3. 观察每个节点的输出

### 5. 获取结果

在 "5. 整合资源清单" 节点：
- 右键点击节点
- 选择 "Show Data"
- 查看 manifest.json

---

## 📝 示例：完整演示

### 输入小说

```
第一章 相遇

春日的阳光透过梧桐树叶洒落在街道上，林晓薇匆匆走在去公司的路上。
她没注意到，一辆黑色轿车正缓缓驶来...

"小心！"

一个低沉的男声响起，林晓薇被拉入一个温暖的怀抱。她抬头，看到
一双深邃的眼眸。

"你没事吧？"男人关切地问道，声音中带着一丝紧张。

林晓薇愣住了，这个男人有着俊朗的面容，眉宇间透着一股英气。
她似乎在哪里见过他...

"我...我没事。"她有些慌乱地站直身子，"谢谢你。"

男人微微一笑："我叫陆晨轩。很高兴认识你，虽然是在这种情况下。"

林晓薇感觉心跳加速了一拍："我叫林晓薇。"

这一刻，命运的齿轮开始转动...
```

### 配置参数

```python
# 1. 小说分析
num_scenes = 10
text_model = "deepseek-chat"
target_language = "english"
art_style = "cinematic"

# 2. 图像生成
image_model = "flux-pro"
aspect_ratio = "16:9"

# 3. 视频生成
video_model = "kling-v2"
duration = "5s"

# 4. 音频生成
voice_id = "male-qn-jingying"
generate_music = true
```

### 输出结果

#### 场景 1: 春日相遇

**描述**: 林晓薇在街上差点被车撞，被陆晨轩救下

**对话**: 
```
小心！(breath) 你没事吧？
```

**视觉提示词**:
```
Cinematic shot of a young woman in her 20s on a spring street, 
sunlight filtering through plane trees, a black sedan approaching, 
worried expression, soft natural lighting, romantic atmosphere, 
16:9 aspect ratio
```

**情绪**: romantic

**资源**:
- 图像: https://fal.media/files/scene1.jpg
- 视频: https://example.com/video1.mp4
- 配音: https://example.com/dialogue1.mp3
- 音乐: https://suno.com/music1.mp3

---

## ⚠️ 注意事项

### 1. API Key 安全

- ✅ 不要在代码中硬编码 API Key
- ✅ 不要分享 API Key 给他人
- ✅ 定期轮换 API Key
- ✅ 监控 API Key 使用情况

### 2. 资源 URL 有效期

- ⚠️ 图像/视频/音频 URL 通常在 1 小时后过期
- ✅ 及时下载或保存资源
- ✅ 不要依赖 URL 永久有效

### 3. 异步任务处理

- ⚠️ 视频生成通常需要 1-5 分钟/个
- ⚠️ 音乐生成通常需要 30-60 秒/个
- ✅ 节点会自动轮询状态
- ✅ 可调整轮询间隔和超时时间

### 4. 成本控制

- ⚠️ 大量场景会产生较高成本
- ✅ 先用少量场景测试
- ✅ 选择经济配置降低成本
- ✅ 监控 API 使用量

### 5. 质量优化

- ✅ 小说文本越详细，生成效果越好
- ✅ 场景数量适中（5-20 个）
- ✅ 选择合适的艺术风格
- ✅ 根据需求选择模型

---

## 🔧 故障排除

### 问题 1: API Key 无效

**症状**: "Invalid API key" 错误

**解决方案**:
1. 检查 API Key 是否正确
2. 确认 API Key 以 `sk-` 开头
3. 检查账户余额是否充足

### 问题 2: 节点执行超时

**症状**: "Task timeout" 错误

**解决方案**:
1. 检查网络连接
2. 增加轮询超时时间
3. 减少批量处理数量

### 问题 3: 图像/视频质量不满意

**症状**: 生成效果不理想

**解决方案**:
1. 优化小说文本描述
2. 尝试不同的图像模型
3. 调整艺术风格参数
4. 增加场景数量细化内容

### 问题 4: 成本超出预期

**症状**: API 费用过高的

**解决方案**:
1. 使用经济配置
2. 减少场景数量
3. 关闭音乐生成
4. 使用 DeepSeek 替代 GPT-4

---

## 📚 进阶技巧

### 技巧 1: 分段处理长篇小说

对于超长小说（>50 章节）：

1. 将小说分段处理
2. 每段提取 10-20 个场景
3. 合并多个 manifest.json
4. 保持人物描述一致

### 技巧 2: 自定义视觉提示词

在小说文本中插入视觉提示：

```
【场景：春日街道，阳光透过梧桐树叶】
林晓薇匆匆走在去公司的路上...

【镜头：特写，林晓薇惊讶的表情】
"小心！"
```

### 技巧 3: 多音色对话

为不同角色使用不同音色：

1. 手动编辑 scenes_json
2. 为每个场景指定音色
3. 使用自定义音色 ID

### 技巧 4: 批量并行处理

使用多个工作流并行处理：

1. 复制工作流
2. 分配不同场景范围
3. 并行运行
4. 合并结果

---

## 📖 完整工作流 JSON

工作流文件位置：
```
ComfyUI-UnlimitAI/workflows/novel_to_drama_complete_workflow.json
```

加载方式：
1. ComfyUI → Load → 选择文件
2. 配置 API Key 和参数
3. 运行工作流

---

## 🎯 总结

### 优点

✅ 全自动化处理，无需人工干预

✅ 支持多种 AI 模型，灵活配置

✅ 批量处理，高效快速

✅ 成本可控，透明清晰

✅ 输出完整，资源齐全

### 适用场景

✅ 小说转漫剧视频制作

✅ 小说可视化预览

✅ 小说改编策划

✅ 有声读物制作

✅ 小说宣传素材生成

### 未来改进

🔮 支持本地模型混合推理

🔮 实时预览和编辑

🔍 更精细的场景控制

🎥 视频剪辑和特效

👥 多角色对话优化

---

**工作流版本**: 1.0.0

**最后更新**: 2026-05-02

**维护者**: AI Assistant

**支持**: https://github.com/your-repo/ComfyUI-UnlimitAI/issues
