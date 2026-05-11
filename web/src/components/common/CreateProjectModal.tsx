/**
 * 创建项目对话框
 * 
 * 简洁优雅的设计，支持：
 * - 项目名称输入
 * - 项目描述（可选）
 * - 项目类型选择
 */

import { useState } from 'react';
import { X, Film, Sparkles, Heart, Zap, BookOpen } from 'lucide-react';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (data: { name: string; description?: string; genre?: string }) => void;
}

const genres = [
  { 
    id: 'drama', 
    label: '剧情', 
    icon: <Film className="w-4 h-4" />,
    description: '适合叙事性强的故事，注重情节发展'
  },
  { 
    id: 'romance', 
    label: '爱情', 
    icon: <Heart className="w-4 h-4" />,
    description: '注重情感表达，温馨浪漫的氛围'
  },
  { 
    id: 'comedy', 
    label: '喜剧', 
    icon: <Sparkles className="w-4 h-4" />,
    description: '轻松幽默的风格，明快的节奏'
  },
  { 
    id: 'action', 
    label: '动作', 
    icon: <Zap className="w-4 h-4" />,
    description: '激烈的冲突场面，快节奏剪辑'
  },
  { 
    id: 'literary', 
    label: '文艺', 
    icon: <BookOpen className="w-4 h-4" />,
    description: '艺术性表达，注重意境营造'
  },
];

export function CreateProjectModal({ isOpen, onClose, onCreate }: CreateProjectModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('drama');
  
  if (!isOpen) return null;
  
  const handleCreate = () => {
    if (!name.trim()) return;
    
    onCreate({
      name: name.trim(),
      description: description.trim() || undefined,
      genre: selectedGenre
    });
    
    // 重置表单
    setName('');
    setDescription('');
    setSelectedGenre('drama');
    onClose();
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && name.trim()) {
      handleCreate();
    }
    if (e.key === 'Escape') {
      onClose();
    }
  };
  
  return (
    <>
      {/* 背景遮罩 */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 animate-fade-in"
        onClick={onClose}
      />
      
      {/* 对话框 */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div 
          className="bg-[var(--bg-primary)] rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-scale-in"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 头部 */}
          <div className="relative px-6 py-5 border-b border-[var(--border-subtle)]">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">新建项目</h2>
            <p className="text-sm text-[var(--text-tertiary)] mt-1">创建一个新的创作项目</p>
            
            <button
              onClick={onClose}
              className="absolute top-5 right-6 p-1.5 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
            >
              <X className="w-5 h-5 text-[var(--text-tertiary)]" />
            </button>
          </div>
          
          {/* 内容 */}
          <div className="px-6 py-5 space-y-5">
            {/* 项目名称 */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                项目名称 <span className="text-[var(--accent-error)]">*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="例如：星际迷途"
                className="w-full h-11 px-4 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                autoFocus
              />
            </div>
            
            {/* 项目描述 */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                项目描述 <span className="text-[var(--text-tertiary)] text-xs">（可选）</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="简短描述这个项目..."
                rows={3}
                className="w-full px-4 py-3 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
              />
            </div>
            
            {/* 项目类型 */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                项目类型
              </label>
              <div className="grid grid-cols-5 gap-2 mb-2">
                {genres.map((genre) => (
                  <button
                    key={genre.id}
                    onClick={() => setSelectedGenre(genre.id)}
                    className={`
                      flex flex-col items-center justify-center py-3 rounded-lg border transition-all
                      ${selectedGenre === genre.id
                        ? 'bg-[var(--accent-primary)] border-[var(--accent-primary)] text-white'
                        : 'bg-[var(--bg-secondary)] border-[var(--border-default)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:border-[var(--accent-primary)]/50'
                      }
                    `}
                  >
                    {genre.icon}
                    <span className="text-xs mt-1.5 font-medium">{genre.label}</span>
                  </button>
                ))}
              </div>
              
              {/* 类型说明 */}
              <div className="text-xs text-[var(--text-tertiary)] p-3 bg-[var(--bg-secondary)] rounded-lg">
                <p className="font-medium mb-1">
                  {genres.find(g => g.id === selectedGenre)?.label}：
                </p>
                <p>{genres.find(g => g.id === selectedGenre)?.description}</p>
              </div>
            </div>
          </div>
          
          {/* 底部按钮 */}
          <div className="px-6 py-4 bg-[var(--bg-secondary)] flex items-center justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
            >
              取消
            </button>
            <button
              onClick={handleCreate}
              disabled={!name.trim()}
              className="px-6 py-2 bg-[var(--accent-primary)] text-white text-sm font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              创建项目
            </button>
          </div>
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
