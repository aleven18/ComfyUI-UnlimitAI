# ComfyUI 工作流使用指南

## 📋 工作流文件

### 主要工作流

| 文件名 | 说明 | 推荐场景 |
|--------|------|----------|
| `novel_to_drama_complete.json` | 完整工作流（6节点） | **推荐使用** |
| `novel_to_drama_workflow.json` | 简化版工作流 | 快速测试 |

### 辅助文件

| 文件名 | 说明 |
|--------|------|
| `WORKFLOW_GUIDE.md` | 完整使用指南 |
| `quick_start.py` | 命令行快速开始 |
| `validate_workflow.py` | 工作流验证工具 |

---

## 🚀 快速开始（ComfyUI）

### 步骤 1: 安装插件

```bash
# 方法 1: 复制到 ComfyUI custom_nodes 目录
cp -r /Users/aleven/.config/opencode/ComfyUI-UnlimitAI \
      /path/to/ComfyUI/custom_nodes/

# 方法 2: Git clone
cd /path/to/ComfyUI/custom_nodes/
git clone https://github.com/your-repo/ComfyUI-UnlimitAI.git
```

### 步骤 2: 重启 ComfyUI

```bash
cd /path/to/ComfyUI
python main.py

# 或使用 --listen 允许外部访问
python main.py --listen 0.0.0.0
```

### 步骤 3: 加载工作流

1. **打开 ComfyUI**
   - 浏览器访问: `http://127.0.0.1:8188`

2. **加载工作流文件**
   - 点击右侧菜单的 **"Load"** 按钮
   - 选择 `workflows/novel_to_drama_complete.json`
   - 工作流自动加载到画布

3. **或者拖拽加载**
   - 直接将 `novel_to_drama_complete.json` 文件拖到浏览器窗口

### 步骤 4: 配置 API Key

**在以下 4 个节点中填入相同的 API Key**:

1. **节点 1: 小说分析**
   - 找到 `api_key` 字段
   - 输入: `sk-xxxxxxxxxxxx`

2. **节点 2: 批量生成图像**
   - 找到 `api_key` 字段
   - 输入相同的 API Key

3. **节点 3: 批量生成视频**
   - 找到 `api_key` 字段
   - 输入相同的 API Key

4. **节点 4: 批量生成音频**
   - 找到 `api_key` 字段
   - 输入相同的 API Key

### 步骤 5: 输入小说文本

在 **节点 1: 小说分析** 中：

1. 找到 `novel_text` 字段
2. 粘贴您的中文小说文本（任意长度）
3. 调整 `num_scenes` 参数（建议 5-20）

### 步骤 6: 运行工作流

1. 点击右侧菜单的 **"Queue Prompt"** 按钮
2. 等待处理完成（10 场景约 15-30 分钟）
3. 观察节点执行进度

### 步骤 7: 查看结果

在 **节点 5: 整合资源清单** 中：

1. 右键点击节点
2. 选择 **"Inspect"** 或 **"Show Data"**
3. 查看 `manifest_json` 输出

---

## ⚙️ 节点参数详解

### 节点 1: 小说分析 (NovelToDramaWorkflowNode)

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| api_key | STRING | UnlimitAI API Key | 必填 |
| novel_text | STRING | 中文小说文本 | 任意长度 |
| num_scenes | INT | 提取场景数量 | 5-20 |
| text_model | CHOICE | 文本模型 | deepseek-chat |
| target_language | CHOICE | 目标语言 | english / chinese |
| art_style | CHOICE | 艺术风格 | cinematic |

**输出**:
- `scenes_json`: 场景 JSON 数据
- `summary`: 剧情概要
- `total_cost`: 预估成本

### 节点 2: 批量生成图像 (SceneImageGeneratorNode)

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| api_key | STRING | API Key | 必填 |
| scenes_json | STRING | 场景数据 | 自动输入 |
| image_model | CHOICE | 图像模型 | flux-pro |
| aspect_ratio | CHOICE | 画面比例 | 16:9 |
| max_scenes | INT | 最大场景数 | 与节点1相同 |

**输出**:
- `images_json`: 图像 URL 列表
- `summary`: 生成统计

### 节点 3: 批量生成视频 (SceneVideoGeneratorNode)

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| api_key | STRING | API Key | 必填 |
| images_json | STRING | 图像数据 | 自动输入 |
| video_model | CHOICE | 视频模型 | kling-v2 |
| duration | CHOICE | 视频时长 | 5 |
| aspect_ratio | CHOICE | 画面比例 | 16:9 |

**输出**:
- `videos_json`: 视频 URL 列表
- `summary`: 生成统计

### 节点 4: 批量生成音频 (SceneAudioGeneratorNode)

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| api_key | STRING | API Key | 必填 |
| scenes_json | STRING | 场景数据 | 自动输入 |
| voice_id | STRING | 音色 ID | male-qn-jingying |
| generate_music | BOOLEAN | 生成音乐 | true |
| max_scenes | INT | 最大场景数 | 与节点1相同 |

**输出**:
- `audio_json`: 音频 URL 列表
- `summary`: 生成统计

### 节点 5: 整合资源清单 (DramaManifestNode)

| 参数 | 类型 | 说明 | 来源 |
|------|------|------|------|
| scenes_json | STRING | 场景数据 | 节点1 |
| images_json | STRING | 图像数据 | 节点2 |
| videos_json | STRING | 视频数据 | 节点3 |
| audio_json | STRING | 音频数据 | 节点4 |
| title | STRING | 作品标题 | 自定义 |

