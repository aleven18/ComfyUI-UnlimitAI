import { useState } from 'react';
import { Key, Eye, EyeOff, ArrowRight, AlertCircle } from 'lucide-react';

interface ApiKeyLoginProps {
  onLogin: (apiKey: string) => void;
  initialKey?: string;
}

export function ApiKeyLogin({ onLogin, initialKey = '' }: ApiKeyLoginProps) {
  const [apiKey, setApiKey] = useState(initialKey);
  const [showKey, setShowKey] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const trimmed = apiKey.trim();
    if (!trimmed) {
      setError('请输入 API Key');
      return;
    }

    setLoading(true);
    try {
      onLogin(trimmed);
    } catch (err: any) {
      setError(err.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[var(--bg-tertiary)] rounded-2xl mb-4">
            <Key className="w-8 h-8 text-[var(--accent-primary)]" />
          </div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)]">ComfyUI-UnlimitAI</h1>
          <p className="mt-2 text-[var(--text-secondary)]">小说转漫剧 · AI驱动的多模态创作工具</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-[var(--bg-elevated)] rounded-2xl shadow-lg p-8 border border-[var(--border-default)]">
          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">配置 API Key</h2>
          <p className="text-sm text-[var(--text-secondary)] mb-6">
            输入您的 UnlimitAI API Key 以开始使用。密钥将安全保存在本地浏览器中。
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
                API Key
              </label>
              <div className="relative">
                <input
                  type={showKey ? 'text' : 'password'}
                  value={apiKey}
                  onChange={(e) => {
                    setApiKey(e.target.value);
                    setError(null);
                  }}
                  placeholder="sk-..."
                  autoFocus
                  className="w-full px-4 py-3 pr-12 bg-[var(--bg-tertiary)] border border-[var(--border-default)] rounded-xl focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-[var(--accent-primary)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)]"
                />
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]"
                >
                  {showKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="flex items-start gap-2 p-3 bg-[var(--accent-error)] bg-opacity-10 rounded-lg border border-[var(--accent-error)] border-opacity-30">
                <AlertCircle className="w-5 h-5 text-[var(--accent-error)] flex-shrink-0 mt-0.5" />
                <p className="text-sm text-[var(--accent-error)]">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !apiKey.trim()}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-[var(--accent-primary)] hover:brightness-110 disabled:bg-[var(--bg-tertiary)] disabled:text-[var(--text-tertiary)] disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all"
            >
              {loading ? (
                <span className="inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>进入工作台</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>

          <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
            <p className="text-xs text-[var(--text-tertiary)] text-center">
              还没有 API Key？请访问{' '}
              <a
                href="https://unlimitai.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--accent-primary)] hover:text-[var(--accent-secondary)] underline"
              >
                unlimitai.com
              </a>
              {' '}获取
            </p>
          </div>
        </form>

        <p className="mt-6 text-center text-xs text-[var(--text-tertiary)]">
          Powered by ComfyUI & UnlimitAI API
        </p>
      </div>
    </div>
  );
}
