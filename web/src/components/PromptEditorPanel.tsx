import { useState, useEffect } from 'react';
import { Settings, Save, RotateCcw, Eye, Edit3, AlertCircle } from 'lucide-react';

interface PromptConfig {
  name: string;
  description: string;
  template: string;
  variables: string[];
}

const DEFAULT_PROMPTS = {
  storyboard_structure_analysis: {
    name: '故事结构分析',
    description: '分析小说的故事结构和情感曲线',
    template: `{lang_prompt}分析以下小说的故事结构和情感曲线：

小说内容：
{novel_text}

请分析并返回JSON格式：
{
    "title": "故事标题",
    "genre": "类型",
    "main_characters": ["角色列表"],
    "emotional_curve": [
        {"time": "开头", "emotion": "起始情绪", "intensity": 1-10},
        {"time": "发展", "emotion": "发展情绪", "intensity": 1-10},
        {"time": "高潮", "emotion": "高潮情绪", "intensity": 1-10},
        {"time": "结尾", "emotion": "结束情绪", "intensity": 1-10}
    ],
    "key_moments": [
        {"moment": "关键时刻描述", "importance": "high/medium/low", "suggested_duration": "建议时长"}
    ],
    "pacing": "节奏（快/中/慢）",
    "suggested_shot_count": 建议镜头数（整数）
}

只返回JSON，不要其他内容。`,
    variables: ['lang_prompt', 'novel_text']
  },
  storyboard_generation: {
    name: '分镜生成',
    description: '根据小说生成分镜脚本',
    template: `{lang_prompt}为以下小说生成详细的分镜脚本：

小说内容：
{novel_text}

故事结构：
{story_structure}

要求：
1. 风格：{style_guide}
2. 详细程度：{detail_level_guide}
3. 目标总时长：{target_duration}秒
4. 建议镜头数：{suggested_shot_count}个左右

每个镜头包含：
- shot_id: 镜头编号（从1开始）
- scene_number: 所属场景
- shot_type: 景别（大远景/远景/全景/中景/近景/特写/大特写）
- camera_movement: 运镜方式（固定/推/拉/摇/移/跟/升降/环绕）
- angle: 拍摄角度（平视/俯视/仰视/斜角）
- description: 画面内容描述（详细）
- action: 动作描述
- dialogue: 对话或旁白
- sound: 音效建议
- music: 配乐风格
- duration: 时长（秒），根据内容重要性决定（1-15秒）
- transition: 转场方式（切/淡入淡出/溶解/划变）
- emotion: 情绪氛围
- visual_prompt: 用于生成图像的英文提示词（详细，包含场景、人物、动作、光线）

返回JSON格式：
{
    "title": "分镜标题",
    "total_duration": 总时长,
    "shots": [...]
}

注意：
- 合理分配时长，重要场景给更多时长
- 时长总和应接近{target_duration}秒
- 景别和运镜要有变化，避免单调
- 考虑情感曲线，高潮部分节奏加快
- 每个镜头的visual_prompt要详细具体

只返回JSON，不要其他内容。`,
    variables: ['lang_prompt', 'novel_text', 'story_structure', 'style_guide', 'detail_level_guide', 'target_duration', 'suggested_shot_count']
  },
  novel_scene_extraction: {
    name: '小说场景提取',
    description: '从小说中提取关键场景',
    template: `{lang_instruction}分析以下小说文本，提取{num_scenes}个关键场景。

对于每个场景，提供以下信息：
1. scene_number: 场景编号
2. title: 场景标题（简洁）
3. description: 场景描述（详细，包含人物、动作、环境、情感）
4. characters: 出场人物列表
5. mood: 场景氛围（如紧张、温馨、悲伤等）
6. dialogue: 关键对话或内心独白（用于配音）
7. visual_prompt: 用于生成图像的英文提示词（详细，包含场景、人物、动作、光线、风格）
8. camera_movement: 建议的镜头运动（如slow zoom, pan left, close-up等）

小说文本：
{novel_text}

请以JSON数组格式返回场景列表：
[
  {
    "scene_number": 1,
    "title": "场景标题",
    "description": "详细描述...",
    "characters": ["人物1", "人物2"],
    "mood": "氛围",
    "dialogue": "对话内容",
    "visual_prompt": "A detailed English prompt for image generation...",
    "camera_movement": "镜头运动"
  },
  ...
]

只返回JSON数组，不要其他内容。`,
    variables: ['lang_instruction', 'num_scenes', 'novel_text']
  }
};

