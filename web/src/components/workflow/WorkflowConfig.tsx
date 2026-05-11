/**
 * 工作流配置中心
 * 
 * 用于配置每个模块的参数，不执行任务
 * 设计风格：简约、专业、高级
 */

import { useProjectStore } from '@/store/projectStore';

export function WorkflowConfig() {
  const { settings, updateSettings } = useProjectStore();
  
  return (
    <div className="h-full overflow-y-auto p-8">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-1">工作流配置</h2>
          <p className="text-sm text-[var(--text-tertiary)]">配置各模块参数，设置将在各标签页执行任务时生效</p>
        </div>
        
        <div className="space-y-4 pb-8">
          <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
            <div className="bg-[var(--bg-secondary)] px-6 py-4 border-b border-[var(--border-default)]">
              <h3 className="text-sm font-medium text-[var(--text-primary)]">模块1 · 小说分析</h3>
            </div>
            
            <div className="p-6 space-y-5">
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">文本模型</label>
                <select 
                  className="w-full px-3 py-2 text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] rounded focus:outline-none focus:border-[var(--accent-primary)]"
                  value={settings.defaultImageModel || 'gpt-4o-mini'}
                  onChange={(e) => updateSettings({ defaultImageModel: e.target.value })}
                >
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="deepseek-chat">DeepSeek Chat</option>
                  <option value="qwen-max">Qwen Max</option>
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">最大场景数</label>
                <input
                  type="range"
                  min="1"
                  max="50"
                  defaultValue="15"
                  className="w-full h-1 bg-[var(--bg-tertiary)] rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-[var(--text-tertiary)] mt-1">
                  <span>1</span>
                  <span className="font-medium">15</span>
                  <span>50</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
            <div className="bg-[var(--bg-secondary)] px-6 py-4 border-b border-[var(--border-default)]">
              <h3 className="text-sm font-medium text-[var(--text-primary)]">模块2 · 角色创建</h3>
            </div>
            
            <div className="p-6 space-y-5">
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">图像模型</label>
                <select 
                  className="w-full px-3 py-2 text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] rounded focus:outline-none focus:border-[var(--accent-primary)]"
                  value={settings.defaultImageModel}
                  onChange={(e) => updateSettings({ defaultImageModel: e.target.value })}
                >
                  <option value="doubao-seedream-4-0-250828">🫘 豆包 Seedream 4.0 ✓ (11.9秒)</option>
                  <option value="gpt-image-1-all">🍌 香蕉 GPT Image All ✓ (13.5秒)</option>
                </select>
                <p className="text-xs text-green-500 mt-2">
                  ✓ 已测试可用
                </p>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">每个角色参考图数量</label>
                <input
                  type="range"
                  min="3"
                  max="10"
                  defaultValue="5"
                  className="w-full h-1 bg-[var(--bg-tertiary)] rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-[var(--text-tertiary)] mt-1">
                  <span>3张</span>
                  <span className="font-medium">5张</span>
                  <span>10张</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
            <div className="bg-[var(--bg-secondary)] px-6 py-4 border-b border-[var(--border-default)]">
              <h3 className="text-sm font-medium text-[var(--text-primary)]">模块3 · 分镜脚本</h3>
            </div>
            
            <div className="p-6 space-y-5">
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">细节级别</label>
                <select className="w-full px-3 py-2 text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] rounded focus:outline-none focus:border-[var(--accent-primary)]">
                  <option value="simple">简单 — 快速</option>
                  <option value="standard">标准 — 平衡</option>
                  <option value="detailed">详细 — 高质量</option>
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">目标时长</label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min="10"
                    max="300"
                    defaultValue="60"
                    className="flex-1 px-3 py-2 text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] rounded focus:outline-none focus:border-[var(--accent-primary)]"
                  />
                  <span className="text-sm text-[var(--text-secondary)]">秒</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
            <div className="bg-[var(--bg-secondary)] px-6 py-4 border-b border-[var(--border-default)]">
              <h3 className="text-sm font-medium text-[var(--text-primary)]">模块4 · 资源生成</h3>
            </div>
            
            <div className="p-6 space-y-5">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">图像模型</label>
                  <select 
                    className="w-full px-3 py-2 text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] rounded focus:outline-none focus:border-[var(--accent-primary)]"
                    value={settings.defaultImageModel}
                    onChange={(e) => updateSettings({ defaultImageModel: e.target.value })}
                  >
                    <option value="doubao-seedream-4-0-250828">🫘 豆包 Seedream 4.0 ✓</option>
                    <option value="gpt-image-1-all">🍌 香蕉 GPT Image All ✓</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">视频模型</label>
                  <select 
                    className="w-full px-3 py-2 text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] rounded focus:outline-none focus:border-[var(--accent-primary)]"
                    value={settings.defaultVideoModel}
                    onChange={(e) => updateSettings({ defaultVideoModel: e.target.value })}
                  >
                    <optgroup label="VEO 3.1系列（推荐）">
                      <option value="veo3.1-fast">VEO 3.1 Fast ✓</option>
                      <option value="veo3.1-pro">VEO 3.1 Pro ✓</option>
                    </optgroup>
                    <optgroup label="VEO 3系列">
                      <option value="veo3">VEO 3 ✓</option>
                      <option value="veo3-fast">VEO 3 Fast ✓</option>
                    </optgroup>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">音频引擎</label>
                <select 
                  className="w-full px-3 py-2 text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] rounded focus:outline-none focus:border-[var(--accent-primary)]"
                  value={settings.defaultAudioEngine}
                  onChange={(e) => updateSettings({ defaultAudioEngine: e.target.value })}
                >
                  <option value="minimax">Minimax</option>
                  <option value="openai">OpenAI TTS</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="border border-[var(--border-default)] rounded-lg overflow-hidden">
            <div className="bg-[var(--bg-secondary)] px-6 py-4 border-b border-[var(--border-default)]">
              <h3 className="text-sm font-medium text-[var(--text-primary)]">模块5 · 最终合成</h3>
            </div>
            
            <div className="p-6 space-y-5">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">输出格式</label>
                  <select className="w-full px-3 py-2 text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] rounded focus:outline-none focus:border-[var(--accent-primary)]">
                    <option value="mp4">MP4</option>
                    <option value="webm">WebM</option>
                    <option value="mov">MOV</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2 uppercase tracking-wide">质量预设</label>
                  <select className="w-full px-3 py-2 text-sm bg-[var(--bg-primary)] border border-[var(--border-default)] rounded focus:outline-none focus:border-[var(--accent-primary)]">
                    <option value="preview">预览 — 快速</option>
                    <option value="standard">标准</option>
                    <option value="high">高质量</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          
          <div className="pt-2">
            <button
              className="w-full py-3 text-sm font-medium bg-[var(--accent-primary)] text-white rounded hover:opacity-90 transition-opacity"
              onClick={() => {
                alert('配置已保存');
              }}
            >
              保存配置
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
