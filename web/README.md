# 🌐 ComfyUI-UnlimitAI Web Interface

基于 React + TypeScript + Tailwind CSS 构建的 Web 前端界面，通过 ComfyUI API 调用后端插件。

---

## 📊 项目架构

```
┌─────────────────────────────────┐
│   Web Frontend (本项目)          │
│   - React 18 + TypeScript       │
│   - Tailwind CSS                │
│   - Zustand 状态管理             │
│   - Axios + WebSocket           │
└──────────┬──────────────────────┘
           │ HTTP + WebSocket
           ↓
┌─────────────────────────────────┐
│   ComfyUI Server (localhost:8188)│
│   - 提供 REST API               │
│   - WebSocket 实时通信          │
└──────────┬──────────────────────┘
           │
           ↓
┌─────────────────────────────────┐
│   ComfyUI-UnlimitAI 插件        │
│   - 59个自定义节点              │
│   - 工作流执行引擎              │
└─────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 前置要求

- Node.js 18+
- npm 或 yarn
- ComfyUI 运行在 `http://127.0.0.1:8188`

### 2. 安装依赖

```bash
cd web
npm install
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 `http://localhost:3000`

### 4. 构建生产版本

```bash
npm run build
```

---

## 📁 项目结构

```
web/
├── src/
│   ├── components/          # UI 组件
│   │   ├── NovelInput.tsx      # 小说输入
│   │   ├── ConfigPanel.tsx     # 参数配置
│   │   ├── ProgressMonitor.tsx # 进度监控
│   │   └── ResultGallery.tsx   # 结果展示
│   ├── lib/                 # 核心库
│   │   ├── comfyui-client.ts   # ComfyUI API 客户端
│   │   └── workflow-manager.ts # 工作流管理
│   ├── hooks/               # React Hooks
│   │   └── useComfyUI.ts       # ComfyUI 状态管理
│   ├── store/               # 状态管理
│   │   └── index.ts            # Zustand Store
│   ├── types/               # TypeScript 类型
│   │   └── index.ts
│   ├── workflows/           # 工作流模板
│   ├── App.tsx              # 主应用
│   ├── main.tsx             # 入口文件
│   └── index.css            # 样式文件
├── index.html               # HTML 模板
├── package.json             # 依赖配置
├── tsconfig.json            # TypeScript 配置
├── vite.config.ts           # Vite 配置
└── tailwind.config.js       # Tailwind 配置
```

---

## 🎯 核心功能

### 1. 小说输入

- 文本输入框
- 文件上传（.txt, .md）
- 字数统计

### 2. 参数配置

- API Key 配置
- 预设模式选择（budget/balanced/quality/max_quality）
- 项目名称
- 场景数量
- 语言选择
- 画面风格
- 成本预估

### 3. 实时进度

- 进度条显示
- 当前节点高亮
- 实时日志输出
- 错误提示

### 4. 结果展示

- 图片预览
- 视频播放
- 音频播放
- 下载导出

---

## 🔧 API 集成

### ComfyUI API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/prompt` | POST | 提交工作流 |
| `/upload/image` | POST | 上传文件 |
| `/history/{id}` | GET | 查询历史 |
| `/interrupt` | POST | 中断任务 |
| `/view` | GET | 获取结果 |
| `/ws` | WebSocket | 实时通信 |

### WebSocket 消息类型

```typescript
// 进度更新
{ type: 'progress', data: { value: number, max: number } }

// 节点执行
{ type: 'executing', data: { node: string } }

// 节点完成
{ type: 'executed', data: { node: string, output: any } }

// 错误
{ type: 'execution_error', data: any }
```

---

## 🎨 自定义开发

### 添加新组件

```tsx
// src/components/MyComponent.tsx
import React from 'react';

export function MyComponent() {
  return (
    <div className="...">
      {/* Your code */}
    </div>
  );
}
```

### 扩展 API 客户端

```typescript
// src/lib/comfyui-client.ts
async myNewMethod() {
  const response = await this.client.get('/my-endpoint');
  return response.data;
}
```

### 添加新工作流

```typescript
// src/lib/workflow-manager.ts
static getTemplate(preset: PresetType): ComfyUIWorkflow {
  const templates = {
    // ... 添加新预设
    custom: customWorkflow,
  };
}
```

---

## 🌐 生产部署

### 构建

```bash
npm run build
```

生成的文件在 `dist/` 目录

### 部署选项

#### 1. Nginx

```nginx
server {
  listen 80;
  server_name your-domain.com;
  
  location / {
    root /path/to/dist;
    try_files $uri $uri/ /index.html;
  }
  
  location /api/ {
    proxy_pass http://127.0.0.1:8188/;
  }
  
  location /ws/ {
    proxy_pass http://127.0.0.1:8188/ws/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

#### 2. Docker

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 3. Vercel / Netlify

直接连接 GitHub 仓库自动部署

---

## 🔒 环境变量

创建 `.env` 文件：

```bash
VITE_COMFYUI_URL=http://127.0.0.1:8188
```

在代码中使用：

```typescript
const comfyUIClient = new ComfyUIClient(import.meta.env.VITE_COMFYUI_URL);
```

---

## 🎯 待开发功能

- [ ] 工作流可视化编辑
- [ ] 自定义工作流构建
- [ ] 历史记录管理
- [ ] 批量处理
- [ ] 多语言支持（i18n）
- [ ] 暗色模式
- [ ] 移动端适配
- [ ] PWA 支持

---

## 📚 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2 | UI 框架 |
| TypeScript | 5.0 | 类型安全 |
| Vite | 5.0 | 构建工具 |
| Tailwind CSS | 3.3 | 样式框架 |
| Zustand | 4.4 | 状态管理 |
| Axios | 1.6 | HTTP 客户端 |
| Lucide React | 0.294 | 图标库 |

---

## 🐛 常见问题

### 1. 无法连接到 ComfyUI

**检查**:
- ComfyUI 是否运行在 `http://127.0.0.1:8188`
- 防火墙是否阻止连接
- 查看浏览器控制台错误

### 2. WebSocket 连接失败

**解决**:
- 检查 WebSocket URL 是否正确
- 确认 ComfyUI 支持 WebSocket
- 查看网络面板

### 3. 工作流提交失败

**检查**:
- API Key 是否正确
- 工作流 JSON 格式是否正确
- 查看服务器日志

---

## 📖 相关文档

- [ComfyUI API 文档](https://github.com/comfyanonymous/ComfyUI)
- [React 文档](https://react.dev)
- [Tailwind CSS 文档](https://tailwindcss.com)
- [Zustand 文档](https://docs.pmnd.rs/zustand)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License

---

**Made with ❤️ by ComfyUI-UnlimitAI Team**
