# 工作流文件说明

本目录包含ComfyUI工作流JSON文件，可直接导入ComfyUI使用。

## 工作流列表

### 推荐工作流

| 文件名 | 配置 | 成本 | 质量 | 时间 | 推荐场景 |
|--------|------|------|------|------|---------|
| `balanced_workflow.json` | ⚖️ 性价比 ⭐ | $5.30/10场景 | ⭐⭐⭐⭐ | 23分钟 | 日常使用、个人项目 |
| `quality_workflow.json` | 🎯 优质 | $5.45/10场景 | ⭐⭐⭐⭐ | 25分钟 | 商业项目、客户交付 |
| `max_quality_workflow.json` | 👑 最佳质量 | $6.15/10场景 | ⭐⭐⭐⭐⭐ | 25分钟 | 顶级项目、电影级 |
| `budget_workflow.json` | 💰 最经济 | $2.03/10场景 | ⭐⭐⭐ | 12分钟 | 测试、预览 |

### 其他工作流

- `novel_to_drama_optimized.json` - 优化版工作流（通用）
- `novel_to_drama_workflow.json` - 基础工作流
- `novel_to_drama_complete.json` - 完整工作流
- `novel_to_drama_complete_workflow.json` - 完整工作流（带说明）

## 使用方法

### 1. 安装ComfyUI

```bash
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
pip install -r requirements.txt
```

### 2. 安装插件

```bash
cd ComfyUI/custom_nodes
ln -s /Users/aleven/.config/opencode/ComfyUI-UnlimitAI
```

### 3. 启动ComfyUI

```bash
python main.py
```

### 4. 加载工作流

1. 打开浏览器访问 `http://127.0.0.1:8188`
2. 点击右侧面板的 **Load** 按钮
3. 选择工作流文件（推荐 `balanced_workflow.json`）
4. 工作流将自动加载到画布

### 5. 配置参数

在 **配置节点** 中设置：

1. **API Key** - 你的UnlimitAI API密钥
2. **场景数量** - 需要生成的场景数
3. **作品标题** - 你的漫剧作品名称
4. **模型选择** - 文本、图像、视频、音频模型
5. **其他参数** - 根据需要调整

### 6. 输入小说文本

在 **小说分析节点** 中粘贴你的小说文本。

### 7. 运行工作流

点击 **Queue Prompt** 按钮开始生成。

## 工作流结构

每个工作流包含以下节点：

```
配置节点 (DramaConfigNode)
    ↓
成本估算 (CostEstimatorNode)
    ↓
小说分析 (NovelToDramaWorkflowNode)
    ↓
图像生成 (SceneImageGeneratorNode)
    ↓
视频生成 (SceneVideoGeneratorNode)
    ↓
音频生成 (SceneAudioGeneratorNode)
    ↓
输出整合 (DramaManifestNode)
```

## 输出格式

最终输出为 `manifest.json`，包含：

```json
{
  "title": "我的漫剧作品",
  "created_at": "2026-05-02",
  "total_scenes": 10,
  "scenes": [
    {
      "scene_number": 1,
      "title": "春日相遇",
      "description": "林晓薇在街上差点被车撞...",
      "characters": ["林晓薇", "陆晨轩"],
      "mood": "romantic",
      "dialogue": "(breath) 小心！你没事吧？",
      "visual_prompt": "Cinematic shot of a young woman...",
      "camera_movement": "slow zoom in",
      "image_url": "https://...",
      "video_url": "https://...",
      "dialogue_url": "https://...",
      "music_url": "https://..."
    }
  ]
}
```

## 成本对比

| 配置 | 文本 | 图像 | 视频 | 音频 | 音乐 | 总计 |
|------|------|------|------|------|------|------|
| 💰 最经济 | $0.0003 | $0.03 | $1.50 | $0.003 | $0.50 | **$2.03** |
| ⚖️ 性价比 | $0.0003 | $0.30 | $3.00 | $1.00 | $1.00 | **$5.30** |
| 🎯 优质 | $0.05 | $0.40 | $3.00 | $1.00 | $1.00 | **$5.45** |
| 👑 最佳质量 | $0.75 | $0.40 | $3.00 | $1.00 | $1.00 | **$6.15** |

*成本基于10个场景计算*

## 模型选择说明

### 文本模型

- **DeepSeek V3** ($0.0003) - 中文优秀，成本极低
- **GPT-4o** ($0.05) - 强推理，多语言
- **Claude Opus 4** ($0.75) - 最强推理，最佳中文理解

### 图像模型

- **FLUX Schnell** ($0.003) - 快速，经济
- **FLUX Pro** ($0.03) - 高质量，同步生成
- **Imagen 4** ($0.04) - 4K质量，最佳文本渲染

### 视频模型

- **VIDU v2** ($0.15-0.25) - 快速，经济
- **Kling v2** ($0.30) - 图生视频，数字人，对口型

### 音频模型

- **OpenAI TTS-1** ($0.000003/字符) - 标准
- **Minimax TTS** ($0.001/字符) - 中文最佳，情感标签

### 音乐模型

- **Suno Inspiration** ($0.05) - 随机风格
- **Suno Custom** ($0.10) - 可控风格，高质量

## 常见问题

### Q: 如何更换模型？
A: 在配置节点中直接选择不同的模型。

### Q: 如何查看成本？
A: 运行前查看成本估算节点的输出。

### Q: 生成失败怎么办？
A: 
1. 检查API Key是否正确
2. 确认账户余额充足
3. 查看节点输出的错误信息
4. 尝试降低场景数量或选择经济配置

### Q: URL过期怎么办？
A: 生成的资源URL有效期约1小时，请及时下载。

### Q: 如何提高质量？
A:
1. 选择优质或最佳质量配置
2. 提供更详细的小说文本
3. 在场景描述中添加更多细节

## 技术支持

- 插件目录: `/Users/aleven/.config/opencode/ComfyUI-UnlimitAI/`
- API文档: `/Users/aleven/Desktop/UnlimitAI_API_完整文档.md`
- 使用指南: `/Users/aleven/Desktop/ComfyUI_UnlimitAI_使用指南.md`

---

**版本**: 1.0.0  
**更新时间**: 2026-05-04
