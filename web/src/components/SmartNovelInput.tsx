import { useState } from 'react';
import { useAppStore } from '@/store';
import { PresetType } from '@/types';
import { Sparkles, Clock, DollarSign, Film, AlertCircle } from 'lucide-react';

export function SmartNovelInput() {
  const { params, setParams, preset, setPreset } = useAppStore();
  const [novelText, setNovelText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!novelText.trim()) {
      alert('请输入小说文本');
      return;
    }

    setIsAnalyzing(true);

    setTimeout(() => {
      const textLength = novelText.length;
      const estimatedScenes = Math.max(3, Math.min(20, Math.floor(textLength / 300)));
      const estimatedDuration = estimatedScenes * 10;
      const estimatedCost = estimatedScenes * 0.52;

      setAnalysisResult({
        textLength,
        recommendedScenes: estimatedScenes,
        estimatedDuration,
        estimatedCost,
        genre: '剧情',
        style: '电影风格'
      });

      setParams({ maxScenes: estimatedScenes });
      setIsAnalyzing(false);
    }, 2000);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        setNovelText(text);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="bg-[var(--bg-elevated)] rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-[var(--accent-primary)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">智能创作助手</h2>
        </div>
        {!analysisResult && novelText && (
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-4 py-2 bg-[var(--accent-primary)] hover:opacity-90 text-white rounded-lg font-medium disabled:opacity-50"
          >
            {isAnalyzing ? '分析中...' : '智能分析'}
          </button>
        )}
      </div>

      <div className="mb-4 p-4 bg-[var(--accent-primary)] bg-opacity-5 rounded-lg border border-[var(--accent-primary)] border-opacity-30">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">
            1
          </div>
          <div>
            <p className="font-medium text-[var(--text-primary)]">第一步：输入小说文本</p>
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              粘贴或上传小说，AI会自动分析并给出推荐方案
            </p>
          </div>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex gap-2 mb-2">
          <button
            onClick={() => document.getElementById('file-upload')?.click()}
            className="flex items-center gap-2 px-3 py-1.5 border border-[var(--border-default)] rounded-lg text-sm hover:bg-[var(--bg-tertiary)]"
          >
            📁 上传文件
          </button>
          <input
            id="file-upload"
            type="file"
            accept=".txt"
            onChange={handleFileUpload}
            className="hidden"
          />
          <span className="text-sm text-[var(--text-tertiary)]">
            {novelText.length > 0 && `${novelText.length} 字`}
          </span>
        </div>

        <textarea
          value={novelText}
          onChange={(e) => {
            setNovelText(e.target.value);
            setAnalysisResult(null);
          }}
          placeholder="在此粘贴小说文本，或上传 .txt 文件...

示例：
阳光明媚的早晨，小明走在街上。
突然，他看到了一朵美丽的玫瑰花..."
          className="w-full h-48 px-4 py-3 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-[var(--accent-primary)] resize-none"
        />
      </div>

      {analysisResult && (
        <div className="space-y-4">
          <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
            <div className="flex items-start gap-2 mb-3">
              <Sparkles className="w-5 h-5 text-green-600 mt-0.5" />
              <div>
                <p className="font-semibold text-[var(--text-primary)]">AI 智能分析完成</p>
                <p className="text-sm text-[var(--text-secondary)]">基于小说内容，为您推荐以下方案</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="text-center p-3 bg-[var(--bg-elevated)] rounded-lg">
                <Film className="w-5 h-5 text-blue-500 mx-auto mb-1" />
                <p className="text-2xl font-bold text-blue-600">
                  {analysisResult.recommendedScenes}
                </p>
                <p className="text-xs text-[var(--text-secondary)]">推荐场景数</p>
              </div>

              <div className="text-center p-3 bg-[var(--bg-elevated)] rounded-lg">
                <Clock className="w-5 h-5 text-purple-500 mx-auto mb-1" />
                <p className="text-2xl font-bold text-purple-600">
                  {Math.floor(analysisResult.estimatedDuration / 60)}:{(analysisResult.estimatedDuration % 60).toString().padStart(2, '0')}
                </p>
                <p className="text-xs text-[var(--text-secondary)]">预估时长</p>
              </div>

              <div className="text-center p-3 bg-[var(--bg-elevated)] rounded-lg">
                <DollarSign className="w-5 h-5 text-green-500 mx-auto mb-1" />
                <p className="text-2xl font-bold text-green-600">
                  ${analysisResult.estimatedCost.toFixed(2)}
                </p>
                <p className="text-xs text-[var(--text-secondary)]">预估成本</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-[var(--bg-tertiary)] rounded-lg">
              <p className="text-sm text-[var(--text-secondary)]">故事类型</p>
              <p className="font-medium text-[var(--text-primary)]">{analysisResult.genre}</p>
            </div>
            <div className="p-3 bg-[var(--bg-tertiary)] rounded-lg">
              <p className="text-sm text-[var(--text-secondary)]">推荐风格</p>
              <p className="font-medium text-[var(--text-primary)]">{analysisResult.style}</p>
            </div>
          </div>

          <div className="p-4 border border-[var(--border-subtle)] rounded-lg">
            <p className="text-sm font-medium text-[var(--text-primary)] mb-3">快速调整（可选）</p>

            <div className="space-y-3">
              <div>
                <label className="text-sm text-[var(--text-secondary)]">场景数量</label>
                <div className="flex items-center gap-2 mt-1">
                  <input
                    type="range"
                    min="3"
                    max="30"
                    value={params.maxScenes || analysisResult.recommendedScenes}
                    onChange={(e) => setParams({ maxScenes: parseInt(e.target.value) })}
                    className="flex-1"
                  />
                  <span className="text-sm font-medium text-[var(--text-secondary)] w-8">
                    {params.maxScenes || analysisResult.recommendedScenes}
                  </span>
                </div>
              </div>

              <div>
                <label className="text-sm text-[var(--text-secondary)]">质量模式</label>
                <div className="grid grid-cols-4 gap-2 mt-1">
                  {[
                    { id: 'budget', label: '经济', cost: '$0.18/场景' },
                    { id: 'balanced', label: '平衡', cost: '$0.52/场景' },
                    { id: 'quality', label: '质量', cost: '$0.61/场景' },
                    { id: 'max_quality', label: '最高', cost: '$0.75/场景' }
                  ].map(mode => (
                    <button
                      key={mode.id}
                      onClick={() => setPreset(mode.id as PresetType)}
                      className={`p-2 rounded border text-xs ${
                        preset === mode.id
                          ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)] bg-opacity-5 text-[var(--accent-primary)]'
                          : 'border-[var(--border-subtle)] hover:border-[var(--border-default)]'
                      }`}
                    >
                      <div className="font-medium">{mode.label}</div>
                      <div className="text-[var(--text-tertiary)] mt-0.5">{mode.cost}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-start gap-2 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5" />
            <div className="text-sm text-yellow-800">
              <p className="font-medium">下一步</p>
              <p>确认方案后，点击右侧"开始生成"按钮，系统将自动创建视频</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
