import { useState, useEffect } from 'react';
import { ProjectList } from '@/components/project/ProjectList';
import { ProjectDetail } from '@/components/project/ProjectDetail';
import { Logo } from '@/components/Logo';
import { GlobalSettingsModal } from '@/components/common/GlobalSettingsModal';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { saveGlobalApiKey, clearGlobalApiKey } from '@/lib/unified-config';
import { eventBus, Events } from '@/lib/event-bus';
import { Key, Eye, EyeOff, ArrowRight, AlertCircle } from 'lucide-react';

interface UserInfo {
  id: number;
  username: string;
  display_name: string;
  email: string;
  quota: number;
  used_quota: number;
  request_count: number;
  status: number;
}

interface TokenInfo {
  id: number;
  key: string;
  status: number;
  name: string;
  used_quota: number;
  remain_quota: number;
  expired_time: number;
  unlimited_quota: boolean;
}

export function App() {
  const [isDark, setIsDark] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [showUserPanel, setShowUserPanel] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [tokens, setTokens] = useState<TokenInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDark(savedTheme === 'dark');
    }
    
    const savedApiKey = localStorage.getItem('unlimitai_api_key');
    if (savedApiKey) {
      setApiKey(savedApiKey);
      setIsLoggedIn(true);
      fetchUserInfo(savedApiKey);
    }
    
    const unsubscribe = eventBus.on(Events.OPEN_SETTINGS, () => {
      setShowSettings(true);
    });
    
    return () => {
      unsubscribe();
    };
  }, []);
  
  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);
  
  const toggleTheme = () => {
    setIsDark(!isDark);
  };
  
  const fetchUserInfo = async (key: string) => {
    if (!key) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const usageResponse = await fetch('/api/usage/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key })
      });
      
      if (usageResponse.ok) {
        const usageData = await usageResponse.json();
        if (usageData.success) {
          const tokenInfo = usageData.data;
          setUserInfo({
            id: 0,
            username: tokenInfo.name || '用户',
            display_name: tokenInfo.name || '用户',
            email: '',
            quota: tokenInfo.unlimited_quota ? 999999999 : tokenInfo.total_available,
            used_quota: tokenInfo.total_used,
            request_count: 0,
            status: 1
          });
          
          setTokens([{
            id: 0,
            key: key,
            status: 1,
            name: tokenInfo.name || '默认令牌',
            used_quota: tokenInfo.total_used,
            remain_quota: tokenInfo.unlimited_quota ? 999999999 : tokenInfo.total_available,
            expired_time: 0,
            unlimited_quota: tokenInfo.unlimited_quota
          }]);
        }
      } else {
        setUserInfo({
          id: 0,
          username: '用户',
          display_name: '用户',
          email: '',
          quota: 0,
          used_quota: 0,
          request_count: 0,
          status: 1
        });
      }
    } catch (err) {
      // ignore network errors for balance check
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleLogin = (key: string) => {
    saveGlobalApiKey(key);
    setApiKey(key);
    setIsLoggedIn(true);
    fetchUserInfo(key);
  };
  
  const handleSaveApiKey = () => {
    if (!apiKey) return;
    handleLogin(apiKey);
  };
  
  const handleClearApiKey = () => {
    clearGlobalApiKey();
    setApiKey('');
    setUserInfo(null);
    setTokens([]);
    setShowUserPanel(false);
    setIsLoggedIn(false);
  };
  
  const formatQuota = (quota: number, isUnlimited: boolean = false) => {
    if (isUnlimited) return '∞';
    return (quota / 500000).toFixed(2);
  };

  if (!isLoggedIn) {
    return <ErrorBoundary><ApiKeyLoginPage onLogin={handleLogin} isDark={isDark} /></ErrorBoundary>;
  }
  
  return (
    <div className="h-screen flex flex-col bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <ErrorBoundary>
      <header className="h-12 bg-[var(--bg-primary)] border-b border-[var(--border-subtle)] px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Logo />
          <h1 className="text-sm font-semibold tracking-tight">UnlimitAI</h1>
          {userInfo && (
            <span className="text-xs text-[var(--text-tertiary)] ml-2">
              API余额: ${formatQuota(userInfo.quota, tokens[0]?.unlimited_quota)}
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <button onClick={toggleTheme} className="btn-icon" title={isDark ? '切换到浅色模式' : '切换到深色模式'}>
            {isDark ? (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
              </svg>
            )}
          </button>
          
          <button onClick={() => setShowSettings(true)} className="btn-icon" title="全局设置">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          
          <button onClick={() => setShowUserPanel(true)} className="btn-icon" title="账户信息">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
          </button>
        </div>
      </header>
      
      <div className="flex-1 flex overflow-hidden">
        <ProjectList />
        <ProjectDetail />
      </div>
      
      <GlobalSettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />
      
      {showUserPanel && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 flex items-center justify-center animate-fade-in" onClick={() => setShowUserPanel(false)}>
          <div className="bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-xl shadow-2xl max-w-lg w-[90vw] max-h-[90vh] overflow-auto p-6 animate-scale-in" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold mb-4">账户信息</h2>
            
            {!userInfo ? (
              <div className="space-y-4">
                <p className="text-sm text-[var(--text-secondary)]">输入您的API Key查询余额</p>
                
                {error && (
                  <div className="p-3 bg-[var(--accent-error)] bg-opacity-10 text-[var(--accent-error)] text-sm rounded-lg">
                    {error}
                  </div>
                )}
                
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">API Key</label>
                  <input
                    type="password"
                    placeholder="sk-..."
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="input-base"
                  />
                </div>
                
                <div className="pt-4 flex gap-2">
                  <button onClick={() => setShowUserPanel(false)} className="btn-secondary flex-1">取消</button>
                  <button onClick={handleSaveApiKey} className="btn-primary flex-1">查询余额</button>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="w-8 h-8 border-2 border-[var(--accent-primary)] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                    <p className="text-sm text-[var(--text-secondary)]">加载中...</p>
                  </div>
                ) : (
                  <>
                    <div className="card p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium">{userInfo.display_name || userInfo.username}</h3>
                        <span className="badge">ID: {userInfo.id}</span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="card p-4">
                        <p className="text-xs text-[var(--text-tertiary)] mb-1">账户余额</p>
                        <p className="text-2xl font-bold text-[var(--accent-success)]">
                          ${formatQuota(userInfo.quota, tokens[0]?.unlimited_quota)}
                        </p>
                      </div>
                      <div className="card p-4">
                        <p className="text-xs text-[var(--text-tertiary)] mb-1">已使用</p>
                        <p className="text-2xl font-bold">${formatQuota(userInfo.used_quota)}</p>
                      </div>
                    </div>
                    
                    <div className="card p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-xs text-[var(--text-tertiary)]">用量统计</span>
                        <span className="text-xs text-[var(--text-tertiary)]">
                          {userInfo.quota > 0 ? ((userInfo.used_quota / userInfo.quota) * 100).toFixed(1) : 0}% 已使用
                        </span>
                      </div>
                      <div className="w-full bg-[var(--bg-tertiary)] rounded-full h-2">
                        <div 
                          className="bg-[var(--accent-primary)] h-2 rounded-full transition-all" 
                          style={{ width: `${Math.min(100, userInfo.quota > 0 ? (userInfo.used_quota / userInfo.quota) * 100 : 0)}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div className="pt-4 flex gap-2">
                      <button onClick={handleClearApiKey} className="btn-secondary flex-1">退出登录</button>
                      <button onClick={() => setShowUserPanel(false)} className="btn-primary flex-1">关闭</button>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      )}
      </ErrorBoundary>
    </div>
  );
}

function ApiKeyLoginPage({ onLogin, isDark }: { onLogin: (key: string) => void; isDark: boolean }) {
  const [key, setKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const trimmed = key.trim();
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
          <h1 className="text-3xl font-bold text-[var(--text-primary)]">UnlimitAI</h1>
          <p className="mt-2 text-[var(--text-secondary)]">ComfyUI 多模态创作工具</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-[var(--bg-elevated)] rounded-2xl shadow-lg p-8 border border-[var(--border-default)]">
          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">配置 API Key</h2>
          <p className="text-sm text-[var(--text-secondary)] mb-6">
            输入您的 UnlimitAI API Key 以开始使用。密钥将安全保存在本地浏览器中。
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">API Key</label>
              <div className="relative">
                <input
                  type={showKey ? 'text' : 'password'}
                  value={key}
                  onChange={(e) => { setKey(e.target.value); setError(null); }}
                  placeholder="sk-..."
                  autoFocus
                  className="input-base pr-12"
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
              disabled={loading || !key.trim()}
              className="w-full btn-primary flex items-center justify-center gap-2 py-3 disabled:opacity-40 disabled:cursor-not-allowed"
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
              <a href="https://unlimitai.com" target="_blank" rel="noopener noreferrer" className="text-[var(--accent-primary)] hover:text-[var(--accent-secondary)] underline">
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
