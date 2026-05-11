# 📊 项目大小统计报告

## 🎯 快速概览

**插件大小**: 142 MB  
**ComfyUI models**: 2.7 GB  
**ComfyUI总计**: ~3-5 GB (估计，SMB网络盘查询慢)

---

## 📋 详细大小

### 1. ComfyUI-UnlimitAI 插件 ✅

**总大小**: **142 MB**

**详细分布**:
```
web/              140 MB  (前端，含node_modules)
nodes/            232 KB  (节点代码)
docs/             432 KB  (文档)
utils/            144 KB  (工具库)
tests/            108 KB  (测试)
workflows/        104 KB  (工作流模板)
scripts/           52 KB  (脚本)
其他文件           ~2 MB  (配置、文档等)
```

**说明**:
- 前端占大部分（140MB），主要是node_modules
- 核心代码很小（~1MB）
- 文档完善（432KB）

---

### 2. ComfyUI 核心

**已知大小**:
```
models/           2.7 GB  (模型文件)
venv/             ~1-2 GB (估计，Python虚拟环境)
custom_nodes/     32 KB   (插件链接)
ComfyUI核心       ~500 MB (估计)
```

**总计估计**: **3-5 GB**

**说明**:
- models目录已有2.7GB（可能有预下载的模型）
- venv包含所有Python依赖
- SMB网络盘导致查询缓慢

---

## 💾 迁移建议

### 如果要迁移到本地

**需要复制的文件**:
- ComfyUI核心 + venv + models: **~3-5 GB**
- 插件: **142 MB** (已在本地)

**总计**: **~3.2-5.2 GB**

**预计时间**:
- 本地SSD复制: **2-5分钟**
- SMB网络盘: **无法估算**（太慢）

---

## 🎯 空间优化建议

### 可以不迁移的部分

**1. models目录 (2.7 GB)**
- 可以保留在SMB网络盘
- 使用符号链接指向网络盘
- 节省本地空间

**2. venv (1-2 GB)**
- 可以在本地重新创建
- 只需5-10分钟
- 避免复制慢速网络盘

---

## 💡 最优迁移方案

### 方案A: 完整迁移（推荐）

**复制内容**: 3-5 GB  
**时间**: 2-5分钟（本地SSD）  
**优势**: 完全独立，速度快

```bash
cp -r "/Volumes/工作/comfyui" ~/ComfyUI
```

---

### 方案B: 最小迁移（节省空间）

**只迁移核心**: ~500 MB  
**保留models在SMB**: 2.7 GB  
**时间**: 1-2分钟

```bash
# 创建本地ComfyUI
mkdir -p ~/ComfyUI
cd ~/ComfyUI

# 复制核心文件
cp -r "/Volumes/工作/comfyui"/{comfy,comfy_extras,nodes.py,main.py,requirements.txt} .

# 创建venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 链接models（节省空间）
ln -s "/Volumes/工作/comfyui/models" models

# 链接插件
mkdir -p custom_nodes
ln -s /Users/aleven/.config/opencode/ComfyUI-UnlimitAI custom_nodes/
```

**优势**:
- ✅ 节省2.7GB本地空间
- ✅ 启动速度快
- ✅ models可以共享

---

## 📊 大小对比

| 项目 | SMB网络盘 | 本地SSD |
|------|-----------|---------|
| 插件 | 142 MB | ✅ 已在本地 |
| ComfyUI核心 | ~500 MB | 可迁移 |
| venv | 1-2 GB | 可重建 |
| models | 2.7 GB | 可保留SMB |

---

## 🚀 推荐方案

**综合考虑**:

### ✅ 推荐方案B（最小迁移）

**理由**:
1. ✅ 节省2.7GB本地空间
2. ✅ 启动速度快（本地核心）
3. ✅ models可共享
4. ✅ 迁移时间短（1-2分钟）

**所需空间**: **~500 MB**

---

## 📞 需要执行？

**告诉我**:
- **"完整迁移"** - 复制全部（3-5GB）
- **"最小迁移"** - 只复制核心（500MB）⭐推荐
- **"不迁移"** - 继续使用SMB

**我会立即帮你执行！** 🚀
