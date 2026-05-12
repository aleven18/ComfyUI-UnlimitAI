import { useAppStore } from '@/store';
import { PresetType } from '@/types';
import { FileJson, Check } from 'lucide-react';

interface Workflow {
  id: string;
  name: string;
  description: string;
  icon: string;
  features: string[];
  cost: string;
  speed: string;
  quality: string;
}

const workflows: Workflow[] = [
  {
    id: 'budget',
    name: '经济模式',
    description: '快速低成本，适合测试和预览',
    icon: '💰',
    features: ['Flux Schnell', 'Kling v1 (5秒)', '快速TTS'],
    cost: '$0.31/场景',
    speed: '⚡⚡⚡⚡⚡',
    quality: '⭐⭐⭐'
  },
  {
    id: 'balanced',
    name: '平衡模式',
    description: '质量与成本平衡，推荐日常使用',
    icon: '⚖️',
    features: ['Flux Dev', 'Kling v1.5 (10秒)', 'Minimax音频'],
    cost: '$0.52/场景',
    speed: '⚡⚡⚡⚡',
    quality: '⭐⭐⭐⭐'
  },
  {
    id: 'quality',
    name: '质量模式',
    description: '高质量输出，适合重要项目',
    icon: '🎨',
    features: ['Flux Pro', 'Kling v2 (10秒)', 'HD音频'],
    cost: '$0.61/场景',
    speed: '⚡⚡⚡',
    quality: '⭐⭐⭐⭐⭐'
  },
  {
    id: 'max_quality',
    name: '最高质量',
    description: '最佳效果，适合商业项目',
    icon: '🏆',
    features: ['Imagen 4.0', 'VEO 3.1 (10秒)', 'HD音频+音乐'],
    cost: '$0.75/场景',
    speed: '⚡⚡',
    quality: '⭐⭐⭐⭐⭐+'
  }
];

export function WorkflowSelector() {
  const { preset, setPreset } = useAppStore();

  return (
    <div className="bg-[var(--bg-elevated)] rounded-lg shadow-md p-6">
      <div className="flex items-center gap-2 mb-4">
        <FileJson className="w-5 h-5 text-[var(--accent-primary)]" />
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">选择工作流</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {workflows.map((workflow) => (
          <div
            key={workflow.id}
            className={`
              relative border-2 rounded-lg p-4 cursor-pointer transition-all
              ${preset === workflow.id
                ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)] bg-opacity-5'
                : 'border-[var(--border-subtle)] hover:border-[var(--accent-primary)] hover:border-opacity-50 hover:bg-[var(--bg-tertiary)]'}
            `}
            onClick={() => setPreset(workflow.id as PresetType)}
          >
            {preset === workflow.id && (
              <div className="absolute top-2 right-2">
                <div className="bg-[var(--accent-primary)] rounded-full p-1">
                  <Check className="w-4 h-4 text-white" />
                </div>
              </div>
            )}

            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">{workflow.icon}</span>
              <div>
                <h3 className="font-semibold text-[var(--text-primary)]">{workflow.name}</h3>
                <p className="text-xs text-[var(--text-secondary)]">{workflow.description}</p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-3">
              {workflow.features.map((feature, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-1 bg-[var(--bg-tertiary)] rounded-full text-[var(--text-secondary)]"
                >
                  {feature}
                </span>
              ))}
            </div>

            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>
                <span className="text-[var(--text-tertiary)]">成本:</span>
                <span className="ml-1 font-medium text-[var(--text-primary)]">{workflow.cost}</span>
              </div>
              <div>
                <span className="text-[var(--text-tertiary)]">速度:</span>
                <span className="ml-1">{workflow.speed}</span>
              </div>
              <div>
                <span className="text-[var(--text-tertiary)]">质量:</span>
                <span className="ml-1">{workflow.quality}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-[var(--accent-primary)] bg-opacity-5 rounded-lg border border-[var(--accent-primary)] border-opacity-30">
        <p className="text-sm text-[var(--accent-primary)]">
          <span className="font-medium">当前选择:</span>{' '}
          {workflows.find(w => w.id === preset)?.name} - {workflows.find(w => w.id === preset)?.description}
        </p>
      </div>
    </div>
  );
}
