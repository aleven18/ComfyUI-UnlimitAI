# 🎯 ComfyUI 作为 API 服务使用指南

## 📊 架构说明

你的需求：**前端独立界面 + ComfyUI作为API后端**

这正是我们的设计！

```
┌─────────────────────────────────┐
│  用户                            │
└──────────┬──────────────────────┘
           │
           ↓
┌─────────────────────────────────┐
│  前端Web界面 (独立)              │
│  http://localhost:3000           │
│  - React界面                     │
│  - 用户交互                      │
│  - 实时进度显示                  │
└──────────┬──────────────────────┘
           │ API调用
           ↓
┌─────────────────────────────────┐
│  ComfyUI (纯API服务)            │
│  http://127.0.0.1:8188           │
│  - 后端处理                      │
│  - 节点执行                      │
│  - 结果返回                      │
└─────────────────────────────────┘
```

---

## ✅ 前端已实现的API功能

### 1. REST API调用 ✅

```typescript
// 提交工作流
await client.queuePrompt(workflow)

// 上传文件
await client.uploadImage(file)

// 查询历史
await client.getHistory(promptId)

// 中断任务
await client.interrupt()

// 获取结果图片URL
client.getImageUrl(filename)
```

### 2. WebSocket实时通信 ✅

```typescript
// 实时进度更新
onProgress: (data) => {
  // 进度: data.value / data.max
}

// 节点执行状态
onExecuting: (node) => {
  // 当前执行节点: node
}

// 节点完成
onExecuted: (node, output) => {
  // 节点完成，获取输出
}

// 错误处理
onError: (error) => {
  // 错误处理
}
```

---

## 🚀 启动方式

### 方式1: 分别启动（推荐）

#### 步骤1: 启动ComfyUI API服务

```bash
cd "/Volumes/工作/comfyui"
source venv/bin/activate
python main.py --listen 127.0.0.1 --port 8188
```

**说明**:
- ComfyUI运行在 http://127.0.0.1:8188
- 只提供API服务
- 不需要打开Web界面

---

#### 步骤2: 启动前端界面（新终端）

```bash
cd /Users/aleven/.config/opencode/ComfyUI-UnlimitAI/web
npm run dev
```

**访问**: http://localhost:3000

---

### 方式2: 一键启动

```bash
cd /Users/aleven/.config/opencode/ComfyUI-UnlimitAI
./start.sh
```

**这会同时启动**:
- ComfyUI API服务（后台）
- 前端开发服务器

---

## 📋 使用流程

### 1. 启动服务

```bash
# 终端1: ComfyUI API
cd "/Volumes/工作/comfyui"
source venv/bin/activate
python main.py

# 终端2: 前端界面
cd /Users/aleven/.config/opencode/ComfyUI-UnlimitAI/web
npm run dev
```

---

### 2. 访问前端界面

打开浏览器访问: **http://localhost:3000**

---

### 3. 配置API Key

在前端界面的"参数配置"面板输入你的UnlimitAI API Key

---

### 4. 开始使用

1. **输入小说文本**
2. **选择预设模式**
3. **配置参数**
4. **点击"开始转换"**

前端会自动：
- 调用ComfyUI API提交工作流
- 通过WebSocket接收实时进度
- 显示生成结果

---

## 🔧 API端点说明

### ComfyUI提供的API端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/prompt` | POST | 提交工作流 |
| `/upload/image` | POST | 上传文件 |
| `/history/{id}` | GET | 查询历史 |
| `/view` | GET | 获取结果文件 |
| `/interrupt` | POST | 中断任务 |
| `/queue` | POST | 管理队列 |
| `/ws` | WebSocket | 实时通信 |

---

## 💡 前端优势

### 相比ComfyUI原生界面

**前端独立界面**：
- ✅ 更简洁的用户体验
- ✅ 专为小说转漫剧优化
- ✅ 实时进度可视化
- ✅ 参数配置更直观
- ✅ 成本预估功能

**ComfyUI原生界面**：
- ✅ 通用节点编辑器
- ✅ 可视化工作流
- ✅ 适合高级用户

---

## 🎯 典型使用场景

### 场景1: 纯API模式

**只启动ComfyUI**：
```bash
python main.py
```

**使用场景**：
- 通过API调用
- 集成到其他系统
- 自动化脚本

---

### 场景2: 前端+API模式

**同时启动前端和ComfyUI**：
```bash
./start.sh
```

**使用场景**：
- 日常使用
- 可视化操作
- 实时监控

---

### 场景3: 多用户访问

**ComfyUI监听所有接口**：
```bash
python main.py --listen 0.0.0.0
```

**前端配置**：
```typescript
// 修改API地址
const client = new ComfyUIClient('http://your-server:8188')
```

**使用场景**：
- 局域网访问
- 多人协作
- 远程服务

---

## 🔒 安全配置（生产环境）

### 1. 限制监听地址

```bash
# 只监听本地
python main.py --listen 127.0.0.1

# 局域网访问
python main.py --listen 0.0.0.0
```

---

### 2. 使用反向代理（推荐）

**Nginx配置**：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端
    location / {
        proxy_pass http://localhost:3000;
    }
    
    # ComfyUI API
    location /api/ {
        proxy_pass http://127.0.0.1:8188/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📊 性能优化

### 1. 前端优化

**构建生产版本**：
```bash
cd web
npm run build
npm run preview
```

**优势**：
- 更小的文件大小
- 更快的加载速度
- 更好的性能

---

### 2. API优化

**启用压缩**：
```bash
python main.py --enable-compression
```

**调整超时**：
```bash
python main.py --timeout 300
```

---

## 🐛 常见问题

### 问题1: 前端无法连接ComfyUI

**检查**：
```bash
# 确认ComfyUI正在运行
curl http://127.0.0.1:8188/system_stats
```

**解决**：
- 确认ComfyUI已启动
- 检查端口是否正确
- 查看防火墙设置

---

### 问题2: WebSocket连接失败

**检查**：
```bash
# 查看浏览器控制台
# WebSocket connection to 'ws://127.0.0.1:8188/ws' failed
```

**解决**：
- 确认WebSocket支持
- 检查网络代理设置
- 使用正确的ws://协议

---

### 问题3: 跨域问题

**现象**：
```
Access to XMLHttpRequest at 'http://127.0.0.1:8188' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**解决**：
- Vite已配置代理，无需处理
- 生产环境使用Nginx反向代理

---

## 📋 快速命令参考

### 启动服务

```bash
# 方式1: 分别启动
# 终端1
cd "/Volumes/工作/comfyui"
source venv/bin/activate
python main.py

# 终端2
cd /Users/aleven/.config/opencode/ComfyUI-UnlimitAI/web
npm run dev

# 方式2: 一键启动
cd /Users/aleven/.config/opencode/ComfyUI-UnlimitAI
./start.sh
```

### 访问地址

- **前端界面**: http://localhost:3000
- **ComfyUI API**: http://127.0.0.1:8188

### 管理命令

```bash
./stop.sh      # 停止服务
./status.sh    # 查看状态
```

---

## 🎯 总结

**完美适配你的需求！**

✅ **前端独立界面** - React Web应用  
✅ **ComfyUI作为API** - 纯后端服务  
✅ **完整API调用** - REST + WebSocket  
✅ **实时通信** - 进度更新  
✅ **开箱即用** - 无需修改  

**现在就可以启动使用！**

```bash
cd /Users/aleven/.config/opencode/ComfyUI-UnlimitAI
./start.sh
```

然后访问: http://localhost:3000 🚀
