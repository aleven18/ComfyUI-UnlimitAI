import { useState } from 'react';
import { useAppStore } from '@/store';
import { Settings, Key, Server, Save, Eye, EyeOff } from 'lucide-react';

export function SettingsPanel() {
  const { params, setParams } = useAppStore();
  const [showApiKey, setShowApiKey] = useState(false);
  const [activeTab, setActiveTab] = useState<'api' | 'server' | 'advanced'>('api');

  const handleSave = () => {
    localStorage.setItem('comfyui-settings', JSON.stringify(params));
    alert('✅ 设置已保存！');
  };

  const handleReset = () => {
    if (confirm('确定要重置所有设置吗？')) {
      setParams({
        apiKey: '',
        projectName: '我的漫剧作品',
        maxScenes: 10,
        language: 'chinese',
        style: 'cinematic'
      });
      localStorage.removeItem('comfyui-settings');
      alert('✅ 设置已重置！');
    }
  };

  return (
    <div className="bg-[var(--bg-elevated)] rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-[var(--accent-primary)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">设置</h2>
        </div>
      </div>

      <div className="flex border-b border-[var(--border-subtle)] mb-4">
        <button
          className={`px-4 py-2 text-sm font-medium ${
            activeTab === 'api'
              ? 'text-[var(--accent-primary)] border-b-2 border-[var(--accent-primary)]'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
          onClick={() => setActiveTab('api')}
        >
          <Key className="w-4 h-4 inline mr-1" />
          API配置
        </button>
        <button
          className={`px-4 py-2 text-sm font-medium ${
            activeTab === 'server'
              ? 'text-[var(--accent-primary)] border-b-2 border-[var(--accent-primary)]'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
          onClick={() => setActiveTab('server')}
        >
          <Server className="w-4 h-4 inline mr-1" />
          服务器
        </button>
      </div>

      {activeTab === 'api' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
              UnlimitAI API Key
            </label>
            <div className="relative">
              <input
                type={showApiKey ? 'text' : 'password'}
                value={params.apiKey || ''}
                onChange={(e) => setParams({ apiKey: e.target.value })}
                placeholder="输入你的API Key"
                className="w-full px-3 py-2 pr-10 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-[var(--accent-primary)]"
              />
              <button
                type="button"
                className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]"
                onClick={() => setShowApiKey(!showApiKey)}
              >
                {showApiKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            <p className="text-xs text-[var(--text-tertiary)] mt-1">
              从 UnlimitAI 官网获取你的API Key
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
              ComfyUI API 端点
            </label>
            <input
              type="text"
              value="http://127.0.0.1:8188"
              disabled
              className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)]"
            />
            <p className="text-xs text-[var(--text-tertiary)] mt-1">
              ComfyUI服务地址（自动检测）
            </p>
          </div>

          <div className="pt-2">
            <button
              onClick={async () => {
                try {
                  const response = await fetch('http://127.0.0.1:8188/system_stats');
                  if (response.ok) {
                    alert('✅ 连接成功！ComfyUI正在运行');
                  } else {
                    alert('❌ 连接失败，请检查ComfyUI是否启动');
                  }
                } catch (error) {
                  alert('❌ 连接失败，请检查ComfyUI是否启动');
                }
              }}
              className="w-full px-4 py-2 bg-[var(--bg-tertiary)] hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] rounded-lg text-sm font-medium"
            >
              测试连接
            </button>
          </div>
        </div>
      )}

      {activeTab === 'server' && (
        <div className="space-y-4">
          <div className="p-4 bg-[var(--bg-tertiary)] rounded-lg">
            <h3 className="font-medium text-[var(--text-primary)] mb-2">ComfyUI状态</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[var(--text-secondary)]">地址:</span>
                <span className="font-mono">http://127.0.0.1:8188</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-secondary)]">状态:</span>
                <span className="text-green-600">● 运行中</span>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
              WebSocket端点
            </label>
            <input
              type="text"
              value="ws://127.0.0.1:8188/ws"
              disabled
              className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg bg-[var(--bg-tertiary)] text-[var(--text-secondary)]"
            />
          </div>
        </div>
      )}

      <div className="flex gap-3 mt-6 pt-4 border-t border-[var(--border-subtle)]">
        <button
          onClick={handleSave}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-[var(--accent-primary)] hover:opacity-90 text-white rounded-lg font-medium"
        >
          <Save className="w-4 h-4" />
          保存设置
        </button>
        <button
          onClick={handleReset}
          className="px-4 py-2 border border-[var(--border-default)] hover:bg-[var(--bg-tertiary)] text-[var(--text-secondary)] rounded-lg font-medium"
        >
          重置
        </button>
      </div>
    </div>
  );
}
