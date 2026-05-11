import { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, Sparkles, Trash2, Loader2, AlertCircle } from 'lucide-react';
import { chatWithAI } from '@/lib/ai-assistant-api';
import { getUnifiedConfig as getConfig, hasApiKey } from '@/lib/unified-config';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface CreativeAssistantProps {
  novelText?: string;
  storyboard?: any;
  currentPrompt?: string;
}

export function CreativeAssistant({ novelText, storyboard, currentPrompt }: CreativeAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '你好！我是你的AI创作助手。我可以帮助你：\n\n• 优化小说描述，使其更适合转化为视频\n• 提供分镜建议和镜头设计\n• 优化图像生成提示词\n• 回答创作相关的问题\n• 提供风格和创意建议\n\n有什么我可以帮助你的吗？',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    if (!hasApiKey()) {
      const noKeyMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '⚠️ 请先在右上角"设置"中配置API Key，才能使用AI助手功能。',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, noKeyMessage]);
      return;
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const config = getConfig();

      if (!config.apiKey) {
        throw new Error('API Key未配置');
      }

      const response = await chatWithAI(
        input,
        config.apiKey,
        { novelText, storyboard },
        'deepseek-chat'
      );

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.content + `\n\n_成本: $${response.cost.toFixed(6)}_`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('AI Assistant Error:', error);
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `抱歉，我遇到了一些问题：${error instanceof Error ? error.message : '未知错误'}\n\n请检查：\n1. API Key是否正确配置\n2. 网络连接是否正常\n3. API额度是否充足`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([{
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '对话已清空。有什么我可以帮助你的吗？',
      timestamp: new Date()
    }]);
  };

  const quickActions = [
    { label: '优化提示词', query: '如何优化图像生成提示词？' },
    { label: '分镜建议', query: '给我一些分镜和镜头设计建议' },
    { label: '小说优化', query: '如何优化小说文本使其更适合转视频？' },
    { label: '风格推荐', query: '推荐适合我的创作风格' },
  ];

  return (
    <div className="bg-[var(--bg-elevated)] rounded-lg shadow-md flex flex-col h-[600px]">
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-[var(--accent-primary)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">AI创作助手</h2>
          {!hasApiKey() && (
            <AlertCircle className="w-4 h-4 text-yellow-500" />
          )}
        </div>
        <button
          onClick={handleClear}
          className="p-2 hover:bg-[var(--bg-tertiary)] rounded-lg text-[var(--text-tertiary)]"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="p-3 border-b bg-[var(--bg-tertiary)]">
        <p className="text-xs text-[var(--text-tertiary)] mb-2">快捷问题：</p>
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => setInput(action.query)}
              className="text-xs px-3 py-1.5 bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded-full hover:border-[var(--accent-primary)] hover:border-opacity-50 hover:bg-[var(--accent-primary)] hover:bg-opacity-5"
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-[var(--accent-primary)] text-white'
                  : 'bg-[var(--bg-tertiary)] text-[var(--text-primary)]'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-[var(--accent-primary)]" />
                  <span className="text-xs font-medium text-[var(--accent-primary)]">AI助手</span>
                </div>
              )}
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              <div className={`text-xs mt-2 ${
                message.role === 'user' ? 'text-white text-opacity-70' : 'text-[var(--text-tertiary)]'
              }`}>
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-[var(--bg-tertiary)] rounded-lg p-3">
              <div className="flex items-center gap-2 text-[var(--text-tertiary)]">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">正在思考...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="问我任何关于创作的问题..."
            className="flex-1 px-4 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-[var(--accent-primary)]"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-[var(--accent-primary)] hover:opacity-90 text-white rounded-lg disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
