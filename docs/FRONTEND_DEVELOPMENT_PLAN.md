# 🌐 独立前端开发方案

## 📊 项目架构

```
┌─────────────────────────────────────────┐
│         用户界面 (新开发)                │
│  - Web App / Desktop App / Mobile App   │
│  - 简洁的操作流程                        │
│  - 实时进度显示                          │
└──────────────┬──────────────────────────┘
               │ HTTP API + WebSocket
               ↓
┌─────────────────────────────────────────┐
│         ComfyUI Server                   │
│  - 运行在本地或远程服务器                │
│  - 提供 REST API (端口 8188)             │
│  - 提供 WebSocket 实时通信               │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│    ComfyUI-UnlimitAI 插件               │
│  - 59个自定义节点                       │
│  - 工作流执行引擎                       │
└─────────────────────────────────────────┘
```

---

## ✅ 可行性分析

### ComfyUI 提供的 API

| API | 端点 | 功能 |
|-----|------|------|
| **REST API** | `http://127.0.0.1:8188` | 完整的 HTTP 接口 |
| **WebSocket** | `ws://127.0.0.1:8188/ws` | 实时进度推送 |
| **上传文件** | `POST /upload/image` | 上传图片/视频 |
| **提交工作流** | `POST /prompt` | 执行工作流 |
| **查询进度** | `GET /history/{id}` | 查询执行状态 |
| **获取结果** | `GET /view` | 获取生成结果 |
| **中断执行** | `POST /interrupt` | 停止当前任务 |
| **清空队列** | `POST /queue` | 管理任务队列 |

### 核心功能支持

```
✅ 提交工作流 (JSON格式)
✅ 实时进度更新 (WebSocket)
✅ 获取生成结果 (图片/视频/音频)
✅ 管理任务队列
✅ 上传输入文件
✅ 查看历史记录
✅ 中断/重试任务
```

---

## 🎯 开发方案对比

### 方案A: Web 应用 ⭐⭐⭐⭐⭐ 推荐

**技术栈**:
```
前端: React + TypeScript + Tailwind CSS
状态管理: Zustand / Redux Toolkit
UI组件: Shadcn UI / Ant Design
工作流可视化: React Flow
实时通信: WebSocket + Socket.io
构建工具: Vite / Next.js
```

**优势**:
- ✅ 跨平台 (浏览器访问)
- ✅ 易于部署
- ✅ 开发生态丰富
- ✅ 用户体验好

**工作量**: 2-3周

---

### 方案B: 桌面应用 ⭐⭐⭐⭐

**技术栈**:
```
框架: Electron / Tauri
前端: React / Vue
打包: Electron Builder
```

**优势**:
- ✅ 本地运行
- ✅ 更好的性能
- ✅ 文件系统访问
- ✅ 离线使用

**工作量**: 3-4周

---

### 方案C: 移动应用 ⭐⭐⭐

**技术栈**:
```
框架: React Native / Flutter
状态管理: Redux / Provider
```

**优势**:
- ✅ 移动端使用
- ✅ 随时随地

**劣势**:
- ⚠️ 屏幕限制
- ⚠️ 功能简化

**工作量**: 4-5周

---

## 🚀 推荐方案：Web 应用

### 功能模块设计

```
1. 小说输入模块
   ├─ 文本输入框
   ├─ 文件上传
   └─ 历史记录

2. 参数配置模块
   ├─ API Key 配置
   ├─ 模型选择
   ├─ 风格设置
   └─ 成本预估

3. 实时进度模块
   ├─ 当前节点
   ├─ 进度条
   ├─ 日志输出
   └─ 错误提示

4. 结果展示模块
   ├─ 图片预览
   ├─ 视频播放
   ├─ 音频播放
   └─ 下载导出

5. 工作流可视化 (可选)
   ├─ 节点图表
   ├─ 连接关系
   └─ 实时高亮
```

---

## 📋 核心代码示例

### 1. ComfyUI API 客户端

