/**
 * 全局设置面板
 * 
 * 真正影响工作流的配置：
 * 1. 工作流模式（快速/标准/专业）
 * 2. 默认模型配置
 * 3. API Key 管理
 */

import { useState, useEffect } from 'react';
import { X, Zap, Gauge, Crown, Info, TestTube } from 'lucide-react';
import { useProjectStore } from '@/store/projectStore';
import { ImageModelDiagnostic } from '@/components/tools/ImageModelDiagnostic';
import { TextModelDiagnostic } from '@/components/tools/TextModelDiagnostic';
import { TTSModelDiagnostic } from '@/components/tools/TTSModelDiagnostic';

interface GlobalSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type WorkflowMode = 'fast' | 'standard' | 'professional';

const workflowModes = [
  {
    id: 'fast' as const,
    label: '快速模式',
    icon: <Zap className="w-5 h-5" />,
    description: '快速生成，成本优先',
    models: {
      text: 'gpt-4o-mini',
      image: 'doubao-seedream-4-0-250828',
      video: 'kling-v1'
    },
    color: 'text-yellow-500'
  },
  {
    id: 'standard' as const,
    label: '标准模式',
    icon: <Gauge className="w-5 h-5" />,
    description: '平衡质量与成本',
    models: {
      text: 'deepseek-chat',
      image: 'doubao-seedream-4-0-250828',
      video: 'doubao-seedance-1-0-lite-i2v-250428'
    },
    color: 'text-blue-500'
  },
  {
    id: 'professional' as const,
    label: '专业模式',
    icon: <Crown className="w-5 h-5" />,
    description: '最高质量，不计成本',
    models: {
      text: 'gpt-4o',
      image: 'doubao-seedream-4-0-250828',
      video: 'kling-v3'
    },
    color: 'text-purple-500'
  }
];