**输出**:
- `manifest_json`: 完整资源清单
- `summary`: 工作流总结

---

## 📊 配置方案

### 方案 1: 经济配置（约 $3.80/10场景）

```yaml
节点1:
  text_model: deepseek-chat
  num_scenes: 10

节点2:
  image_model: flux-pro
  
节点3:
  video_model: vidu2
  duration: 5
  
节点4:
  voice_id: male-qn-jingying
  generate_music: true
```

### 方案 2: 标准配置（约 $4.40/10场景）⭐ 推荐

```yaml
节点1:
  text_model: deepseek-chat
  num_scenes: 10

节点2:
  image_model: flux-pro
  
节点3:
  video_model: kling-v2
  duration: 5
  
节点4:
  voice_id: male-qn-jingying
  generate_music: true
```

### 方案 3: 高质量配置（约 $6.60/10场景）

```yaml
节点1:
  text_model: gpt-4o
  num_scenes: 10

节点2:
  image_model: ideogram-v3
  
节点3:
  video_model: veo-3.1
  duration: 5
  
节点4:
  voice_id: male-qn-jingying
  generate_music: true
```

---

## 💡 使用技巧

### 技巧 1: 使用环境变量存储 API Key

```bash
# 设置环境变量
export UNLIMITAI_API_KEY="sk-xxxxxxxxxxxx"

# 在 ComfyUI 启动脚本中使用
UNLIMITAI_API_KEY="sk-xxx" python main.py
```

### 技巧 2: 分段处理长篇小说

对于超长小说（>10 章节）：

1. 将小说分段（每段 3-5 章）
2. 每段提取 10 个场景
3. 分别运行工作流
4. 合并多个 manifest.json

### 技巧 3: 批量下载资源

manifest.json 生成后：

```python
import json
import urllib.request

# 读取 manifest
with open('manifest.json', 'r') as f:
    data = json.load(f)

# 下载所有视频
for scene in data['scenes']:
    video_url = scene['video_url']
    filename = f"scene_{scene['scene_number']}.mp4"
    
    print(f"下载 {filename}...")
    urllib.request.urlretrieve(video_url, filename)
```

### 技巧 4: 自定义视觉提示词

在小说文本中插入视觉提示：

```
【场景：春日街道，阳光透过梧桐树叶，柔和光线】
林晓薇匆匆走在去公司的路上...

【镜头：特写，林晓薇惊讶的表情，眼神明亮】
"小心！"
```

### 技巧 5: 调整执行顺序

在 ComfyUI 中：

1. 可以单独运行某个节点（右键 → "Run this node"）
2. 可以暂停/继续工作流
3. 可以查看每个节点的输出

---

## ⚠️ 常见问题

### 问题 1: 找不到节点

**症状**: 工作流加载后节点显示为红色

**原因**: 插件未正确安装

**解决方案**:
```bash
# 检查插件是否在正确位置
ls /path/to/ComfyUI/custom_nodes/ComfyUI-UnlimitAI

# 重启 ComfyUI
python main.py
```

### 问题 2: 节点执行失败

**症状**: 节点显示红色错误

**可能原因**:
1. API Key 无效
2. 网络连接问题
3. API 余额不足
4. 参数配置错误

**解决方案**:
1. 检查 API Key 格式（以 `sk-` 开头）
2. 测试网络连接
3. 查看账户余额
4. 检查参数配置

### 问题 3: 输出 URL 无法访问

**症状**: 资源 URL 返回 404

**原因**: URL 已过期（通常 1 小时后过期）

**解决方案**:
- 及时下载资源
- 不要延迟处理

### 问题 4: 处理时间过长

**症状**: 工作流执行超过 1 小时

**原因**:
- 视频生成耗时
- API 队列繁忙
- 场景数量过多

**解决方案**:
- 减少场景数量
- 选择更快的模型（如 vidu2）
- 分批处理

### 问题 5: 成本超出预期

**症状**: API 费用过高

**解决方案**:
- 使用经济配置
- 减少场景数量
- 关闭音乐生成
- 监控使用量

---

## 📈 性能优化

### 优化 1: 减少视频时长

```
duration: "5"  # 5秒视频（推荐）
duration: "10" # 10秒视频（成本翻倍）
```

### 优化 2: 选择经济模型

```
# 经济顺序
video_model: vidu2 < kling-v2 < veo-3.1
image_model: flux-pro < ideogram-v3 < dall-e-3
```

### 优化 3: 批量处理

- 一次处理 10-20 个场景
- 避免频繁运行小批量任务
- 使用队列管理

---

## 📞 获取帮助

### 检查日志

ComfyUI 终端会显示详细日志：

```bash
# 查看错误信息
tail -f /path/to/ComfyUI/comfyui.log
```

### 验证工作流

```bash
cd workflows
python3 validate_workflow.py novel_to_drama_complete.json
```

### 相关文档

- **API 文档**: `/Users/aleven/Desktop/UnlimitAI_API_完整文档.md`
- **工作流指南**: `WORKFLOW_GUIDE.md`
- **项目文档**: `../README.md`

---

## ✅ 检查清单

运行工作流前，请确认：

- [ ] ComfyUI-UnlimitAI 插件已安装
- [ ] ComfyUI 已重启
- [ ] 工作流已正确加载
- [ ] 所有节点的 API Key 已填写
- [ ] 小说文本已输入
- [ ] 参数配置正确
- [ ] 账户余额充足

---

**版本**: 1.0.0

**最后更新**: 2026-05-02

**适用于**: ComfyUI
