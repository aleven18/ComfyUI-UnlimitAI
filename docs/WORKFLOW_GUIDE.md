# 工作流使用指南

本文档详细介绍如何使用ComfyUI-UnlimitAI提供的4套预设工作流。

---

## 📋 目录

- [工作流概述](#工作流概述)
- [快速开始](#快速开始)
- [工作流详解](#工作流详解)
- [自定义工作流](#自定义工作流)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

---

## 工作流概述

ComfyUI-UnlimitAI提供4套预设工作流，满足不同场景需求：

| 工作流 | 质量等级 | 成本等级 | 适用场景 | 推荐人群 |
|--------|----------|----------|----------|----------|
| **Budget** | ⭐⭐ | 💰 最便宜 | 快速测试、原型验证 | 开发者、测试人员 |
| **Balanced** | ⭐⭐⭐ | 💰💰 适中 | 日常使用、内容创作 | 内容创作者、个人用户 |
| **Quality** | ⭐⭐⭐⭐ | 💰💰💰 较高 | 正式发布、商业内容 | 专业创作者、工作室 |
| **Max Quality** | ⭐⭐⭐⭐⭐ | 💰💰💰💰 最高 | 顶级质量需求 | 电影级制作、商业项目 |

---

## 快速开始

### 1. 选择工作流

根据你的需求选择合适的工作流：

```bash
# 工作流文件位置
workflows/
├── budget_workflow.json      # 成本优化
├── balanced_workflow.json    # 平衡模式（推荐新手）
├── quality_workflow.json     # 质量优先
└── max_quality_workflow.json # 极致质量
```

### 2. 加载工作流

在ComfyUI中：

1. 打开ComfyUI界面
2. 点击 "Load" 按钮
3. 选择对应的工作流JSON文件
4. 工作流将自动加载到画布

### 3. 配置API Key

确保已配置UnlimitAI API Key：

```bash
# 方法1: 环境变量
export UNITED_API_KEY="your_api_key_here"

# 方法2: .env文件
echo "UNITED_API_KEY=your_api_key_here" > .env
```

### 4. 运行工作流

1. 调整节点参数（可选）
2. 点击 "Queue Prompt" 运行
3. 等待生成完成
4. 查看输出结果

---

## 工作流详解

### 1. Budget Workflow (成本优化)

**文件**: `workflows/budget_workflow.json`

**特点**:
- 使用最经济的模型组合
- 快速生成速度
- 适合快速测试和迭代
- **成本节省**: 约61%

**模型选择**:
```yaml
文本模型: DeepSeek Chat      # 极低成本
图像模型: FLUX.1 Schnell     # 快速生成
视频模型: Kling Video V2     # 性价比高
音频模型: TTS-1              # 标准质量
音乐模型: MusicGen           # 开源免费
```

**适用场景**:
- ✅ 快速原型测试
- ✅ 概念验证
- ✅ 学习和实验
- ✅ 预算有限的项目

**示例输出质量**:
- 文本: 流畅连贯
- 图像: 清晰度中等，细节一般
- 视频: 720p质量
- 音频: 标准质量
- 总体: 可用，但不够精细

**预期成本**:
```
示例: 生成1分钟视频内容
- 文本生成: $0.0001
- 图像生成 (3张): $0.009
- 视频生成: $0.10
- 音频生成: $0.0001
- 音乐生成: $0.001
-------------------
总计: ~$0.11
```

---

### 2. Balanced Workflow (平衡模式)

**文件**: `workflows/balanced_workflow.json`

**特点**:
- 平衡质量和成本
- 推荐日常使用
- 良好的生成质量
- **成本节省**: 约45%

**模型选择**:
```yaml
文本模型: DeepSeek Chat      # 优秀的中文能力
图像模型: FLUX.1 Dev         # 更高质量
视频模型: Kling Video V2     # 稳定可靠
音频模型: Minimax TTS        # 自然音色
音乐模型: MusicGen           # 多样风格
```

**适用场景**:
- ✅ 日常内容创作
- ✅ 社交媒体内容
- ✅ 教育内容
- ✅ 个人项目

**示例输出质量**:
- 文本: 优秀，细节丰富
- 图像: 清晰度高，细节较好
- 视频: 1080p质量
- 音频: 自然流畅
- 总体: 质量良好，性价比高

**预期成本**:
```
示例: 生成1分钟视频内容
- 文本生成: $0.0001
- 图像生成 (3张): $0.030
- 视频生成: $0.10
- 音频生成: $0.0002
- 音乐生成: $0.001
-------------------
总计: ~$0.13
```

---

### 3. Quality Workflow (质量优先)

**文件**: `workflows/quality_workflow.json`

**特点**:
- 高质量输出
- 使用顶级模型
- 适合正式发布
- **成本节省**: 约30%

**模型选择**:
```yaml
文本模型: GPT-4 Turbo        # 顶级理解能力
图像模型: Ideogram V2        # 最佳细节
视频模型: Runway Gen-3 Turbo # 专业级质量
音频模型: Minimax TTS        # 自然音色
音乐模型: Stable Audio 2.0   # 高保真
```

**适用场景**:
- ✅ 商业内容发布
- ✅ 营销素材
- ✅ 专业作品集
- ✅ 高要求项目

**示例输出质量**:
- 文本: 专业级，富有创意
- 图像: 高清晰度，细节丰富
- 视频: 1080p，专业级质量
- 音频: 高质量，情感丰富
- 总体: 接近专业制作水准

**预期成本**:
```
示例: 生成1分钟视频内容
- 文本生成: $0.03
- 图像生成 (3张): $0.15
- 视频生成: $0.25
- 音频生成: $0.0002
- 音乐生成: $0.002
-------------------
总计: ~$0.43
```

---

### 4. Max Quality Workflow (极致质量)

**文件**: `workflows/max_quality_workflow.json`

**特点**:
- 最高质量输出
- 使用最先进模型
- 电影级制作水准
- **不设成本上限**

**模型选择**:
```yaml
文本模型: Claude 3 Opus      # 最强理解能力
图像模型: Ideogram V2        # 最佳视觉效果
视频模型: Runway Gen-3 Turbo # 顶级视频质量
音频模型: Minimax TTS        # 情感丰富
音乐模型: Stable Audio 2.0   # 专业音乐质量
```

**适用场景**:
- ✅ 电影级制作
- ✅ 高端商业项目
- ✅ 艺术创作
- ✅ 质量至上的场景

**示例输出质量**:
- 文本: 文学级，富有深度
- 图像: 超高清，艺术级
- 视频: 接近电影质量
- 音频: 专业配音水准
- 总体: 专业制作级别

**预期成本**:
```
示例: 生成1分钟视频内容
- 文本生成: $0.15
- 图像生成 (3张): $0.15
- 视频生成: $0.25
- 音频生成: $0.0002
- 音乐生成: $0.002
-------------------
总计: ~$0.55
```

---

## 自定义工作流

### 修改现有工作流

1. **打开工作流JSON文件**
2. **修改节点参数**:

```json
{
  "nodes": [
    {
      "id": 1,
      "type": "TextGeneratorNode",
      "inputs": {
        "model": "deepseek-chat",  // 可修改模型
        "temperature": 0.7,         // 调整创造性
        "max_tokens": 1000          // 控制长度
      }
    }
  ]
}
```

### 创建自定义工作流

1. **在ComfyUI中设计流程**
2. **连接节点**
3. **配置参数**
4. **保存为JSON**

### 工作流模板

创建 `my_custom_workflow.json`:

```json
{
  "name": "My Custom Workflow",
  "description": "Custom workflow for specific use case",
  "nodes": [
    {
      "id": 1,
      "type": "NovelAnalyzerNode",
      "inputs": {
        "novel_text": "",
        "extract_scenes": true
      }
    },
    {
      "id": 2,
      "type": "CharacterImageLoaderNode",
      "inputs": {
        "character_name": "",
        "style": "anime"
      }
    }
  ],
  "links": [
    [1, 0, 2, 0]  // 连接节点1的输出0到节点2的输入0
  ]
}
```

---

## 最佳实践

### 1. 选择合适的模型

**文本模型选择指南**:
```
需要速度 → DeepSeek Chat
需要推理 → DeepSeek Reasoner  
需要创意 → GPT-4 Turbo
需要理解 → Claude 3 Opus
```

**图像模型选择指南**:
```
快速生成 → FLUX.1 Schnell
高质量 → FLUX.1 Dev
文字渲染 → Ideogram V2
真实照片 → Imagen 3.0
```

**视频模型选择指南**:
```
性价比 → Kling Video V2
质量优先 → Runway Gen-3 Turbo
创意动画 → Pika 2.0
```

### 2. 优化提示词

**好的提示词特征**:
- ✅ 具体明确
- ✅ 包含关键细节
- ✅ 指定风格和氛围
- ✅ 适当的长度

**示例**:
```
# 好的提示词
"一个穿着蓝色碎花连衣裙的年轻女孩，站在樱花树下，
微风拂过，花瓣飘落，温暖的午后阳光，日系动漫风格，
柔和色调，高清细节"

# 差的提示词
"女孩站在树下"
```

### 3. 控制成本

**成本优化技巧**:
1. 使用Budget工作流测试
2. 满意后再用Quality工作流
3. 启用缓存功能
4. 批量处理提高效率
5. 选择合适的图像尺寸

### 4. 质量控制

**提高质量的技巧**:
1. 使用详细的提示词
2. 添加负面提示词
3. 调整temperature参数
4. 多次生成选择最佳
5. 后期优化处理

---

## 故障排除

### 常见问题

#### Q1: API调用失败

**解决方案**:
```bash
# 检查API Key配置
echo $UNITED_API_KEY

# 检查网络连接
curl https://api.unlimitai.com/health

# 查看错误日志
tail -f logs/unlimitai.log
```

#### Q2: 生成质量不满意

**解决方案**:
1. 改进提示词
2. 调整模型参数
3. 尝试不同模型
4. 使用更高质量工作流

#### Q3: 生成速度慢

**解决方案**:
1. 使用Budget工作流
2. 减小图像尺寸
3. 降低视频时长
4. 使用并行处理

#### Q4: 成本超预算

**解决方案**:
1. 使用Budget工作流
2. 启用缓存
3. 优化提示词减少重试
4. 批量处理提高效率

---

## 高级技巧

### 1. 工作流组合

可以组合多个工作流实现复杂功能：

```
工作流1: 小说分析 → 提取角色和场景
工作流2: 角色生成 → 创建角色立绘
工作流3: 场景生成 → 生成场景插画
工作流4: 视频合成 → 合成最终视频
```

### 2. 参数调优

根据内容类型调整参数：

```python
# 激情场景
temperature = 0.9  # 更高创造性
top_p = 0.95

# 技术文档
temperature = 0.3  # 更确定性
top_p = 0.8

# 平衡创作
temperature = 0.7  # 平衡
top_p = 0.9
```

### 3. 批量处理

使用脚本批量处理：

```python
from utils.api_client import UnlimitAIClient

client = UnlimitAIClient()

# 批量生成
prompts = ["场景1", "场景2", "场景3"]
results = [client.generate_text(p) for p in prompts]
```

---

## 总结

选择工作流的建议：

- 🚀 **快速测试** → Budget Workflow
- 💡 **日常使用** → Balanced Workflow（推荐）
- 🎯 **正式发布** → Quality Workflow
- 💎 **顶级质量** → Max Quality Workflow

记住：先用Budget测试，满意后再用Quality生成最终版本！

---

## 获取帮助

- 📖 查看 [README.md](../README.md)
- 📚 查看 [DEVELOPMENT.md](../DEVELOPMENT.md)
- 💬 在 [Discussions](https://github.com/your-repo/discussions) 提问
- 🐛 在 [Issues](https://github.com/your-repo/issues) 报告问题

---

**祝你创作愉快！** 🎨