```typescript
// lib/comfyui-client.ts
import axios from 'axios';

const COMFYUI_URL = 'http://127.0.0.1:8188';

export class ComfyUIClient {
  private clientId: string;
  
  constructor() {
    this.clientId = Math.random().toString(36).substring(7);
  }

  // 提交工作流
  async queuePrompt(workflow: any) {
    const response = await axios.post(`${COMFYUI_URL}/prompt`, {
      prompt: workflow,
      client_id: this.clientId
    });
    return response.data.prompt_id;
  }

  // 上传文件
  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append('image', file);
    
    const response = await axios.post(
      `${COMFYUI_URL}/upload/image`,
      formData
    );
    return response.data;
  }

  // 获取历史记录
  async getHistory(promptId: string) {
    const response = await axios.get(
      `${COMFYUI_URL}/history/${promptId}`
    );
    return response.data;
  }

  // WebSocket 实时通信
  connectWebSocket(onProgress: Function) {
    const ws = new WebSocket(`ws://127.0.0.1:8188/ws?clientId=${this.clientId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onProgress(data);
    };
    
    return ws;
  }
}
```

---

### 2. 工作流模板管理

```typescript
// lib/workflow-templates.ts
import budgetWorkflow from '../workflows/budget_workflow.json';
import balancedWorkflow from '../workflows/balanced_workflow.json';
import qualityWorkflow from '../workflows/quality_workflow.json';

export class WorkflowManager {
  // 获取工作流模板
  static getTemplate(preset: 'budget' | 'balanced' | 'quality') {
    const templates = {
      budget: budgetWorkflow,
      balanced: balancedWorkflow,
      quality: qualityWorkflow
    };
    
    return templates[preset];
  }

  // 填充参数
  static fillWorkflow(template: any, params: any) {
    // 遍历节点，填充用户参数
    template.nodes.forEach((node: any) => {
      if (node.type === 'DramaConfigNode') {
        node.widgets_values[0] = params.apiKey;
        node.widgets_values[1] = params.maxScenes;
        // ... 更多参数
      }
    });
    
    return template;
  }
}
```

---

### 3. React 组件示例

```tsx
// components/NovelConverter.tsx
import { useState } from 'react';
import { ComfyUIClient } from '../lib/comfyui-client';
import { WorkflowManager } from '../lib/workflow-templates';

const client = new ComfyUIClient();

