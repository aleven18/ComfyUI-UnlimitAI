import { useAppStore } from '@/store';
import { WorkflowManager, PresetType } from '@/lib/workflow-manager';
import { getApiKey } from '@/lib/unified-config';
import { Settings, DollarSign, UserCircle, Film } from 'lucide-react';

export function ConfigPanel() {
  const { params, setParams, preset, setPreset } = useAppStore();

  const effectiveParams = { ...params, apiKey: params.apiKey || getApiKey() || '' };

  const handleParamChange = (key: string, value: unknown) => {
    setParams({ [key]: value });
  };

  const handlePresetChange = (newPreset: PresetType) => {
    setPreset(newPreset);
    const defaults = WorkflowManager.getDefaultParams(newPreset);
    setParams({
      imageModel: defaults.imageModel,
      videoModel: defaults.videoModel,
      videoDuration: defaults.videoDuration,
      voiceId: defaults.voiceId,
      maxScenes: defaults.maxScenes,
      imageReference: defaults.imageReference,
    });
  };

  const estimatedCost = WorkflowManager.estimateCost(
    preset,
    effectiveParams.maxScenes || WorkflowManager.getDefaultParams(preset).maxScenes || 10
  );

  const isKlingImage = effectiveParams.imageModel === 'kling-v2';
  const isKlingVideo = effectiveParams.videoModel === 'kling-v2';

  return (
    <div className="card p-6 space-y-6">
      <div className="flex items-center gap-2">
        <Settings className="w-5 h-5 text-[var(--accent-primary)]" />
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">基础配置</h2>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">API Key *</label>
          <input
            type="password"
            value={effectiveParams.apiKey || ''}
            onChange={(e) => handleParamChange('apiKey', e.target.value)}
            placeholder="输入 UnlimitAI API Key"
            className="input-base"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">预设模式</label>
          <select
            value={preset}
            onChange={(e) => handlePresetChange(e.target.value as PresetType)}
            className="input-base"
          >
            <option value="budget">经济模式 - 快速低成本</option>
            <option value="balanced">平衡模式 - 质量与成本平衡</option>
            <option value="quality">质量模式 - 高质量输出</option>
            <option value="max_quality">最高质量 - 最佳效果</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">项目名称</label>
          <input
            type="text"
            value={effectiveParams.projectName || ''}
            onChange={(e) => handleParamChange('projectName', e.target.value)}
            placeholder="我的漫剧作品"
            className="input-base"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">最大场景数</label>
          <input
            type="number"
            min="1"
            max="50"
            value={effectiveParams.maxScenes || 10}
            onChange={(e) => handleParamChange('maxScenes', parseInt(e.target.value))}
            className="input-base"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">语言</label>
          <select
            value={effectiveParams.language || 'chinese'}
            onChange={(e) => handleParamChange('language', e.target.value)}
            className="input-base"
          >
            <option value="chinese">中文</option>
            <option value="english">英文</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">画面风格</label>
          <select
            value={effectiveParams.style || 'cinematic'}
            onChange={(e) => handleParamChange('style', e.target.value)}
            className="input-base"
          >
            <option value="cinematic">电影风格</option>
            <option value="anime">动漫风格</option>
            <option value="realistic">写实风格</option>
            <option value="artistic">艺术风格</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">图像模型</label>
          <select
            value={effectiveParams.imageModel || 'flux-pro'}
            onChange={(e) => handleParamChange('imageModel', e.target.value)}
            className="input-base"
          >
            <option value="flux-pro">FLUX Pro</option>
            <option value="ideogram-v3">Ideogram V3</option>
            <option value="kling-v2">Kling V2（支持角色一致性）</option>
            <option value="dall-e-3">DALL-E 3</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">视频模型</label>
          <select
            value={effectiveParams.videoModel || 'kling-v2'}
            onChange={(e) => handleParamChange('videoModel', e.target.value)}
            className="input-base"
          >
            <option value="kling-v2">Kling V2（支持故事板合并）</option>
            <option value="veo-3.1">VEO 3.1</option>
            <option value="vidu2">Vidu2</option>
            <option value="hailuo">Hailuo</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">画面比例</label>
          <select
            value={effectiveParams.aspectRatio || '16:9'}
            onChange={(e) => handleParamChange('aspectRatio', e.target.value)}
            className="input-base"
          >
            <option value="16:9">16:9 横屏</option>
            <option value="9:16">9:16 竖屏</option>
            <option value="1:1">1:1 方形</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">视频时长</label>
          <select
            value={effectiveParams.videoDuration || '5'}
            onChange={(e) => handleParamChange('videoDuration', e.target.value)}
            className="input-base"
          >
            <option value="5">5 秒</option>
            <option value="10">10 秒</option>
          </select>
        </div>
      </div>

      {isKlingImage && (
        <div className="border border-[var(--accent-primary)] border-opacity-30 rounded-lg p-4 bg-[var(--accent-primary)] bg-opacity-5 space-y-4">
          <div className="flex items-center gap-2">
            <UserCircle className="w-5 h-5 text-[var(--accent-primary)]" />
            <h3 className="text-md font-semibold text-[var(--text-primary)]">角色一致性</h3>
          </div>
          <p className="text-xs text-[var(--text-tertiary)]">
            上传角色参考图，让所有场景保持同一角色外观。仅 Kling V2 图像模型支持。
          </p>

          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">参考图 URL</label>
            <input
              type="text"
              value={effectiveParams.refImageUrl || ''}
              onChange={(e) => handleParamChange('refImageUrl', e.target.value)}
              placeholder="https://example.com/character.jpg"
              className="input-base"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">一致性模式</label>
            <select
              value={effectiveParams.imageReference || 'none'}
              onChange={(e) => handleParamChange('imageReference', e.target.value)}
              className="input-base"
            >
              <option value="none">关闭</option>
              <option value="subject">主体一致 - 保持角色整体外观</option>
              <option value="face">面部一致 - 仅保持面部特征</option>
            </select>
          </div>

          {effectiveParams.imageReference !== 'none' && effectiveParams.imageReference !== undefined && (
            <>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                  参考图强度: {effectiveParams.imageFidelity ?? 0.5}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={effectiveParams.imageFidelity ?? 0.5}
                  onChange={(e) => handleParamChange('imageFidelity', parseFloat(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-[var(--text-tertiary)]">
                  <span>自由</span>
                  <span>严格遵循</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                  角色相似度: {effectiveParams.humanFidelity ?? 0.45}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={effectiveParams.humanFidelity ?? 0.45}
                  onChange={(e) => handleParamChange('humanFidelity', parseFloat(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-[var(--text-tertiary)]">
                  <span>自由</span>
                  <span>高度一致</span>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {isKlingVideo && (
        <div className="border border-[var(--accent-primary)] border-opacity-30 rounded-lg p-4 bg-[var(--accent-primary)] bg-opacity-5 space-y-4">
          <div className="flex items-center gap-2">
            <Film className="w-5 h-5 text-[var(--accent-primary)]" />
            <h3 className="text-md font-semibold text-[var(--text-primary)]">故事板模式</h3>
          </div>
          <p className="text-xs text-[var(--text-tertiary)]">
            将所有场景合并为一个 Kling 故事板视频，场景间自动过渡。仅 Kling V2 视频模型支持。
          </p>

          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">故事板模式</label>
            <select
              value={effectiveParams.storyboardMode || 'disabled'}
              onChange={(e) => handleParamChange('storyboardMode', e.target.value)}
              className="input-base"
            >
              <option value="disabled">关闭 - 逐场景生成视频</option>
              <option value="combine_scenes">合并 - 所有场景合成一个故事板视频</option>
            </select>
          </div>

          {effectiveParams.storyboardMode === 'combine_scenes' && (
            <div className="p-3 bg-[var(--bg-tertiary)] rounded text-xs text-[var(--text-secondary)]">
              将每个场景的 visual_prompt 作为故事板片段，时长均分到各场景。总时长 = 视频时长设置。
            </div>
          )}
        </div>
      )}

      <div className="p-4 bg-[var(--bg-tertiary)] rounded-lg border border-[var(--border-default)]">
        <div className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-[var(--accent-primary)]" />
          <div>
            <p className="text-sm text-[var(--text-tertiary)]">预估成本</p>
            <p className="text-xl font-bold text-[var(--accent-primary)]">
              ${estimatedCost.toFixed(2)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
