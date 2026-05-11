import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Film, Layers, Zap, DollarSign } from 'lucide-react';
import { chatWithAI } from '@/lib/ai-assistant-api';
import { getUnifiedConfig, hasApiKey } from '@/lib/unified-config';

export function ProfessionalAssistant({ novelText }: { novelText?: string }) {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const tools = [
    { icon: <Film className="w-4 h-4" />, label: '剧本分析', action: () => analyze('script') },
    { icon: <Layers className="w-4 h-4" />, label: '分镜设计', action: () => analyze('storyboard') },
    { icon: <Zap className="w-4 h-4" />, label: '参数优化', action: () => analyze('technical') },
    { icon: <DollarSign className="w-4 h-4" />, label: '成本预算', action: () => analyze('cost') }
  ];

  const analyze = async (type: string) => {
    if (!novelText || novelText.length < 50) {
      alert('请先输入至少50字的小说文本');
      return;
    }
    if (!hasApiKey()) {
      alert('请先配置API Key');
      return;
    }
    
    setIsLoading(true);
    try {
      const config = getUnifiedConfig();
      const prompt = `作为专业AI创作顾问，请为以下小说提供${type}分析：\n\n${novelText}`;
      const response = await chatWithAI(prompt, config.apiKey!, { novelText }, 'deepseek-chat');
      setMessages(prev => [...prev, { role: 'assistant', content: response.content, time: new Date() }]);
    } catch (error) {
      alert('分析失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    if (!hasApiKey()) {
      alert('请先配置API Key');
      return;
    }
    
    const userMessage = { role: 'user', content: input, time: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      const config = getUnifiedConfig();
      const response = await chatWithAI(input, config.apiKey!, { novelText }, 'deepseek-chat');
      setMessages(prev => [...prev, { role: 'assistant', content: response.content, time: new Date() }]);
    } catch (error) {
      alert('发送失败');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[var(--bg-primary)]">
      {/* Header */}
      <div className="px-6 py-4 border-b border-[var(--border-subtle)]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[var(--text-secondary)]" />
            <h2 className="text-base font-semibold">AI 创作助手</h2>
          </div>
          <span className="text-xs text-[var(--text-tertiary)]">专业分析工具</span>
        </div>
        
        <div className="grid grid-cols-4 gap-2">
          {tools.map((tool, i) => (
            <button
              key={i}
              onClick={tool.action}
              disabled={isLoading}
              className="flex flex-col items-center gap-1.5 px-3 py-2 rounded-lg border border-[var(--border-subtle)] hover:border-[var(--text-tertiary)] hover:bg-[var(--bg-hover)] transition-all disabled:opacity-50"
            >
              <span className="text-[var(--text-secondary)]">{tool.icon}</span>
              <span className="text-xs text-[var(--text-tertiary)]">{tool.label}</span>
            </button>
          ))}
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 border border-[var(--border-default)] rounded-lg flex items-center justify-center mb-3">
              <Sparkles className="w-6 h-6 text-[var(--text-tertiary)]" />
            </div>
            <p className="text-sm text-[var(--text-secondary)] mb-1">AI助手已就绪</p>
            <p className="text-xs text-[var(--text-tertiary)]">点击上方工具开始分析</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                <div className={`inline-block max-w-[80%] px-4 py-3 rounded-lg ${
                  msg.role === 'user' 
                    ? 'bg-[var(--bg-tertiary)] text-[var(--text-primary)]' 
                    : 'bg-[var(--bg-secondary)] border border-[var(--border-subtle)] text-[var(--text-primary)]'
                }`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="text-left">
                <div className="inline-block px-4 py-3 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-lg">
                  <p className="text-sm text-[var(--text-tertiary)]">分析中...</p>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input */}
      <div className="p-4 border-t border-[var(--border-subtle)]">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="输入问题..."
            className="flex-1 h-10 px-4 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg text-sm focus:outline-none focus:border-[var(--text-tertiary)] text-[var(--text-primary)]"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="w-10 h-10 flex items-center justify-center border border-[var(--border-default)] rounded-lg hover:bg-[var(--bg-hover)] disabled:opacity-50 transition-all"
          >
            <Send className="w-4 h-4 text-[var(--text-secondary)]" />
          </button>
        </div>
      </div>
    </div>
  );
}
