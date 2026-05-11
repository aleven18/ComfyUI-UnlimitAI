/**
 * AI助手API客户端
 */

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ChatResponse {
  content: string;
  model: string;
  inputTokens: number;
  outputTokens: number;
  cost: number;
}

import { getUnifiedConfig } from './unified-config';
const API_BASE_URL = () => getUnifiedConfig().apiBaseUrl;

// 默认使用DeepSeek Chat（推荐）
const DEFAULT_MODEL = 'deepseek-chat';

// 系统提示词
const SYSTEM_PROMPT = `你是一个专业的AI创作助手，精通：

1. 📝 小说创作和文本优化
2. 🎬 电影分镜和镜头设计  
3. 🎨 图像生成提示词优化
4. 🎵 音频和音乐建议
5. 💰 成本优化策略

你的职责是帮助用户优化创作，提供专业建议。

回答要求：
- 专业但易懂
- 简洁明了  
- 提供具体建议
- 可以举例说明`;

/**
 * 发起AI对话
 */
export async function chatWithAI(
  message: string,
  apiKey: string,
  context?: {
    novelText?: string;
    storyboard?: any;
  },
  model: string = DEFAULT_MODEL,
  customSystemPrompt?: string,
  conversationHistory?: ChatMessage[]
): Promise<ChatResponse> {
  // 构建消息
  const messages: ChatMessage[] = [
    {
      role: 'system',
      content: (customSystemPrompt || SYSTEM_PROMPT) + buildContext(context)
    }
  ];
  
  // 添加对话历史
  if (conversationHistory && conversationHistory.length > 0) {
    messages.push(...conversationHistory);
  }
  
  // 添加当前用户消息
  messages.push({
    role: 'user',
    content: message
  });
  
  // 调用API
  const response = await fetch(`${API_BASE_URL()}/v1/chat/completions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: model,
      messages: messages,
      temperature: 0.7,
      max_tokens: 2000
    })
  });
  
  if (!response.ok) {
    throw new Error(`API错误: ${response.status}`);
  }
  
  const data = await response.json();
  
  const usage = data.usage || {};
  const content = data.choices?.[0]?.message?.content ?? '';
  const inputTokens = usage.prompt_tokens ?? 0;
  const outputTokens = usage.completion_tokens ?? 0;
  
  const cost = 
    inputTokens * 0.00000014 +
    outputTokens * 0.00000028;
  
  return {
    content,
    model: model,
    inputTokens,
    outputTokens,
    cost
  };
}

/**
 * 构建上下文信息
 */
function buildContext(context?: any): string {
  if (!context) return '';
  
  let parts = '\n\n【当前项目信息】';
  
  if (context.novelText) {
    parts += `\n小说文本：已提供（${context.novelText.length}字）`;
  }
  
  if (context.storyboard) {
    parts += '\n分镜信息：已生成';
  }
  
  return parts;
}

/**
 * 快捷功能：优化提示词
 */
export async function optimizePrompt(
  originalPrompt: string,
  apiKey: string
): Promise<string> {
  const response = await chatWithAI(
    `请优化以下图像生成提示词：\n\n${originalPrompt}\n\n请给出优化后的英文提示词和优化要点。`,
    apiKey
  );
  return response.content;
}

/**
 * 快捷功能：分镜建议
 */
export async function suggestStoryboard(
  sceneDescription: string,
  apiKey: string
): Promise<string> {
  const response = await chatWithAI(
    `请为以下场景提供分镜建议：\n\n${sceneDescription}\n\n请给出镜头设计、景别、运镜和时长建议。`,
    apiKey
  );
  return response.content;
}
