/**
 * AI对话式角色创建助手
 * 
 * 通过自然对话引导用户创建角色卡
 * 更友好、更互动的体验
 */

import { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2, User, Sparkles } from 'lucide-react';
import { chatWithAI } from '@/lib/ai-assistant-api';
import { getUnifiedConfig as getConfig, hasApiKey } from '@/lib/unified-config';

interface Message {
  id: string;
  role: 'assistant' | 'user';
  content: string;
  timestamp: Date;
}

interface AIGuideCharacterCreationProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (characterData: any) => void;
}

export function AIGuideCharacterCreation({ isOpen, onClose, onCreate }: AIGuideCharacterCreationProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '你好！我是AI角色创作助手。\n\n我会通过对话的方式帮助你创建角色卡。让我们开始吧！\n\n首先，这个角色叫什么名字？',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [collectedInfo, setCollectedInfo] = useState<any>({});
  const [isComplete, setIsComplete] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  if (!isOpen) return null;
  
  const handleSend = async () => {
    if (!input.trim() || isGenerating) return;
    
    if (!hasApiKey()) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '⚠️ 请先在右上角"设置"中配置API Key，才能使用AI助手功能。',
        timestamp: new Date()
      };
      setMessages([...messages, errorMessage]);
      return;
    }
    
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };
    
    setMessages([...messages, userMessage]);
    setInput('');
    setIsGenerating(true);
    
    try {
      const config = getConfig();
      const conversationHistory = messages.map(m => ({
        role: m.role,
        content: m.content
      }));
      
      const systemPrompt = `你是一个专业的角色创作助手，正在通过对话帮助用户创建角色卡。

当前已收集的信息：
${JSON.stringify(collectedInfo, null, 2)}

你需要引导用户提供以下信息（按优先级）：
1. 角色名称 ✓（必须）
2. 角色定位 ✓（主角/配角/反派/路人，必须）
3. 外貌描述 ✓（详细的体貌特征，用于图像生成，必须）
4. 性别和年龄
5. 性格特点
6. 背景故事
7. 特殊能力或特征

规则：
- 每次只问一个问题，等待用户回答
- 用自然、友好的语气对话
- 根据用户的回答提取关键信息
- 外貌描述要具体，包括：发型发色、眼睛、身高体型、穿着等
- 如果用户回答中包含有用信息，提取并记录
- 当收集完姓名、定位、外貌后，可以询问是否还有其他要补充的
- 最后总结角色信息，说"角色信息收集完成！"
- 回复要简洁，不要超过3句话

回复格式：
如果收集到信息，在最后用JSON格式标注：
[INFO]{"key": "value"}[/INFO]

关键字段名：
- name: 角色名称
- role: 角色定位（主角/配角/反派/路人）
- appearance: 外貌描述（完整的外貌特征描述）
- gender: 性别（男/女）
- age: 年龄
- personality: 性格特点
- background: 背景故事

例如：
用户：他叫李明，是个高中生，主角
助手：好的，李明是个高中生主角。能描述一下他的外貌吗？
[INFO]{"name": "李明", "role": "主角"}[/INFO]

用户：短发，黑发，有点瘦，戴着眼镜
助手：明白了，短发黑发、偏瘦、戴眼镜的李明。他的性格怎么样？
[INFO]{"appearance": "短发黑发，偏瘦，戴眼镜"}[/INFO]`;

      const response = await chatWithAI(
        input.trim(),
        config.apiKey!,
        undefined,
        'deepseek-chat',
        systemPrompt,
        conversationHistory  // 传递对话历史
      );
      
      let assistantContent = response.content;
      let newCollectedInfo = { ...collectedInfo };
      
      // 提取收集到的信息
      const infoMatch = assistantContent.match(/\[INFO\](\{[\s\S]*?\})\[\/INFO\]/);
      if (infoMatch) {
        try {
          const info = JSON.parse(infoMatch[1]);
          newCollectedInfo = { ...newCollectedInfo, ...info };
          setCollectedInfo(newCollectedInfo);
          assistantContent = assistantContent.replace(/\[INFO\].*\[\/INFO\]/g, '').trim();
        } catch (e) {
          // JSON解析失败，忽略
        }
      }
      
      // 检查是否完成（必须有姓名、定位、外貌）
      const hasName = !!newCollectedInfo.name;
      const hasRole = !!newCollectedInfo.role;
      const hasAppearance = !!newCollectedInfo.appearance;
      
      if (hasName && hasRole && hasAppearance) {
        setIsComplete(true);
        
        // 添加总结信息
        assistantContent += '\n\n---\n\n**角色信息总结：**\n';
        if (newCollectedInfo.name) assistantContent += `- 名字：${newCollectedInfo.name}\n`;
        if (newCollectedInfo.role) assistantContent += `- 定位：${newCollectedInfo.role}\n`;
        if (newCollectedInfo.gender) assistantContent += `- 性别：${newCollectedInfo.gender}\n`;
        if (newCollectedInfo.age) assistantContent += `- 年龄：${newCollectedInfo.age}\n`;
        if (newCollectedInfo.appearance) assistantContent += `- 外貌：${newCollectedInfo.appearance}\n`;
        if (newCollectedInfo.personality) assistantContent += `- 性格：${newCollectedInfo.personality}\n`;
        if (newCollectedInfo.background) assistantContent += `- 背景：${newCollectedInfo.background}\n`;
      }
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (error: any) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `抱歉，我遇到了一些问题：${error.message}\n\n请重试或手动创建角色卡。`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsGenerating(false);
    }
  };
  
  const handleCreateCharacter = () => {
    const characterData = {
      name: collectedInfo.name || '未命名角色',
      role: collectedInfo.role === '主角' ? 'protagonist' : 
            collectedInfo.role === '配角' ? 'supporting' : 
            collectedInfo.role === '反派' ? 'antagonist' : 'minor',
      appearance: {
        referenceImage: '',
        description: collectedInfo.appearance || '',
        gender: collectedInfo.gender === '男' ? 'male' : 
                collectedInfo.gender === '女' ? 'female' : 'other',
        age: parseInt(collectedInfo.age) || 25,
        ageRange: 'young_adult'
      },
      voice: {
        engine: 'minimax',
        voiceId: '',
        voiceStyle: '',
        speechRate: 1.0,
        pitch: 1.0,
        personality: []
      },
      personality: {
        traits: collectedInfo.personality ? collectedInfo.personality.split(/[,，、]/) : [],
        background: collectedInfo.background || '',
        motivation: '',
        relationships: []
      },
      consistency: {
        seed: 0,
        style: 'realistic',
        tags: []
      },
      usage: {
        scenes: [],
        totalDialogueLines: 0,
        totalDuration: 0
      }
    };
    
    onCreate(characterData);
    
    // 重置状态
    setMessages([{
      id: '1',
      role: 'assistant',
      content: '你好！我是AI角色创作助手。\n\n我会通过对话的方式帮助你创建角色卡。让我们开始吧！\n\n首先，这个角色叫什么名字？',
      timestamp: new Date()
    }]);
    setCollectedInfo({});
    setIsComplete(false);
    onClose();
  };
  
  const handleReset = () => {
    setMessages([{
      id: '1',
      role: 'assistant',
      content: '你好！我是AI角色创作助手。\n\n我会通过对话的方式帮助你创建角色卡。让我们开始吧！\n\n首先，这个角色叫什么名字？',
      timestamp: new Date()
    }]);
    setCollectedInfo({});
    setIsComplete(false);
  };
  
  return (
    <>
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 animate-fade-in"
        onClick={onClose}
      />
      
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div 
          className="bg-[var(--bg-primary)] rounded-2xl shadow-2xl w-full max-w-2xl h-[80vh] overflow-hidden flex flex-col animate-scale-in"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 头部 */}
          <div className="relative px-6 py-5 border-b border-[var(--border-subtle)]">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[var(--accent-primary)]" />
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">AI角色创作助手</h2>
            </div>
            <p className="text-sm text-[var(--text-tertiary)] mt-1">
              通过对话引导创建角色卡
            </p>
            
            <button
              onClick={onClose}
              className="absolute top-5 right-6 p-1.5 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
            >
              <X className="w-5 h-5 text-[var(--text-tertiary)]" />
            </button>
          </div>
          
          {/* 对话区域 */}
          <div className="flex-1 flex overflow-hidden">
            {/* 信息收集状态 */}
            <div className="w-64 border-r border-[var(--border-subtle)] p-4 overflow-y-auto bg-[var(--bg-secondary)]">
              <h3 className="text-sm font-semibold mb-4">信息收集进度</h3>
              <div className="space-y-3">
                <InfoItem label="姓名" value={collectedInfo.name} required />
                <InfoItem label="定位" value={collectedInfo.role} required />
                <InfoItem label="外貌" value={collectedInfo.appearance} required />
                <InfoItem label="性别" value={collectedInfo.gender} />
                <InfoItem label="年龄" value={collectedInfo.age} />
                <InfoItem label="性格" value={collectedInfo.personality} />
                <InfoItem label="背景" value={collectedInfo.background} />
              </div>
            </div>
            
            {/* 对话内容 */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
                  ${message.role === 'user' 
                    ? 'bg-[var(--accent-primary)]' 
                    : 'bg-[var(--bg-tertiary)]'
                  }
                `}>
                  {message.role === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Sparkles className="w-4 h-4 text-[var(--accent-primary)]" />
                  )}
                </div>
                
                <div className={`
                  max-w-[70%] px-4 py-3 rounded-2xl whitespace-pre-wrap
                  ${message.role === 'user'
                    ? 'bg-[var(--accent-primary)] text-white'
                    : 'bg-[var(--bg-secondary)] text-[var(--text-primary)]'
                  }
                `}>
                  <p className="text-sm leading-relaxed">{message.content}</p>
                </div>
              </div>
            ))}
            
            {isGenerating && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-[var(--bg-tertiary)] flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-[var(--accent-primary)]" />
                </div>
                <div className="px-4 py-3 bg-[var(--bg-secondary)] rounded-2xl">
                  <Loader2 className="w-4 h-4 animate-spin text-[var(--accent-primary)]" />
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
            </div>
          </div>
          
          {/* 完成提示 */}
          {isComplete && (
            <div className="px-6 py-4 bg-[var(--bg-secondary)] border-t border-[var(--border-subtle)]">
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <p className="text-sm font-medium text-[var(--text-primary)]">角色信息已收集完成</p>
                  <p className="text-xs text-[var(--text-tertiary)] mt-1">点击创建角色卡，或继续补充细节</p>
                </div>
                <button
                  onClick={handleReset}
                  className="px-4 py-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                >
                  重新开始
                </button>
                <button
                  onClick={handleCreateCharacter}
                  className="px-6 py-2 bg-[var(--accent-primary)] text-white text-sm font-medium rounded-lg hover:opacity-90 transition-all"
                >
                  创建角色卡
                </button>
              </div>
            </div>
          )}
          
          {/* 输入区域 */}
          {!isComplete && (
            <div className="px-6 py-4 bg-[var(--bg-secondary)] border-t border-[var(--border-subtle)]">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                  placeholder="输入你的回答..."
                  className="flex-1 h-10 px-4 bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                  disabled={isGenerating}
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isGenerating}
                  className="px-4 py-2 bg-[var(--accent-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes scale-in {
          from { 
            opacity: 0;
            transform: scale(0.95) translateY(-10px);
          }
          to { 
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
        
        .animate-fade-in {
          animation: fade-in 0.2s ease-out;
        }
        
        .animate-scale-in {
          animation: scale-in 0.3s ease-out;
        }
      `}</style>
    </>
  );
}

function InfoItem({ label, value, required }: { label: string; value?: string; required?: boolean }) {
  const hasValue = !!value;
  
  return (
    <div className="flex items-start gap-2">
      <div className={`
        w-2 h-2 rounded-full mt-1.5 flex-shrink-0
        ${hasValue ? 'bg-[var(--success)]' : required ? 'bg-[var(--warning)]' : 'bg-[var(--border-default)]'}
      `} />
      <div className="flex-1 min-w-0">
        <p className="text-xs text-[var(--text-tertiary)] mb-0.5">
          {label}
          {required && <span className="text-[var(--accent-error)] ml-1">*</span>}
        </p>
        {hasValue && (
          <p className="text-xs text-[var(--text-primary)] line-clamp-2">{value}</p>
        )}
      </div>
    </div>
  );
}
