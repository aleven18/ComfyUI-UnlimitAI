import { useState } from 'react';
import { useAppStore } from '@/store';
import { useProjectStore } from '@/store/projectStore';
import { STORYBOARD_TEMPLATES, getTemplateById } from '@/data/storyboard-templates';
import { StoryboardSegment, StoryboardTemplate } from '@/types';
import {
  Film, Sparkles, RotateCcw, Lightbulb,
  UserCircle, Camera, Eye, Image, Video, Wand2, CheckCircle2, Loader2,
  Mic, Music, ChevronDown, ChevronUp,
} from 'lucide-react';
import { WorkflowManager } from '@/lib/workflow-manager';
import { getApiKey } from '@/lib/unified-config';

function newSegId() { return `seg_${crypto.randomUUID()}`; }

function makeSegmentsFromTemplate(tpl: StoryboardTemplate, useExample: boolean): StoryboardSegment[] {
  const src = useExample ? tpl.example.segments : tpl.segments;
  return src.map((s) => ({ id: newSegId(), prompt: s.prompt, duration: s.duration }));
}

const STEP_LABELS = [
  { label: '角色与故事分析', icon: Eye, desc: 'LLM 分析角色图与故事描述' },
  { label: '生成视频脚本', icon: Wand2, desc: '生成逐段视频提示词与对白' },
  { label: '生成参考图', icon: Image, desc: 'AI 生成场景设定图' },
  { label: '生成对白音频', icon: Mic, desc: 'TTS 合成角色对白' },
  { label: '生成故事板视频', icon: Video, desc: '合成连贯的故事板视频' },
  { label: '音视频混合', icon: Film, desc: 'ffmpeg 混合视频+对白' },
];

interface StoryboardPanelProps {
  onGenerate?: () => void;
  isConverting?: boolean;
  progress?: number;
  currentNode?: string | null;
  logs?: string[];
  error?: string | null;
}

