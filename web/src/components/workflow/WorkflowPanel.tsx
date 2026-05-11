import { useState } from 'react';
import { Play, Pause, DollarSign } from 'lucide-react';
import { useProjectStore } from '@/store/projectStore';
import { useComfyUI } from '@/hooks/useComfyUI';

export function WorkflowPanel() {
  const { scenes, characters } = useProjectStore();
  const { startConversionWithStoryboard, isConverting, progress, logs } = useComfyUI();
  
  const [preset, setPreset] = useState<'budget' | 'balanced' | 'quality' | 'max_quality'>('balanced');
  const [generationMode, setGenerationMode] = useState<'batch' | 'single'>('batch');
  
  const totalDuration = scenes.reduce((sum, s) => sum + s.duration, 0);
  const estimatedCost = calculateCost(scenes.length, totalDuration, preset);
  
  const handleStartGeneration = async () => {
    if (scenes.length === 0) {
      alert('请先创建场景');
      return;
    }
    
    if (!confirm(`确定要开始生成 ${scenes.length} 个场景吗？\n预估成本: $${estimatedCost.toFixed(2)}`)) {
      return;
    }
    
    // 转换为Shot格式
    const shots = scenes.map(scene => ({
      id: scene.id,
      shotNumber: scene.shotNumber,
      shotSize: scene.shotSize,
      cameraMove: scene.cameraMove,
      duration: scene.duration,
      description: scene.description,
      prompt: scene.prompt,
      notes: scene.notes,
      characters: scene.characters
    }));
    
    await startConversionWithStoryboard(shots);
  };
  
  return (
    <div className="p-6 max-w-4xl">
      <h2 className="text-lg font-semibold mb-6">工作流</h2>
      
      {/* Generation Mode */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">生成模式</label>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => setGenerationMode('batch')}
            className={`p-4 border rounded-lg text-left ${
              generationMode === 'batch' 
                ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)] bg-opacity-10' 
                : 'border-[var(--border-default)]'
            }`}
          >
            <div className="font-medium">批量生成</div>
            <div className="text-sm text-[var(--text-tertiary)] mt-1">一次性生成所有场景</div>
          </button>
          <button
            onClick={() => setGenerationMode('single')}
            className={`p-4 border rounded-lg text-left ${
              generationMode === 'single' 
                ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)] bg-opacity-10' 
                : 'border-[var(--border-default)]'
            }`}
          >
            <div className="font-medium">单场景生成</div>
            <div className="text-sm text-[var(--text-tertiary)] mt-1">逐个生成场景</div>
          </button>
        </div>
      </div>
      
      {/* Quality Preset */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">质量预设</label>
        <div className="grid grid-cols-2 gap-3">
          {[
            { id: 'budget', name: '经济模式', cost: 0.30, desc: '快速生成，低成本' },
            { id: 'balanced', name: '平衡模式', cost: 0.52, desc: '质量与成本平衡' },
            { id: 'quality', name: '高质量', cost: 0.61, desc: '高质量输出' },
            { id: 'max_quality', name: '最高质量', cost: 0.75, desc: '专业级质量' }
          ].map(option => (
            <button
              key={option.id}
              onClick={() => setPreset(option.id as any)}
              className={`p-4 border rounded-lg text-left ${
                preset === option.id 
                  ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)] bg-opacity-10' 
                  : 'border-[var(--border-default)]'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium">{option.name}</span>
                <span className="text-sm text-[var(--accent-primary)]">${option.cost}/场景</span>
              </div>
              <div className="text-sm text-[var(--text-tertiary)]">{option.desc}</div>
            </button>
          ))}
        </div>
      </div>
      
      {/* Cost Estimation */}
      <div className="mb-6 p-4 bg-[var(--bg-secondary)] rounded-lg">
        <h3 className="font-medium mb-3 flex items-center gap-2">
          <DollarSign className="w-4 h-4" />
          成本预估
        </h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-[var(--text-tertiary)]">场景数量</div>
            <div className="font-medium mt-1">{scenes.length} 个</div>
          </div>
          <div>
            <div className="text-[var(--text-tertiary)]">总时长</div>
            <div className="font-medium mt-1">{totalDuration} 秒</div>
          </div>
          <div>
            <div className="text-[var(--text-tertiary)]">预估成本</div>
            <div className="font-medium mt-1 text-[var(--accent-primary)]">${estimatedCost.toFixed(2)}</div>
          </div>
        </div>
      </div>
      
      {/* Progress */}
      {isConverting && (
        <div className="mb-6 p-4 border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="font-medium">生成进度</span>
            <span className="text-sm text-[var(--text-tertiary)]">{progress.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-[var(--bg-tertiary)] rounded-full h-2">
            <div 
              className="bg-[var(--accent-primary)] h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="mt-3 max-h-32 overflow-y-auto">
            {logs.slice(-5).map((log, i) => (
              <div key={i} className="text-xs text-[var(--text-secondary)] py-1">{log}</div>
            ))}
          </div>
        </div>
      )}
      
      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleStartGeneration}
          disabled={isConverting || scenes.length === 0}
          className="flex-1 px-6 py-3 bg-[var(--accent-primary)] text-white rounded-lg hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isConverting ? (
            <>
              <Pause className="w-4 h-4" />
              生成中...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              开始生成
            </>
          )}
        </button>
      </div>
    </div>
  );
}

function calculateCost(sceneCount: number, totalDuration: number, preset: string): number {
  const costPerScene: Record<string, number> = {
    'budget': 0.30,
    'balanced': 0.52,
    'quality': 0.61,
    'max_quality': 0.75
  };
  
  const baseCost = sceneCount * costPerScene[preset];
  const videoCost = totalDuration * 0.05;
  
  return baseCost + videoCost;
}
