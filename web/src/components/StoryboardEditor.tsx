import { useState } from 'react';
import { Plus, Film, ChevronUp, ChevronDown, Trash2, Play } from 'lucide-react';
import { chatWithAI } from '@/lib/ai-assistant-api';
import { getUnifiedConfig, hasApiKey } from '@/lib/unified-config';

export function StoryboardEditor({ novelText, onStoryboardChange, onStartGeneration }: any) {
  const [shots, setShots] = useState<any[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const moveShot = (id: string, dir: -1 | 1) => {
    const idx = shots.findIndex(s => s.id === id);
    const newIdx = idx + dir;
    if (newIdx < 0 || newIdx >= shots.length) return;
    const updated = [...shots];
    [updated[idx], updated[newIdx]] = [updated[newIdx], updated[idx]];
    const renumbered = updated.map((s, i) => ({ ...s, shotNumber: i + 1 }));
    setShots(renumbered);
    onStoryboardChange?.(renumbered);
  };

  const addShot = () => {
    const newShot = {
      id: crypto.randomUUID(),
      shotNumber: shots.length + 1,
      shotSize: 'medium',
      cameraMove: 'static',
      duration: 5,
      description: '',
      prompt: '',
      notes: ''
    };
    const updated = [...shots, newShot];
    setShots(updated);
    onStoryboardChange?.(updated);
  };

  const updateShot = (id: string, updates: any) => {
    const updated = shots.map(s => s.id === id ? { ...s, ...updates } : s);
    setShots(updated);
    onStoryboardChange?.(updated);
  };

  const deleteShot = (id: string) => {
    const updated = shots.filter(s => s.id !== id).map((s, i) => ({ ...s, shotNumber: i + 1 }));
    setShots(updated);
    onStoryboardChange?.(updated);
  };

  const generateStoryboard = async () => {
    if (!novelText || novelText.length < 50) {
      alert('请先输入至少50字的小说文本');
      return;
    }
    if (!hasApiKey()) {
      alert('请先配置API Key');
      return;
    }
    
    setIsGenerating(true);
    try {
      const config = getUnifiedConfig();
      const prompt = `生成分镜脚本：${novelText}`;
      const response = await chatWithAI(prompt, config.apiKey!, { novelText }, 'deepseek-chat');
      const jsonMatch = response.content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        let data;
        try {
          data = JSON.parse(jsonMatch[0]);
        } catch {
          alert('AI 返回了无效的格式，请重试');
          return;
        }
        const newShots = data.shots.map((shot: any, idx: number) => ({
          id: crypto.randomUUID() + idx,
          shotNumber: idx + 1,
          ...shot
        }));
        setShots(newShots);
        onStoryboardChange?.(newShots);
      }
    } catch (error) {
      alert('生成失败');
    } finally {
      setIsGenerating(false);
    }
  };

  const totalDuration = shots.reduce((sum, s) => sum + s.duration, 0);

  return (
    <div className="h-full flex flex-col bg-[var(--bg-primary)]">
      {/* Header */}
      <div className="px-6 py-4 border-b border-[var(--border-subtle)]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Film className="w-5 h-5 text-[var(--text-secondary)]" />
            <h2 className="text-base font-semibold">分镜编辑器</h2>
            {shots.length > 0 && (
              <span className="text-xs text-[var(--text-tertiary)] ml-2">
                {shots.length} 镜头 · {totalDuration}秒
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={generateStoryboard}
              disabled={isGenerating || !novelText}
              className="px-4 h-8 border border-[var(--border-default)] rounded-lg text-sm hover:bg-[var(--bg-hover)] disabled:opacity-50 transition-all"
            >
              {isGenerating ? '生成中...' : 'AI生成'}
            </button>
            
            {shots.length > 0 && (
              <button
                onClick={() => setShowConfirm(true)}
                className="px-4 h-8 border border-[var(--text-tertiary)] rounded-lg text-sm hover:bg-[var(--bg-hover)] transition-all flex items-center gap-1.5"
              >
                <Play className="w-3.5 h-3.5" />
                开始生成
              </button>
            )}
          </div>
        </div>
      </div>
      
      {/* Toolbar */}
      <div className="px-6 py-3 border-b border-[var(--border-subtle)]">
        <button
          onClick={addShot}
          className="flex items-center gap-2 px-3 h-8 border border-[var(--border-default)] rounded-lg text-sm hover:bg-[var(--bg-hover)] transition-all"
        >
          <Plus className="w-3.5 h-3.5" />
          添加镜头
        </button>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {shots.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 border border-[var(--border-default)] rounded-lg flex items-center justify-center mb-3">
              <Film className="w-6 h-6 text-[var(--text-tertiary)]" />
            </div>
            <p className="text-sm text-[var(--text-secondary)] mb-1">还没有分镜</p>
            <p className="text-xs text-[var(--text-tertiary)]">点击"AI生成"或手动添加</p>
          </div>
        ) : (
          <div className="space-y-3">
            {shots.map((shot) => (
              <div key={shot.id} className="border border-[var(--border-subtle)] rounded-lg p-4 hover:border-[var(--text-tertiary)] transition-all">
                <div className="flex items-start gap-4">
                  <div className="flex flex-col items-center gap-1">
                    <div className="w-10 h-10 border border-[var(--border-default)] rounded flex items-center justify-center">
                      <span className="text-sm font-medium">{shot.shotNumber}</span>
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <button onClick={() => moveShot(shot.id, -1)} className="p-1 hover:bg-[var(--bg-hover)] rounded">
                        <ChevronUp className="w-3 h-3 text-[var(--text-tertiary)]" />
                      </button>
                      <button onClick={() => moveShot(shot.id, 1)} className="p-1 hover:bg-[var(--bg-hover)] rounded">
                        <ChevronDown className="w-3 h-3 text-[var(--text-tertiary)]" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex-1 space-y-3">
                    <div className="grid grid-cols-3 gap-2">
                      <select 
                        value={shot.shotSize} 
                        onChange={(e) => updateShot(shot.id, { shotSize: e.target.value })}
                        className="h-8 px-2 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded text-xs"
                      >
                        <option value="medium">中景</option>
                        <option value="close">近景</option>
                        <option value="long">远景</option>
                      </select>
                      
                      <select 
                        value={shot.cameraMove} 
                        onChange={(e) => updateShot(shot.id, { cameraMove: e.target.value })}
                        className="h-8 px-2 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded text-xs"
                      >
                        <option value="static">固定</option>
                        <option value="pan">摇镜</option>
                        <option value="zoom">变焦</option>
                      </select>
                      
                      <input 
                        type="number" 
                        value={shot.duration} 
                        onChange={(e) => updateShot(shot.id, { duration: Number(e.target.value) })}
                        className="h-8 px-2 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded text-xs" 
                        placeholder="秒"
                      />
                    </div>
                    
                    <textarea 
                      value={shot.description} 
                      onChange={(e) => updateShot(shot.id, { description: e.target.value })}
                      placeholder="画面描述..." 
                      className="w-full h-16 px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded text-xs resize-none"
                    />
                    
                    <input 
                      value={shot.prompt} 
                      onChange={(e) => updateShot(shot.id, { prompt: e.target.value })}
                      placeholder="生成提示词（英文）..." 
                      className="w-full h-8 px-3 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded text-xs"
                    />
                  </div>
                  
                  <button 
                    onClick={() => deleteShot(shot.id)} 
                    className="p-2 hover:bg-[var(--bg-hover)] rounded"
                  >
                    <Trash2 className="w-4 h-4 text-[var(--text-tertiary)]" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Confirm Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setShowConfirm(false)}>
          <div className="bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg p-6 max-w-sm w-[90vw]" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-base font-semibold mb-4">确认生成视频？</h3>
            <div className="space-y-2 mb-4 text-sm">
              <div className="flex justify-between">
                <span className="text-[var(--text-tertiary)]">镜头数量</span>
                <span>{shots.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-tertiary)]">总时长</span>
                <span>{totalDuration}秒</span>
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => setShowConfirm(false)} className="flex-1 h-9 border border-[var(--border-default)] rounded-lg text-sm hover:bg-[var(--bg-hover)]">
                取消
              </button>
              <button 
                onClick={() => { setShowConfirm(false); onStartGeneration?.(shots); }} 
                className="flex-1 h-9 border border-[var(--text-tertiary)] rounded-lg text-sm hover:bg-[var(--bg-hover)]"
              >
                确认
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