export function GlobalSettingsModal({ isOpen, onClose }: GlobalSettingsModalProps) {
  const { settings, updateSettings } = useProjectStore();
  const [selectedMode, setSelectedMode] = useState<WorkflowMode>('standard');
  const [apiKey, setApiKey] = useState('');
  
  useEffect(() => {
    setApiKey(settings.apiKey || '');
    
    // 根据当前文本模型配置推断模式
    if (settings.defaultTextModel === 'gpt-4o-mini') {
      setSelectedMode('fast');
    } else if (settings.defaultTextModel === 'gpt-4o') {
      setSelectedMode('professional');
    } else {
      setSelectedMode('standard');
    }
  }, [settings, isOpen]);
  
  if (!isOpen) return null;
  
  const handleModeChange = (mode: WorkflowMode) => {
    setSelectedMode(mode);
    
    const modeConfig = workflowModes.find(m => m.id === mode);
    if (modeConfig) {
      updateSettings({
        defaultImageModel: modeConfig.models.image,
        defaultVideoModel: modeConfig.models.video,
        defaultAudioEngine: 'minimax'
      });
    }
  };
  
  const handleSave = () => {
    if (apiKey.trim()) {
      updateSettings({ apiKey: apiKey.trim() });
    }
    onClose();
  };
  
  const currentMode = workflowModes.find(m => m.id === selectedMode);
  
  return (
    <>
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 animate-fade-in"
        onClick={onClose}
      />
      
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div 
          className="bg-[var(--bg-primary)] rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden animate-scale-in"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 头部 */}
          <div className="relative px-6 py-5 border-b border-[var(--border-subtle)]">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">全局设置</h2>
            <p className="text-sm text-[var(--text-tertiary)] mt-1">配置默认工作流模式和模型</p>
            
            <button
              onClick={onClose}
              className="absolute top-5 right-6 p-1.5 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
            >
              <X className="w-5 h-5 text-[var(--text-tertiary)]" />
            </button>
          </div>
          
          {/* 内容 */}
          <div className="px-6 py-6 space-y-6 max-h-[70vh] overflow-y-auto">
            {/* 工作流模式 */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
                工作流模式
              </label>
              
              <div className="grid grid-cols-3 gap-3">
                {workflowModes.map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => handleModeChange(mode.id)}
                    className={`
                      relative flex flex-col items-center justify-center py-5 rounded-xl border-2 transition-all
                      ${selectedMode === mode.id
                        ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/5'
                        : 'border-[var(--border-default)] hover:border-[var(--accent-primary)]/50 hover:bg-[var(--bg-hover)]'
                      }
                    `}
                  >
                    {selectedMode === mode.id && (
                      <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-[var(--accent-primary)]" />
                    )}
                    
                    <div className={mode.color}>
                      {mode.icon}
                    </div>
                    
                    <span className="text-sm font-medium mt-2">{mode.label}</span>
                    <span className="text-xs text-[var(--text-tertiary)] mt-1 text-center px-2">
                      {mode.description}
                    </span>
                  </button>
                ))}
              </div>
              
              {/* 当前模式详情 */}
              {currentMode && (
                <div className="mt-4 p-4 bg-[var(--bg-secondary)] rounded-lg border border-[var(--border-default)]">
                  <div className="flex items-start gap-2 mb-3">
                    <Info className="w-4 h-4 text-[var(--text-tertiary)] mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-[var(--text-primary)]">
                        {currentMode.label}配置
                      </p>
                      <p className="text-xs text-[var(--text-tertiary)] mt-1">
                        文本模型: {currentMode.models.text} · 图像模型: {currentMode.models.image} · 视频模型: {currentMode.models.video}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* API Key */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full h-11 px-4 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
              />
              <p className="text-xs text-[var(--text-tertiary)] mt-2">
                用于所有AI功能的统一API Key
              </p>
            </div>
            
            {/* 自定义模型配置 */}
            <div>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
                自定义模型配置
              </label>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-[var(--text-tertiary)] mb-1.5">文本模型</label>
                  <select 
                    className="w-full h-10 px-3 text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]"
                    value={settings.defaultTextModel || 'deepseek-chat'}
                    onChange={(e) => updateSettings({ defaultTextModel: e.target.value })}
                  >
                    <optgroup label="OpenAI 系列">
                      <option value="gpt-4o">GPT-4o ✓</option>
                      <option value="gpt-4o-mini">GPT-4o Mini ✓</option>
                      <option value="gpt-4-turbo">GPT-4 Turbo ✓</option>
                    </optgroup>
                    <optgroup label="DeepSeek 系列">
                      <option value="deepseek-chat">DeepSeek Chat ✓</option>
                    </optgroup>
                    <optgroup label="Qwen 系列">
                      <option value="qwen-max">Qwen Max ✓</option>
                      <option value="qwen-plus">Qwen Plus ✓</option>
                      <option value="qwen-turbo">Qwen Turbo ✓</option>
                    </optgroup>
                  </select>
                </div>
                
                <div>
                  <label className="block text-xs text-[var(--text-tertiary)] mb-1.5">图像模型</label>
                  <select 
                    className="w-full h-10 px-3 text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]"
                    value={settings.defaultImageModel || 'doubao-seedream-4-0-250828'}
                    onChange={(e) => updateSettings({ defaultImageModel: e.target.value })}
                  >
                    <optgroup label="推荐模型">
                      <option value="doubao-seedream-4-0-250828">🫘 豆包 Seedream 4.0 ✓</option>
                      <option value="gpt-image-1-all">🍌 香蕉 GPT Image All ✓</option>
                    </optgroup>
                  </select>
                  <p className="text-xs text-green-500 mt-1">✓ 已测试可用</p>
                </div>
                
                <div>
                  <label className="block text-xs text-[var(--text-tertiary)] mb-1.5">语音合成模型</label>
                  <select 
                    className="w-full h-10 px-3 text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]"
                    value={settings.defaultTTSModel || 'tts-1'}
                    onChange={(e) => updateSettings({ defaultTTSModel: e.target.value })}
                  >
                    <optgroup label="推荐模型">
                      <option value="tts-1">TTS-1 ✓ (2.2秒)</option>
                      <option value="tts-1-hd">TTS-1 HD ✓ (10.3秒)</option>
                    </optgroup>
                  </select>
                  <p className="text-xs text-green-500 mt-1">✓ 已测试可用</p>
                </div>
                
                <div>
                  <label className="block text-xs text-[var(--text-tertiary)] mb-1.5">视频模型</label>
                  <select 
                    className="w-full h-10 px-3 text-sm bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]"
                    value={settings.defaultVideoModel || 'doubao-seedance-1-0-lite-i2v-250428'}
                    onChange={(e) => updateSettings({ defaultVideoModel: e.target.value })}
                  >
                    <optgroup label="豆包系列（角色一致性最佳）">
                      <option value="doubao-seedance-1-0-lite-i2v-250428">🫘 豆包 Seedance ✓ (36秒，支持1-4张参考图)</option>
                    </optgroup>
                    <optgroup label="可灵系列（功能丰富）">
                      <option value="kling-v1">🎬 可灵 V1 ✓ (180秒)</option>
                      <option value="kling-v1-6">🎬 可灵 V1.6 ✓ (支持多图参考)</option>
                      <option value="kling-v2-master">🎬 可灵 V2 Master ✓ (高品质)</option>
                      <option value="kling-v2-5-turbo">🎬 可灵 V2.5 Turbo ✓ (快速)</option>
                      <option value="kling-v3">🎬 可灵 V3 ✓ (最新)</option>
                    </optgroup>
                    <optgroup label="通义万象系列">
                      <option value="wan2.5-i2v-preview">🌟 通义万象 I2V ✓ (60秒，自动音频)</option>
                    </optgroup>
                    <optgroup label="VEO 3.1系列">
                      <option value="veo3.1-fast">VEO 3.1 Fast ✓ (155秒)</option>
                      <option value="veo3.1-pro">VEO 3.1 Pro ✓ (130秒)</option>
                      <option value="veo3.1">VEO 3.1 ✓ (标准)</option>
                    </optgroup>
                    <optgroup label="VEO 3系列">
                      <option value="veo3-fast">VEO 3 Fast ✓ (174秒)</option>
                      <option value="veo3">VEO 3 ✓ (287秒，带音频)</option>
                    </optgroup>
                  </select>
                  <p className="text-xs text-green-500 mt-1">✓ 已测试可用（12个模型，含Kling系列）</p>
                </div>
              </div>
              
              <p className="text-xs text-[var(--text-tertiary)] mt-2">
                自定义配置会覆盖工作流模式的默认设置
              </p>
            </div>

            {/* 图像模型诊断 */}
            <div className="pt-4 border-t border-[var(--border-subtle)]">
              <div className="flex items-center gap-2 mb-4">
                <TestTube className="w-5 h-5 text-[var(--text-secondary)]" />
                <label className="text-sm font-medium text-[var(--text-primary)]">
                  模型诊断工具
                </label>
              </div>
              
              <div className="space-y-6">
                <TextModelDiagnostic />
                <ImageModelDiagnostic />
                <TTSModelDiagnostic />
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
              onClick={handleSave}
              className="px-6 py-2 bg-[var(--accent-primary)] text-white text-sm font-medium rounded-lg hover:opacity-90 transition-all"
            >
              保存设置
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