export function NovelConverter() {
  const [novel, setNovel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('idle');
  const [results, setResults] = useState<any[]>([]);

  const handleConvert = async () => {
    setStatus('processing');
    
    // 1. 获取工作流模板
    const workflow = WorkflowManager.getTemplate('balanced');
    
    // 2. 填充参数
    const filledWorkflow = WorkflowManager.fillWorkflow(workflow, {
      apiKey,
      novelText: novel
    });
    
    // 3. 连接 WebSocket
    const ws = client.connectWebSocket((data: any) => {
      if (data.type === 'progress') {
        setProgress(data.data.value / data.data.max * 100);
      }
      if (data.type === 'executed') {
        setResults(prev => [...prev, data.data.output]);
      }
    });
    
    // 4. 提交工作流
    const promptId = await client.queuePrompt(filledWorkflow);
    
    // 5. 等待完成
    // ... 监听 WebSocket 完成事件
  };

  return (
    <div className="container mx-auto p-6">
      {/* 输入区域 */}
      <textarea
        value={novel}
        onChange={(e) => setNovel(e.target.value)}
        placeholder="输入小说文本..."
        className="w-full h-64 p-4 border rounded"
      />
      
      {/* 配置区域 */}
      <input
        type="password"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
        placeholder="API Key"
        className="w-full p-2 border rounded mt-4"
      />
      
      {/* 转换按钮 */}
      <button
        onClick={handleConvert}
        disabled={status === 'processing'}
        className="mt-4 px-6 py-2 bg-blue-500 text-white rounded"
      >
        开始转换
      </button>
      
      {/* 进度显示 */}
      {status === 'processing' && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-center mt-2">{progress.toFixed(0)}%</p>
        </div>
      )}
      
      {/* 结果展示 */}
      {results.length > 0 && (
        <div className="mt-6 grid grid-cols-3 gap-4">
          {results.map((result, idx) => (
            <div key={idx} className="border rounded p-2">
              <img 
                src={`http://127.0.0.1:8188/view?filename=${result.images[0].filename}`}
                alt={`Result ${idx}`}
                className="w-full"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## 🎨 UI 设计建议

### 简洁流程设计

```
步骤 1: 输入小说
┌──────────────────────┐
│  文本输入框          │
│  或文件上传          │
└──────────────────────┘

步骤 2: 配置参数
┌──────────────────────┐
│  API Key: ********   │
│  模型: Balanced      │
│  场景数: 10          │
└──────────────────────┘

步骤 3: 开始生成
┌──────────────────────┐
│  [开始转换]          │
└──────────────────────┘

步骤 4: 实时预览
┌──────────────────────┐
│  进度: ████████░░ 80%│
│  当前: 生成场景 8/10 │
└──────────────────────┘

步骤 5: 查看结果
┌──────────────────────┐
│  [图片] [视频] [音频]│
└──────────────────────┘
```

---

## 📊 项目结构建议

```
comfyui-unlimitai-web/
├── src/
│   ├── components/
│   │   ├── NovelInput.tsx       # 小说输入
│   │   ├── ConfigPanel.tsx      # 参数配置
│   │   ├── ProgressMonitor.tsx  # 进度监控
│   │   ├── ResultGallery.tsx    # 结果展示
│   │   └── WorkflowViewer.tsx   # 工作流可视化(可选)
│   ├── lib/
│   │   ├── comfyui-client.ts    # API客户端
│   │   ├── workflow-manager.ts  # 工作流管理
│   │   └── websocket.ts         # WebSocket封装
│   ├── hooks/
│   │   ├── useComfyUI.ts        # ComfyUI状态管理
│   │   └── useProgress.ts       # 进度追踪
│   ├── types/
│   │   └── index.ts             # TypeScript类型
│   └── App.tsx
├── public/
│   └── workflows/               # 工作流模板
├── package.json
└── vite.config.ts
```

---

## 🔧 关键技术点

### 1. 实时进度更新

```typescript
// WebSocket 消息类型
interface ComfyUIMessage {
  type: 'status' | 'progress' | 'executing' | 'executed';
  data: {
    node?: string;
    value?: number;
    max?: number;
    output?: any;
  };
}

// 监听进度
ws.onmessage = (event) => {
  const msg: ComfyUIMessage = JSON.parse(event.data);
  
  switch (msg.type) {
    case 'progress':
      updateProgress(msg.data.value, msg.data.max);
      break;
    case 'executed':
      handleNodeComplete(msg.data);
      break;
  }
};
```

### 2. 文件上传处理

```typescript
async function uploadNovelImage(image: File) {
  const formData = new FormData();
  formData.append('image', image);
  
  const res = await axios.post(
    'http://127.0.0.1:8188/upload/image',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
  
  return res.data.name; // 返回文件名
}
```

### 3. 结果获取

```typescript
// 从 ComfyUI 获取生成结果
function getResultImage(filename: string, subfolder: string = '') {
  const params = new URLSearchParams({
    filename,
    subfolder,
    type: 'output'
  });
  
  return `http://127.0.0.1:8188/view?${params}`;
}
```

---

## 🎯 开发计划

### Phase 1: 核心功能 (1周)

```
□ 项目初始化 (Vite + React)
□ API 客户端封装
□ 基础 UI 组件
□ 工作流提交功能
□ 结果展示功能
```

### Phase 2: 进度监控 (1周)

```
□ WebSocket 集成
□ 实时进度显示
□ 日志输出
□ 错误处理
□ 队列管理
```

### Phase 3: 用户体验 (1周)

```
□ 美化 UI
□ 参数配置优化
□ 历史记录
□ 批量处理
□ 导出功能
```

### Phase 4: 高级功能 (可选)

```
□ 工作流可视化编辑
□ 自定义工作流
□ 模板管理
□ 多语言支持
□ 移动端适配
```

---

## 🚀 快速开始模板

我可以为你创建一个**前端项目模板**：

```bash
# 创建项目
npm create vite@latest comfyui-unlimitai-web -- --template react-ts

# 安装依赖
cd comfyui-unlimitai-web
npm install axios zustand tailwindcss

# 开始开发
npm run dev
```

---

## 💡 额外建议

### 1. 配置管理

```typescript
// 支持多个 ComfyUI 服务器
const servers = [
  { name: '本地', url: 'http://127.0.0.1:8188' },
  { name: '远程', url: 'http://192.168.1.100:8188' }
];
```

### 2. 离线支持

```typescript
// Service Worker 缓存结果
// 本地存储工作流历史
```

### 3. 性能优化

```typescript
// 虚拟列表展示大量结果
// 懒加载图片/视频
// 请求去重
```

---

## 🎊 总结

### ✅ 完全可行！

**优势**:
- ✅ 不需要修改现有插件
- ✅ 面向普通用户
- ✅ 更简洁的操作流程
- ✅ 独立产品形态

**开发时间**:
- 基础版本: 2周
- 完整版本: 3-4周

**技术难度**: 中等
- 需要前端开发经验
- API 集成相对简单

---

**需要我帮你创建前端项目模板吗？我可以立即开始！** 🚀
