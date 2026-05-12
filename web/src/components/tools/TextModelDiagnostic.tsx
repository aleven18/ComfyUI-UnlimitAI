import { useState } from 'react';

const API_BASE_URL = 'https://api.unlimitai.org';

const TEST_MODELS = [
  { id: 'gpt-4o', name: 'GPT-4o', tier: 'professional' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', tier: 'fast' },
  { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', tier: 'standard' },
  { id: 'deepseek-chat', name: 'DeepSeek Chat', tier: 'standard' },
  { id: 'qwen-max', name: 'Qwen Max', tier: 'professional' },
  { id: 'qwen-plus', name: 'Qwen Plus', tier: 'standard' },
  { id: 'qwen-turbo', name: 'Qwen Turbo', tier: 'fast' }
];

interface TestResult {
  model: string;
  available: boolean;
  error?: string;
  responseTime?: number;
}

export function TextModelDiagnostic() {
  const [testing, setTesting] = useState(false);
  const [results, setResults] = useState<TestResult[]>([]);
  const [currentModel, setCurrentModel] = useState<string>('');

  const testModel = async (modelId: string): Promise<TestResult> => {
    const apiKey = localStorage.getItem('unlimitai_api_key');
    
    if (!apiKey) {
      return {
        model: modelId,
        available: false,
        error: '未配置API Key'
      };
    }

    const startTime = Date.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/v1/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: modelId,
          messages: [{ role: 'user', content: 'test' }],
          max_tokens: 5
        })
      });

      const responseTime = Date.now() - startTime;

      if (response.ok) {
        return {
          model: modelId,
          available: true,
          responseTime
        };
      }

      const error = await response.json();
      
      return {
        model: modelId,
        available: false,
        error: error.error?.message?.substring(0, 80) || `HTTP ${response.status}`,
        responseTime
      };

    } catch (error: unknown) {
      return {
        model: modelId,
        available: false,
        error: (error instanceof Error ? error.message : String(error)) || '请求失败',
        responseTime: Date.now() - startTime
      };
    }
  };

  const runTests = async () => {
    setTesting(true);
    setResults([]);

    for (const model of TEST_MODELS) {
      setCurrentModel(model.name);
      
      if (results.length > 0) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      const result = await testModel(model.id);
      setResults(prev => [...prev, result]);
    }

    setCurrentModel('');
    setTesting(false);
  };

  const availableModels = results.filter(r => r.available);
  const unavailableModels = results.filter(r => !r.available);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">文本模型诊断工具</h3>
        <p className="text-sm text-[var(--text-secondary)]">
          测试你的API账户可以访问哪些文本生成模型
        </p>
        <div className="text-xs text-green-500 mt-2 space-y-1">
          <p>✓ 已验证可用：GPT-4o, GPT-4o Mini, GPT-4 Turbo</p>
          <p>✓ 已验证可用：DeepSeek Chat, Qwen Max/Plus/Turbo</p>
        </div>
      </div>

      <button
        onClick={runTests}
        disabled={testing}
        className="w-full py-3 px-4 bg-[var(--primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
      >
        {testing ? `正在测试: ${currentModel}...` : '开始诊断'}
      </button>

      {testing && (
        <div className="text-center text-sm text-[var(--text-secondary)]">
          测试中，请稍候... (可能需要1-2分钟)
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          {availableModels.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-green-500 mb-2">
                ✅ 可用模型 ({availableModels.length})
              </h4>
              <div className="space-y-2">
                {availableModels.map(result => {
                  const model = TEST_MODELS.find(m => m.id === result.model);
                  return (
                    <div
                      key={result.model}
                      className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg"
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-medium">{model?.name}</div>
                          <div className="text-xs text-[var(--text-secondary)]">
                            等级: {model?.tier} · 响应时间: {result.responseTime}ms
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {unavailableModels.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-red-500 mb-2">
                ❌ 不可用模型 ({unavailableModels.length})
              </h4>
              <div className="space-y-2">
                {unavailableModels.map(result => {
                  const model = TEST_MODELS.find(m => m.id === result.model);
                  return (
                    <div
                      key={result.model}
                      className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg"
                    >
                      <div className="font-medium">{model?.name}</div>
                      <div className="text-xs text-red-400 mt-1">
                        {result.error}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="text-xs text-[var(--text-secondary)] p-3 bg-[var(--bg-tertiary)] rounded-lg">
        <strong>说明：</strong>此工具会向你的API账户发送测试请求来验证模型可用性。
        每个模型测试间隔1秒，避免触发速率限制。
      </div>
    </div>
  );
}
