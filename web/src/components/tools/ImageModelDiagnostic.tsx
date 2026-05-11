import { useState } from 'react';

const API_BASE_URL = 'https://api.unlimitai.org';

const TEST_MODELS = [
  { id: 'doubao-seedream-4-0-250828', name: '🫘 豆包 Seedream 4.0', description: '推荐：速度快（11.9秒）' },
  { id: 'gpt-image-1-all', name: '🍌 香蕉 GPT Image All', description: '备用：稳定（13.5秒）' }
];

interface TestResult {
  model: string;
  available: boolean;
  error?: string;
  responseTime?: number;
}

export function ImageModelDiagnostic() {
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
      // 所有可用模型都使用1024x1024尺寸
      const imageSize = '1024x1024';
      
      const response = await fetch(`${API_BASE_URL}/v1/images/generations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: modelId,
          prompt: 'test image',
          n: 1,
          size: imageSize
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
      
      if (response.status === 429) {
        return {
          model: modelId,
          available: false,
          error: '速率限制 (429) - 请稍后再试',
          responseTime
        };
      }

      return {
        model: modelId,
        available: false,
        error: error.error?.message || `HTTP ${response.status}`,
        responseTime
      };

    } catch (error: any) {
      return {
        model: modelId,
        available: false,
        error: error.message || '请求失败',
        responseTime: Date.now() - startTime
      };
    }
  };

  const runTests = async () => {
    setTesting(true);
    setResults([]);

    for (const model of TEST_MODELS) {
      setCurrentModel(model.name);
      
      // 添加延迟避免速率限制
      if (results.length > 0) {
        await new Promise(resolve => setTimeout(resolve, 2000));
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
        <h3 className="text-lg font-semibold mb-2">图像模型诊断工具</h3>
        <p className="text-sm text-[var(--text-secondary)]">
          测试你的API账户可以访问哪些图像生成模型
        </p>
        <p className="text-xs text-green-500 mt-2">
          ✓ 已验证：豆包 Seedream 4.0、Grok 4 Image、DALL-E 3 可用
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
                            {model?.description}
                          </div>
                        </div>
                        <div className="text-xs text-[var(--text-secondary)]">
                          {result.responseTime}ms
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

          {availableModels.length > 0 && (
            <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <h4 className="font-semibold text-blue-400 mb-2">💡 建议</h4>
              <p className="text-sm text-[var(--text-secondary)]">
                你的账户可以使用 {availableModels.length} 个图像生成模型。
                我可以修改系统配置，只使用这些可用的模型。
              </p>
              <button
                onClick={() => {
                  const availableIds = availableModels.map(r => r.model);
                  localStorage.setItem('available_image_models', JSON.stringify(availableIds));
                  alert('配置已保存！系统将只使用可用的模型。');
                }}
                className="mt-3 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm"
              >
                应用配置
              </button>
            </div>
          )}

          {availableModels.length === 0 && !testing && (
            <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <h4 className="font-semibold text-yellow-400 mb-2">⚠️ 问题诊断</h4>
              <div className="text-sm text-[var(--text-secondary)] space-y-2">
                <p>你的API账户当前无法使用任何图像生成模型。</p>
                <p>可能的原因：</p>
                <ul className="list-disc list-inside ml-2 space-y-1">
                  <li>账户余额不足</li>
                  <li>账户分组没有图像生成权限</li>
                  <li>需要开通图像生成服务</li>
                </ul>
                <p className="mt-3">
                  <strong>建议：</strong>联系API提供商开通权限，或使用"上传本地图片"功能。
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="text-xs text-[var(--text-secondary)] p-3 bg-[var(--bg-tertiary)] rounded-lg">
        <strong>说明：</strong>此工具会向你的API账户发送测试请求来验证模型可用性。
        每个模型测试间隔2秒，避免触发速率限制。
      </div>
    </div>
  );
}