export function StoryboardPanel({ onGenerate, isConverting, progress = 0, currentNode, logs = [], error }: StoryboardPanelProps) {
  const { storyboard, setStoryboard, result, outputs } = useAppStore();
  const { characters } = useProjectStore();
  const [showExamples, setShowExamples] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showResult, setShowResult] = useState(true);
  const [masterPromptExpanded, setMasterPromptExpanded] = useState(false);

  const canGenerate = storyboard.storyDescription.trim().length > 0 && !isConverting;

  const update = (patch: Partial<typeof storyboard>) => setStoryboard({ ...storyboard, ...patch });

  const currentStepIdx = isConverting ? Math.min(5, Math.floor(progress * 6 / 100)) : -1;

  const applyTemplate = (tpl: StoryboardTemplate, useExample: boolean) => {
    update({
      storyDescription: useExample ? tpl.example.description : tpl.description,
      segments: makeSegmentsFromTemplate(tpl, useExample),
      duration: String(tpl.duration),
      storyboardCount: tpl.segments.length,
      selectedTemplateId: tpl.id,
    });
    setShowExamples(null);
  };

  const toggleCharacterImage = (url: string) => {
    const urls = storyboard.characterImageUrls;
    if (urls.includes(url)) {
      update({ characterImageUrls: urls.filter((u) => u !== url) });
    } else {
      update({ characterImageUrls: [...urls, url] });
    }
  };

  const estimatedCost = WorkflowManager.estimateStoryboardProCost(storyboard);
  const effectiveKey = getApiKey() || '';
  const validationErrors = effectiveKey ? WorkflowManager.validateStoryboardPro(effectiveKey, storyboard) : [];

  const storyboardImageUrl = outputs?.find((o: any) => o.type === 'STRING' && o.url)?.url
    || outputs?.find((o: any) => o.filename?.includes('storyboard_image'))?.url;
  const masterPromptText = outputs?.find((o: any) => o.filename?.includes('master_prompt'))?.url;
  const dialogueTextOutput = outputs?.find((o: any) => o.filename?.includes('dialogue_text'))?.url;
  const videoPromptsOutput = outputs?.find((o: any) => o.filename?.includes('video_prompts'))?.url;
  const hasResult = result?.status === 'completed' && outputs?.length > 0;

  return (
    <div className="space-y-6">
      {isConverting && (
        <div className="card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Film className="w-5 h-5 text-[var(--accent-primary)]" />
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">生成进度</h2>
            <span className="ml-auto text-sm text-[var(--text-secondary)]">{progress.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-[var(--bg-tertiary)] rounded-full h-2 mb-4">
            <div
              className="bg-[var(--accent-primary)] h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
            {STEP_LABELS.map((step, i) => {
              const StepIcon = step.icon;
              const isComplete = isConverting ? i < currentStepIdx : false;
              const isCurrent = isConverting && i === currentStepIdx;
              return (
                <div key={i} className={`flex flex-col items-center gap-1.5 p-3 rounded-lg transition-all ${
                  isCurrent ? 'bg-[var(--accent-primary)] bg-opacity-10 border border-[var(--accent-primary)] border-opacity-50' :
                  isComplete ? 'bg-[var(--accent-success)] bg-opacity-5' :
                  'opacity-50'
                }`}>
                  {isComplete ? (
                    <CheckCircle2 className="w-5 h-5 text-[var(--accent-success)]" />
                  ) : isCurrent ? (
                    <Loader2 className="w-5 h-5 text-[var(--accent-primary)] animate-spin" />
                  ) : (
                    <StepIcon className="w-5 h-5 text-[var(--text-tertiary)]" />
                  )}
                  <span className={`text-xs font-medium text-center ${
                    isCurrent ? 'text-[var(--accent-primary)]' :
                    isComplete ? 'text-[var(--accent-success)]' :
                    'text-[var(--text-tertiary)]'
                  }`}>
                    {step.label}
                  </span>
                  <span className="text-[10px] text-[var(--text-tertiary)] text-center">{step.desc}</span>
                </div>
              );
            })}
          </div>
          {logs.length > 0 && (
            <div className="mt-4 max-h-32 overflow-y-auto space-y-1">
              {logs.slice(-5).map((log, i) => (
                <p key={i} className="text-xs text-[var(--text-tertiary)]">{log}</p>
              ))}
            </div>
          )}
          {error && (
            <div className="mt-3 p-3 bg-[var(--accent-error)] bg-opacity-10 border border-[var(--accent-error)] border-opacity-30 rounded-lg text-sm text-[var(--accent-error)]">
              {error}
            </div>
          )}
        </div>
      )}

      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-[var(--accent-warning)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">快捷模板</h2>
          <span className="text-xs text-[var(--text-tertiary)]">点击预填故事描述</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {STORYBOARD_TEMPLATES.map((tpl) => {
            const selected = storyboard.selectedTemplateId === tpl.id;
            return (
              <div key={tpl.id} className="relative">
                <button
                  onClick={() => applyTemplate(tpl, false)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selected
                      ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)] bg-opacity-10'
                      : 'border-[var(--border-default)] hover:border-[var(--accent-primary)] hover:border-opacity-50'
                  }`}
                >
                  <div className="text-2xl mb-2">{tpl.icon}</div>
                  <div className="font-medium text-sm text-[var(--text-primary)]">{tpl.name}</div>
                  <div className="text-xs text-[var(--text-tertiary)] mt-1">{tpl.segments.length} 段 · {tpl.duration}s</div>
                </button>
                <button
                  onClick={() => setShowExamples(showExamples === tpl.id ? null : tpl.id)}
                  className="absolute top-2 right-2 p-1 rounded-full bg-[var(--bg-elevated)] shadow-sm hover:bg-[var(--bg-hover)]"
                  title="查看案例"
                >
                  <Lightbulb className="w-3.5 h-3.5 text-[var(--accent-warning)]" />
                </button>
              </div>
            );
          })}
        </div>

        {showExamples && (() => {
          const tpl = getTemplateById(showExamples);
          if (!tpl) return null;
          return (
            <div className="mt-4 p-4 bg-[var(--accent-warning)] bg-opacity-10 rounded-lg border border-[var(--accent-warning)] border-opacity-30">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-[var(--text-primary)]">{tpl.icon} {tpl.example.title}</h3>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">{tpl.example.description}</p>
                </div>
                <button
                  onClick={() => applyTemplate(tpl, true)}
                  className="btn-primary whitespace-nowrap"
                >
                  使用此案例
                </button>
              </div>
              <p className="text-xs text-[var(--text-tertiary)] italic">{tpl.example.thumbnailTip}</p>
            </div>
          );
        })()}
      </div>

      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Film className="w-5 h-5 text-[var(--accent-primary)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">故事描述</h2>
        </div>
        <p className="text-xs text-[var(--text-tertiary)] mb-3">
          用一句话描述你想生成的故事，AI 将自动分析角色、生成脚本、创建分镜图和视频。
        </p>
        <textarea
          value={storyboard.storyDescription}
          onChange={(e) => update({ storyDescription: e.target.value })}
          placeholder="例如：一只小狐狸误入黑暗魔法森林，在星光精灵的帮助下找到回家的路..."
          rows={3}
          maxLength={500}
          className="input-base resize-y"
        />
        <div className="flex justify-between items-center mt-1">
          <span className={`text-xs ${storyboard.storyDescription.length > 500 ? 'text-[var(--accent-error)]' : 'text-[var(--text-tertiary)]'}`}>
            {storyboard.storyDescription.length}/500
          </span>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <UserCircle className="w-5 h-5 text-[var(--accent-primary)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">角色一致性</h2>
          <span className="text-xs text-[var(--text-tertiary)]">可选 · 让 AI 看图分析角色</span>
        </div>
        <p className="text-xs text-[var(--text-tertiary)] mb-4">
          选择角色卡作为参考图，LLM 将分析角色外观并确保视频中角色一致。支持多角色，生成分镜图时使用第一个角色作为参考。
        </p>
        <div className="space-y-4">
          {characters.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">从角色卡选择</label>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {characters.map((c) => {
                  const imgUrl = c.appearance.referenceImage;
                  const selected = imgUrl && storyboard.characterImageUrls.includes(imgUrl);
                  return (
                    <button
                      key={c.id}
                      onClick={() => imgUrl && toggleCharacterImage(imgUrl)}
                      disabled={!imgUrl}
                      className={`flex items-center gap-2 p-2 rounded-lg border transition-all text-left ${
                        selected
                          ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)] bg-opacity-10'
                          : 'border-[var(--border-default)] hover:border-[var(--accent-primary)] hover:border-opacity-50'
                      } ${!imgUrl ? 'opacity-40 cursor-not-allowed' : ''}`}
                    >
                      {imgUrl ? (
                        <img src={imgUrl} alt={c.name} className="w-8 h-8 rounded object-cover flex-shrink-0" />
                      ) : (
                        <div className="w-8 h-8 rounded bg-[var(--bg-tertiary)] flex items-center justify-center flex-shrink-0">
                          <UserCircle className="w-4 h-4 text-[var(--text-tertiary)]" />
                        </div>
                      )}
                      <div className="min-w-0">
                        <p className="text-xs font-medium text-[var(--text-primary)] truncate">{c.name}</p>
                        <p className="text-[10px] text-[var(--text-tertiary)] truncate">{imgUrl ? '点击选择' : '无参考图'}</p>
                      </div>
                      {selected && <CheckCircle2 className="w-4 h-4 text-[var(--accent-primary)] flex-shrink-0 ml-auto" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
          {storyboard.characterImageUrls.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">已选择的角色参考图</label>
              <div className="flex flex-wrap gap-2">
                {storyboard.characterImageUrls.map((url, i) => (
                  <div key={i} className="relative group">
                    <img src={url} alt={`角色 ${i + 1}`} className="w-16 h-16 rounded-lg object-cover border border-[var(--border-default)]" />
                    <button
                      onClick={() => toggleCharacterImage(url)}
                      className="absolute -top-1 -right-1 w-5 h-5 bg-[var(--accent-error)] rounded-full text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      &times;
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">一致性模式</label>
              <select
                value={storyboard.imageReference}
                onChange={(e) => update({ imageReference: e.target.value as 'subject' | 'face' })}
                className="input-base"
              >
                <option value="subject">主体一致 - 保持角色整体外观</option>
                <option value="face">面部一致 - 仅保持面部特征</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                参考图强度: {storyboard.imageFidelity}
              </label>
              <input
                type="range" min="0" max="1" step="0.01"
                value={storyboard.imageFidelity}
                onChange={(e) => update({ imageFidelity: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Camera className="w-5 h-5 text-[var(--accent-primary)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">模型选择</h2>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">文本模型</label>
            <select
              value={storyboard.textModel}
              onChange={(e) => update({ textModel: e.target.value })}
              className="input-base"
            >
              <option value="gpt-4o">GPT-4o (推荐)</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
              <option value="deepseek-chat">DeepSeek Chat</option>
              <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
            </select>
            <p className="text-[10px] text-[var(--text-tertiary)] mt-1">用于分析角色和生成脚本</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">图像模型</label>
            <select
              value={storyboard.imageModel}
              onChange={(e) => update({ imageModel: e.target.value })}
              className="input-base"
            >
              <option value="kling-v2">Kling V2</option>
              <option value="kling-v3">Kling V3</option>
              <option value="flux-pro">Flux Pro</option>
              <option value="gpt-image">GPT Image</option>
            </select>
            <p className="text-[10px] text-[var(--text-tertiary)] mt-1">用于生成分镜画面</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">视频模型</label>
            <select
              value={storyboard.videoModel}
              onChange={(e) => update({ videoModel: e.target.value })}
              className="input-base"
            >
              <option value="kling-v2-master">Kling V2 Master</option>
              <option value="kling-v2-1-master">Kling V2.1 Master</option>
              <option value="kling-v2-5-turbo">Kling V2.5 Turbo</option>
              <option value="kling-v3">Kling V3</option>
            </select>
            <p className="text-[10px] text-[var(--text-tertiary)] mt-1">用于生成故事板视频</p>
          </div>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Camera className="w-5 h-5 text-[var(--accent-primary)]" />
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">视频设置</h2>
          </div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-xs px-3 py-1 bg-[var(--bg-tertiary)] hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] rounded-lg"
          >
            {showAdvanced ? '收起高级' : '展开高级'}
          </button>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">分镜数</label>
            <select
              value={storyboard.storyboardCount}
              onChange={(e) => update({ storyboardCount: parseInt(e.target.value) })}
              className="input-base"
            >
              {[2, 3, 4, 5, 6].map((n) => {
                const dur = parseInt(storyboard.duration);
                const disabled = (dur === 5 && n > 3) || (dur === 10 && n > 5);
                return (
                  <option key={n} value={n} disabled={disabled}>
                    {n} 段{disabled ? ` (时长不足)` : ''}
                  </option>
                );
              })}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">画质</label>
            <select
              value={storyboard.mode}
              onChange={(e) => update({ mode: e.target.value })}
              className="input-base"
            >
              <option value="std">标准 (720p)</option>
              <option value="pro">高清 (1080p)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">画面比例</label>
            <select
              value={storyboard.aspectRatio}
              onChange={(e) => update({ aspectRatio: e.target.value })}
              className="input-base"
            >
              <option value="16:9">16:9 横屏</option>
              <option value="9:16">9:16 竖屏</option>
              <option value="1:1">1:1 方形</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">总时长</label>
            <select
              value={storyboard.duration}
              onChange={(e) => {
                const dur = e.target.value;
                const count = storyboard.storyboardCount;
                const maxCount = dur === '5' ? 3 : 5;
                update({ duration: dur, storyboardCount: Math.min(count, maxCount) });
              }}
              className="input-base"
            >
              <option value="5">5 秒</option>
              <option value="10">10 秒</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">环境音</label>
            <select
              value={storyboard.sound}
              onChange={(e) => update({ sound: e.target.value as 'off' | 'on' })}
              className="input-base"
            >
              <option value="off">关闭</option>
              <option value="on">开启</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">对白生成</label>
            <select
              value={storyboard.generateDialogue}
              onChange={(e) => update({ generateDialogue: e.target.value as 'off' | 'on' })}
              className="input-base"
            >
              <option value="off">关闭</option>
              <option value="on">开启</option>
            </select>
          </div>
          {storyboard.generateDialogue === 'on' && (
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">对白声音</label>
              <select
                value={storyboard.voice}
                onChange={(e) => update({ voice: e.target.value })}
                className="input-base"
              >
                <optgroup label="Minimax">
                  <option value="minimax-male-qn-qingse">男声-青涩</option>
                  <option value="minimax-male-qn-jingying">男声-精英</option>
                  <option value="minimax-female-shaonv">女声-少女</option>
                  <option value="minimax-female-yujie">女声-御姐</option>
                  <option value="minimax-presenter_male">男声-主持</option>
                  <option value="minimax-presenter_female">女声-主持</option>
                  <option value="minimax-audiobook_male_1">男声-有声书1</option>
                  <option value="minimax-audiobook_male_2">男声-有声书2</option>
                </optgroup>
                 <optgroup label="Kling">
                   <option value="kling-Binbin">Binbin (彬彬)</option>
                   <option value="kling-Dashu">Dashu (大叔)</option>
                   <option value="kling-Xiaomei">Xiaomei (小美)</option>
                   <option value="kling-Aibo">Aibo (艾博)</option>
                   <option value="kling-Yezi">Yezi (叶子)</option>
                 </optgroup>
              </select>
            </div>
          )}
        </div>

        {showAdvanced && (
          <div className="mt-4 pt-4 border-t border-[var(--border-subtle)] grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                引导强度: {storyboard.cfgScale}
              </label>
              <input
                type="range" min="0" max="1" step="0.1"
                value={storyboard.cfgScale}
                onChange={(e) => update({ cfgScale: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                角色相似度: {storyboard.humanFidelity}
              </label>
              <input
                type="range" min="0" max="1" step="0.01"
                value={storyboard.humanFidelity}
                onChange={(e) => update({ humanFidelity: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">镜头控制</label>
              <select
                value={storyboard.cameraStyle}
                onChange={(e) => update({ cameraStyle: e.target.value as 'none' | 'simple' | 'custom' })}
                className="input-base"
              >
                <option value="none">关闭 — 无镜头控制</option>
                <option value="simple">简单 — 自动映射镜头描述</option>
                <option value="custom">自定义 — LLM 输出数值参数</option>
              </select>
              <p className="text-[10px] text-[var(--text-tertiary)] mt-1">
                simple: 根据文本自动映射; custom: LLM 直接输出数值
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">负面提示词</label>
              <input
                type="text"
                value={storyboard.negativePrompt}
                onChange={(e) => update({ negativePrompt: e.target.value })}
                placeholder="可选，排除不需要的元素"
                className="input-base"
              />
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        <button
          disabled={!canGenerate}
          onClick={onGenerate}
          className="flex-1 btn-primary flex items-center justify-center gap-2 py-3 text-lg"
        >
          <Film className="w-5 h-5" />
          {isConverting ? '生成中...' : '生成故事板视频'}
        </button>
        <button
          onClick={() => {
            update({
              storyDescription: '',
              characterImageUrls: [],
              storyboardCount: 4,
              duration: '5',
              mode: 'std',
              negativePrompt: '',
              sound: 'off',
              selectedTemplateId: null,
              cameraStyle: 'none',
              voice: 'minimax-male-qn-jingying',
              generateDialogue: 'off',
            });
          }}
          className="btn-secondary p-3"
          title="重置"
        >
          <RotateCcw className="w-5 h-5" />
        </button>
      </div>

      {!isConverting && (
        <div className="text-center">
          <span className="text-xs text-[var(--text-tertiary)]">
            预估费用: ~${estimatedCost.toFixed(2)} · {storyboard.storyboardCount} 段分镜 · {storyboard.duration}s · {storyboard.videoModel}
          </span>
        </div>
      )}

      {validationErrors.length > 0 && !isConverting && (
        <div className="p-3 bg-[var(--accent-warning)] bg-opacity-10 border border-[var(--accent-warning)] border-opacity-30 rounded-lg text-sm text-[var(--accent-warning)]">
          {validationErrors.join('；')}
        </div>
      )}

      {hasResult && !isConverting && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-[var(--accent-success)]" />
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">生成结果</h2>
            </div>
            <button
              onClick={() => setShowResult(!showResult)}
              className="text-xs px-3 py-1 bg-[var(--bg-tertiary)] hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] rounded-lg flex items-center gap-1"
            >
              {showResult ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              {showResult ? '收起' : '展开'}
            </button>
          </div>
          {showResult && (
            <div className="space-y-4">
              {outputs?.filter((o: any) => o.type === 'VIDEO').map((o: any, i: number) => (
                <div key={i}>
                  <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">视频</label>
                  {o.url && (
                    <video src={o.url} controls className="w-full rounded-lg border border-[var(--border-default)]" />
                  )}
                </div>
              ))}
              {outputs?.filter((o: any) => o.type === 'AUDIO').map((o: any, i: number) => (
                <div key={`audio-${i}`}>
                  <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                    <Mic className="w-4 h-4 inline mr-1" />对白音频
                  </label>
                  {o.url && (
                    <audio src={o.url} controls className="w-full" />
                  )}
                </div>
              ))}
              {outputs?.filter((o: any) => o.type === 'STRING').map((o: any, i: number) => {
                const label = o.filename?.includes('master_prompt') ? 'Master Prompt (视觉圣经)'
                  : o.filename?.includes('video_prompts') ? '分镜脚本'
                  : o.filename?.includes('dialogue_text') ? '对白文本'
                  : o.filename?.includes('storyboard_image') ? '参考图 URL'
                  : `输出 ${i + 1}`;
                if (o.filename?.includes('storyboard_image') && o.url) {
                  return (
                    <div key={`str-${i}`}>
                      <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                        <Image className="w-4 h-4 inline mr-1" />参考图
                      </label>
                      <img src={o.url} alt="参考图" className="max-w-sm rounded-lg border border-[var(--border-default)]" />
                    </div>
                  );
                }
                if (o.filename?.includes('master_prompt')) {
                  return (
                    <div key={`str-${i}`}>
                      <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Master Prompt (视觉圣经)</label>
                      <div className="relative">
                        <pre className={`text-xs text-[var(--text-secondary)] bg-[var(--bg-tertiary)] p-3 rounded-lg overflow-auto whitespace-pre-wrap ${
                          !masterPromptExpanded ? 'max-h-24' : ''
                        }`}>
                          {o.url || o.filename || '—'}
                        </pre>
                        <button
                          onClick={() => setMasterPromptExpanded(!masterPromptExpanded)}
                          className="text-[10px] text-[var(--accent-primary)] mt-1 hover:underline"
                        >
                          {masterPromptExpanded ? '收起' : '展开全部'}
                        </button>
                      </div>
                    </div>
                  );
                }
                if (o.filename?.includes('dialogue_text')) {
                  return (
                    <div key={`str-${i}`}>
                      <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                        <Mic className="w-4 h-4 inline mr-1" />对白文本
                      </label>
                      <pre className="text-xs text-[var(--text-secondary)] bg-[var(--bg-tertiary)] p-3 rounded-lg overflow-auto whitespace-pre-wrap">
                        {o.url || o.filename || '—'}
                      </pre>
                    </div>
                  );
                }
                return null;
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
