import { useAppStore } from '@/store';
import { Info, Zap, DollarSign, Clock } from 'lucide-react';

export function ModelComparisonPanel() {
  const { preset } = useAppStore();

  const models = {
    budget: {
      text: { name: 'DeepSeek Chat', time: '10秒', cost: '$0.001' },
      image: { name: 'Flux Schnell', time: '8秒', cost: '$0.003' },
      video: { name: 'Kling v1 (5秒)', time: '50秒', cost: '$0.30' },
      audio: { name: 'OpenAI TTS-1', time: '2秒', cost: '$0.003' },
      music: { name: '无', time: '-', cost: '-' },
    },
    balanced: {
      text: { name: 'DeepSeek Chat', time: '10秒', cost: '$0.001' },
      image: { name: 'Flux Dev', time: '15秒', cost: '$0.015' },
      video: { name: 'Kling v1.5 (10秒)', time: '65秒', cost: '$0.40' },
      audio: { name: 'Minimax', time: '3秒', cost: '$0.002' },
      music: { name: 'Suno V3 (可选)', time: '30秒', cost: '$0.05' },
    },
    quality: {
      text: { name: 'GPT-4o', time: '15秒', cost: '$0.005' },
      image: { name: 'Flux Pro', time: '25秒', cost: '$0.025' },
      video: { name: 'Kling v2 (10秒)', time: '75秒', cost: '$0.50' },
      audio: { name: 'Minimax', time: '4秒', cost: '$0.003' },
      music: { name: 'Suno V3.5', time: '40秒', cost: '$0.08' },
    },
    max_quality: {
      text: { name: 'Claude 3.5 Sonnet', time: '18秒', cost: '$0.003' },
      image: { name: 'Imagen 4.0', time: '35秒', cost: '$0.040' },
      video: { name: 'VEO 3.1 (10秒)', time: '100秒', cost: '$0.60' },
      audio: { name: 'OpenAI TTS-1 HD', time: '5秒', cost: '$0.030' },
      music: { name: 'Suno V3.5', time: '45秒', cost: '$0.08' },
    },
  };

  const currentModels = models[preset as keyof typeof models];

  return (
    <div className="bg-[var(--bg-elevated)] rounded-lg shadow-md p-6">
      <div className="flex items-center gap-2 mb-4">
        <Info className="w-5 h-5 text-[var(--accent-primary)]" />
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">当前模型配置</h2>
      </div>

      <div className="space-y-3">
        {Object.entries(currentModels).map(([type, model]) => (
          <div key={type} className="border rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-[var(--text-primary)] capitalize">
                  {type === 'text' && '📝 文本模型'}
                  {type === 'image' && '🖼️ 图像模型'}
                  {type === 'video' && '🎬 视频模型'}
                  {type === 'audio' && '🔊 音频模型'}
                  {type === 'music' && '🎵 音乐模型'}
                </p>
                <p className="text-xs text-[var(--text-secondary)]">{model.name}</p>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 text-xs text-[var(--text-secondary)]">
                  <Clock className="w-3 h-3" />
                  <span>{model.time}</span>
                </div>
                <div className="flex items-center gap-1 text-xs text-[var(--text-secondary)]">
                  <DollarSign className="w-3 h-3" />
                  <span>{model.cost}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-[var(--bg-tertiary)] rounded-lg">
        <p className="text-xs text-[var(--text-secondary)]">
          <Zap className="w-3 h-3 inline mr-1" />
          切换工作流模式会自动选择最优模型组合
        </p>
      </div>
    </div>
  );
}
