import { useState } from 'react';
import { Plus, Film, ChevronUp, ChevronDown, Trash2, Play } from 'lucide-react';
import { Shot } from '@/types/project';

interface StoryboardEditorProps {
  novelText: string;
  shots: Shot[];
  onShotsChange: (shots: Shot[]) => void;
  onStartGeneration: (shots: Shot[]) => void;
}

const SHOT_SIZES = [
  { value: 'extreme-long', label: '大远景' },
  { value: 'long', label: '远景' },
  { value: 'full', label: '全景' },
  { value: 'medium', label: '中景' },
  { value: 'medium-close', label: '近景' },
  { value: 'close', label: '特写' },
  { value: 'extreme-close', label: '大特写' },
];

const CAMERA_MOVES = [
  { value: 'static', label: '固定' },
  { value: 'pan', label: '摇镜' },
  { value: 'tilt', label: '俯仰' },
  { value: 'dolly', label: '推拉' },
  { value: 'zoom', label: '变焦' },
  { value: 'tracking', label: '跟拍' },
  { value: 'crane', label: '升降' },
];

export function StoryboardEditor({ novelText, shots, onShotsChange, onStartGeneration }: StoryboardEditorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const moveShot = (id: string, dir: -1 | 1) => {
    const idx = shots.findIndex(s => s.id === id);
    const newIdx = idx + dir;
    if (newIdx < 0 || newIdx >= shots.length) return;
    const updated = [...shots];
    [updated[idx], updated[newIdx]] = [updated[newIdx], updated[idx]];
    const renumbered = updated.map((s, i) => ({ ...s, shotNumber: i + 1 }));
    onShotsChange(renumbered);
  };

  const addShot = () => {
    const newShot: Shot = {
      id: crypto.randomUUID(),
      shotNumber: shots.length + 1,
      shotSize: 'medium',
      cameraMove: 'static',
      duration: 5,
      description: '',
      prompt: '',
      notes: '',
      characters: [],
    };
    onShotsChange([...shots, newShot]);
  };

  const updateShot = (id: string, updates: Partial<Shot>) => {
    onShotsChange(shots.map(s => s.id === id ? { ...s, ...updates } : s));
  };

  const deleteShot = (id: string) => {
    onShotsChange(shots.filter(s => s.id !== id).map((s, i) => ({ ...s, shotNumber: i + 1 })));
  };

  const totalDuration = shots.reduce((sum, s) => sum + s.duration, 0);

  return (
    <div className="h-full flex flex-col bg-[var(--bg-primary)]">
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
              onClick={addShot}
              className="px-4 h-8 border border-[var(--border-default)] rounded-lg text-sm hover:bg-[var(--bg-hover)] transition-all flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              添加镜头
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

      <div className="flex-1 overflow-y-auto p-6">
        {shots.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 border border-[var(--border-default)] rounded-lg flex items-center justify-center mb-3">
              <Film className="w-6 h-6 text-[var(--text-tertiary)]" />
            </div>
            <p className="text-sm text-[var(--text-secondary)] mb-1">还没有分镜</p>
            <p className="text-xs text-[var(--text-tertiary)]">点击"添加镜头"开始创建</p>
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
                        {SHOT_SIZES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                      </select>

                      <select
                        value={shot.cameraMove}
                        onChange={(e) => updateShot(shot.id, { cameraMove: e.target.value })}
                        className="h-8 px-2 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded text-xs"
                      >
                        {CAMERA_MOVES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
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
                onClick={() => { setShowConfirm(false); onStartGeneration(shots); }}
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
