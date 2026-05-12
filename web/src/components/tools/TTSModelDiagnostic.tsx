import { useState } from 'react';

const API_BASE_URL = 'https://api.unlimitai.org';

const TEST_MODELS = [
  { id: 'tts-1', name: 'OpenAI TTS-1', description: 'OpenAI 快速生成' },
  { id: 'tts-1-hd', name: 'OpenAI TTS-1 HD', description: 'OpenAI 高清音质' },
  { id: 'minimax', name: 'Minimax TTS', description: 'Minimax 中文语音' }
];

interface TestResult {
  model: string;
  available: boolean;
  error?: string;
  responseTime?: number;
}

export function TTSModelDiagnostic() {
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
      const response = await fetch(`${API_BASE_URL}/v1/audio/speech`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: modelId,
          input: '测试语音合成',
          voice: 'minimax-male-qn-jingying'
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
        <h3 className="text-lg font-semibold mb-2">TTS语音合成模型诊断工具</h3>
        <p className="text-sm text-[var(--text-secondary)]">
          测试你的API账户可以访问哪些语音合成模型
        </p>
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
          测试中，请稍候... (可能需要1分钟)
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
                            {model?.description} · 响应时间: {result.responseTime}ms
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
        <strong>说明：</strong>此工具会向你的API账户发送测试请求来验证语音合成模型可用性。
        每个模型测试间隔1秒，避免触发速率限制。
      </div>
    </div>
  );
}