export function PromptEditorPanel() {
  const [selectedKey, setSelectedKey] = useState<string>('storyboard_generation');
  const [prompts, setPrompts] = useState<Record<string, PromptConfig>>(DEFAULT_PROMPTS);
  const [editingTemplate, setEditingTemplate] = useState<string>('');
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [saveStatus, setSaveStatus] = useState<string>('');

  useEffect(() => {
    const saved = localStorage.getItem('custom_prompts');
    if (saved) {
      try {
        const customPrompts = JSON.parse(saved);
        setPrompts({ ...DEFAULT_PROMPTS, ...customPrompts });
      } catch (e) {
        console.error('加载自定义提示词失败:', e);
      }
    }

    setEditingTemplate(prompts[selectedKey]?.template || '');
  }, [selectedKey]);

  const handleSave = () => {
    try {
      const updated = {
        ...prompts,
        [selectedKey]: {
          ...prompts[selectedKey],
          template: editingTemplate
        }
      };

      setPrompts(updated);

      localStorage.setItem('custom_prompts', JSON.stringify(updated));

      setSaveStatus('✅ 已保存');
      setIsEditing(false);

      setTimeout(() => setSaveStatus(''), 3000);
    } catch (e) {
      setSaveStatus('❌ 保存失败');
    }
  };

  const handleReset = () => {
    if (confirm('确定要重置为默认模板吗？')) {
      const defaultTemplate = DEFAULT_PROMPTS[selectedKey as keyof typeof DEFAULT_PROMPTS]?.template || '';
      setEditingTemplate(defaultTemplate);

      const updated = {
        ...prompts,
        [selectedKey]: {
          ...prompts[selectedKey],
          template: defaultTemplate
        }
      };

      setPrompts(updated);
      localStorage.setItem('custom_prompts', JSON.stringify(updated));
      setSaveStatus('✅ 已重置');
      setTimeout(() => setSaveStatus(''), 3000);
    }
  };

  const currentPrompt = prompts[selectedKey];

  return (
    <div className="bg-[var(--bg-elevated)] rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-[var(--accent-primary)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">系统提示词配置</h2>
        </div>
        {saveStatus && (
          <span className="text-sm text-green-600">{saveStatus}</span>
        )}
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
          选择要编辑的提示词
        </label>
        <select
          value={selectedKey}
          onChange={(e) => {
            setSelectedKey(e.target.value);
            setIsEditing(false);
          }}
          className="w-full px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-[var(--accent-primary)]"
        >
          {Object.entries(prompts).map(([key, config]) => (
            <option key={key} value={key}>
              {config.name} - {config.description}
            </option>
          ))}
        </select>
      </div>

      {currentPrompt && (
        <div className="mb-4 p-3 bg-[var(--bg-tertiary)] rounded-lg">
          <div className="flex items-start gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-blue-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-[var(--text-primary)]">{currentPrompt.name}</p>
              <p className="text-xs text-[var(--text-secondary)]">{currentPrompt.description}</p>
            </div>
          </div>
          <div className="text-xs text-[var(--text-tertiary)]">
            <span className="font-medium">可用变量：</span>
            {currentPrompt.variables.map((v, i) => (
              <code key={i} className="ml-2 px-1 py-0.5 bg-[var(--accent-primary)] bg-opacity-10 text-[var(--accent-primary)] rounded">
                {`{${v}}`}
              </code>
            ))}
          </div>
        </div>
      )}

      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-[var(--text-secondary)]">
            提示词模板
          </label>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="flex items-center gap-1 text-sm text-[var(--accent-primary)] hover:text-[var(--accent-primary)]"
          >
            {isEditing ? <Eye className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
            {isEditing ? '查看模式' : '编辑模式'}
          </button>
        </div>

        {isEditing ? (
          <textarea
            value={editingTemplate}
            onChange={(e) => setEditingTemplate(e.target.value)}
            className="w-full h-96 px-3 py-2 border border-[var(--border-default)] rounded-lg focus:ring-2 focus:ring-[var(--accent-primary)] font-mono text-sm"
            placeholder="输入自定义提示词模板..."
          />
        ) : (
          <div className="w-full h-96 px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-tertiary)] overflow-auto">
            <pre className="font-mono text-sm text-[var(--text-primary)] whitespace-pre-wrap">
              {editingTemplate}
            </pre>
          </div>
        )}
      </div>

      <div className="flex gap-3">
        <button
          onClick={handleSave}
          disabled={!isEditing}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            isEditing
              ? 'bg-[var(--accent-primary)] hover:opacity-90 text-white'
              : 'bg-[var(--bg-tertiary)] text-[var(--text-tertiary)] cursor-not-allowed'
          }`}
        >
          <Save className="w-4 h-4" />
          保存配置
        </button>
        <button
          onClick={handleReset}
          className="flex items-center justify-center gap-2 px-4 py-2 border border-[var(--border-default)] hover:bg-[var(--bg-tertiary)] text-[var(--text-secondary)] rounded-lg font-medium"
        >
          <RotateCcw className="w-4 h-4" />
          重置默认
        </button>
      </div>

      <div className="mt-6 p-4 bg-[var(--accent-primary)] bg-opacity-5 rounded-lg border border-[var(--accent-primary)] border-opacity-30">
        <h3 className="text-sm font-medium text-[var(--accent-primary)] mb-2">使用说明</h3>
        <ul className="text-xs text-[var(--accent-primary)] space-y-1">
          <li>• 选择要编辑的提示词类型</li>
          <li>• 点击"编辑模式"进入编辑状态</li>
          <li>• 使用 <code className="px-1 bg-[var(--accent-primary)] bg-opacity-10 rounded">{'{变量名}'}</code> 作为占位符</li>
          <li>• 修改后点击"保存配置"</li>
          <li>• 配置保存在浏览器本地存储中</li>
          <li>• 点击"重置默认"可恢复原始模板</li>
        </ul>
      </div>

      <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
        <h3 className="text-sm font-medium text-yellow-800 mb-2">自定义示例</h3>
        <div className="text-xs text-yellow-700 space-y-2">
          <div>
            <p className="font-medium">动漫风格：</p>
            <code className="block mt-1 p-2 bg-yellow-100 rounded text-xs">
              {`风格要求：日系动漫风格
- 多使用特写镜头表现表情
- 动作夸张流畅
- 色彩鲜艳
- 注重情感表现`}
            </code>
          </div>
          <div>
            <p className="font-medium">简化输出：</p>
            <code className="block mt-1 p-2 bg-yellow-100 rounded text-xs">
              {`只返回核心字段：
- shot_id
- description
- duration
- visual_prompt`}
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}
