import { useState } from 'react';
import { X, Upload, User, Mic, Sparkles, Loader2, Settings } from 'lucide-react';
import { CharacterCard } from '@/types/project';
import { generateCharacterImage } from '@/lib/image-generation';
import { hasApiKey } from '@/lib/unified-config';
import { eventBus, Events } from '@/lib/event-bus';

interface CharacterEditorProps {
  character: CharacterCard | null;
  onSave: (data: Partial<CharacterCard>) => void;
  onClose: () => void;
}

export function CharacterEditor({ character, onSave, onClose }: CharacterEditorProps) {
  const [activeTab, setActiveTab] = useState<'appearance' | 'voice' | 'personality'>('appearance');
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<Partial<CharacterCard>>({
    name: character?.name || '',
    nickname: character?.nickname || '',
    role: character?.role || 'supporting',
    appearance: {
      referenceImage: character?.appearance.referenceImage || '',
      description: character?.appearance.description || '',
      gender: character?.appearance.gender || 'female',
      age: character?.appearance.age || 25,
      ageRange: character?.appearance.ageRange || 'young_adult',
      distinctiveFeatures: character?.appearance.distinctiveFeatures || []
    },
    voice: {
      engine: character?.voice.engine || 'minimax',
      voiceId: character?.voice.voiceId || '',
      voiceStyle: character?.voice.voiceStyle || 'gentle',
      speechRate: character?.voice.speechRate || 1.0,
      pitch: character?.voice.pitch || 1.0,
      personality: character?.voice.personality || []
    },
    personality: {
      traits: character?.personality.traits || [],
      background: character?.personality.background || '',
      motivation: character?.personality.motivation || '',
      relationships: character?.personality.relationships || []
    },
    consistency: {
      seed: character?.consistency.seed || Math.floor(Math.random() * 1000000),
      style: character?.consistency.style || 'realistic',
      tags: character?.consistency.tags || []
    }
  });
  
  const handleSave = () => {
    onSave(formData);
  };
  
  const handleGenerateImage = async () => {
    if (!hasApiKey()) {
      setGenerateError('请先在右上角设置中配置API Key');
      return;
    }
    
    if (!formData.appearance?.description) {
      setGenerateError('请先填写角色描述');
      return;
    }
    
    setIsGeneratingImage(true);
    setGenerateError(null);
    
    try {
      const prompt = buildCharacterPrompt(formData);
      const imageUrl = await generateCharacterImage(prompt);
      
      setFormData({
        ...formData,
        appearance: { ...formData.appearance!, referenceImage: imageUrl }
      });
    } catch (error: unknown) {
      setGenerateError((error instanceof Error ? error.message : String(error)) || '生成失败');
    } finally {
      setIsGeneratingImage(false);
    }
  };
  
  const buildCharacterPrompt = (data: Partial<CharacterCard>): string => {
    const parts: string[] = [];
    
    if (data.appearance?.description) {
      parts.push(data.appearance.description);
    }
    
    if (data.appearance?.gender) {
      parts.push(data.appearance.gender === 'male' ? 'male' : data.appearance.gender === 'female' ? 'female' : '');
    }
    
    if (data.name) {
      parts.push(`character named ${data.name}`);
    }
    
    parts.push('professional portrait photo, high quality, detailed, cinematic lighting');
    
    return parts.filter(p => p).join(', ');
  };
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-auto">
      <div className="bg-[var(--bg-primary)] rounded-lg w-full max-w-3xl max-h-[90vh] overflow-auto m-4">
        {/* Header */}
        <div className="sticky top-0 bg-[var(--bg-primary)] px-6 py-4 border-b flex items-center justify-between z-10">
          <h2 className="text-xl font-semibold">
            {character ? '编辑角色卡' : '创建角色卡'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[var(--bg-hover)] rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Tabs */}
        <div className="sticky top-[73px] bg-[var(--bg-primary)] border-b z-10">
          <div className="flex px-6">
            <button
              onClick={() => setActiveTab('appearance')}
              className={`px-4 py-3 flex items-center gap-2 ${
                activeTab === 'appearance' 
                  ? 'border-b-2 border-[var(--accent-primary)] text-[var(--accent-primary)] font-medium' 
                  : 'text-[var(--text-secondary)]'
              }`}
            >
              <User className="w-4 h-4" />
              外观
            </button>
            <button
              onClick={() => setActiveTab('voice')}
              className={`px-4 py-3 flex items-center gap-2 ${
                activeTab === 'voice' 
                  ? 'border-b-2 border-[var(--accent-primary)] text-[var(--accent-primary)] font-medium' 
                  : 'text-[var(--text-secondary)]'
              }`}
            >
              <Mic className="w-4 h-4" />
              音色
            </button>
            <button
              onClick={() => setActiveTab('personality')}
              className={`px-4 py-3 flex items-center gap-2 ${
                activeTab === 'personality' 
                  ? 'border-b-2 border-[var(--accent-primary)] text-[var(--accent-primary)] font-medium' 
                  : 'text-[var(--text-secondary)]'
              }`}
            >
              性格
            </button>
          </div>
        </div>
        
        {/* Content */}
        <div className="p-6">
          {activeTab === 'appearance' && (
            <div className="space-y-4">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                    角色名称 *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                    角色定位
                  </label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value as CharacterCard['role'] })}
                    className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                  >
                    <option value="protagonist">主角</option>
                    <option value="supporting">配角</option>
                    <option value="antagonist">反派</option>
                    <option value="minor">次要角色</option>
                  </select>
                </div>
              </div>
              
              {/* Reference Image */}
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                  角色参考图
                </label>
                
                {generateError && (
                  <div className="mb-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <p className="text-xs text-[var(--accent-error)] mb-2">{generateError}</p>
                    {generateError.includes('图像生成') && (
                      <button
                        onClick={() => {
                          setGenerateError(null);
                          eventBus.emit(Events.OPEN_SETTINGS);
                        }}
                        className="flex items-center gap-1.5 text-xs text-[var(--accent-primary)] hover:underline"
                      >
                        <Settings className="w-3.5 h-3.5" />
                        打开设置诊断工具
                      </button>
                    )}
                  </div>
                )}
                
                <div className="border-2 border-dashed border-[var(--border-default)] rounded-lg p-6 text-center">
                  {formData.appearance?.referenceImage ? (
                    <div>
                      <img
                        src={formData.appearance.referenceImage}
                        alt="Preview"
                        className="max-h-40 mx-auto mb-3 rounded"
                      />
                      <div className="flex gap-2 justify-center">
                        <button
                          onClick={() => setFormData({
                            ...formData,
                            appearance: { ...formData.appearance!, referenceImage: '' }
                          })}
                          className="text-[var(--accent-error)] text-sm hover:underline"
                        >
                          删除图片
                        </button>
                        <button
                          onClick={handleGenerateImage}
                          disabled={isGeneratingImage}
                          className="text-[var(--accent-primary)] text-sm hover:underline disabled:opacity-50"
                        >
                          重新生成
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {isGeneratingImage ? (
                        <div>
                          <Loader2 className="w-12 h-12 mx-auto text-[var(--accent-primary)] animate-spin mb-3" />
                          <p className="text-sm text-[var(--text-secondary)]">正在生成参考图...</p>
                        </div>
                      ) : (
                        <>
                          <Upload className="w-12 h-12 mx-auto text-[var(--text-tertiary)] mb-3" />
                          <div className="space-y-2">
                            <button
                              onClick={handleGenerateImage}
                              className="btn-primary w-full flex items-center justify-center gap-2"
                            >
                              <Sparkles className="w-4 h-4" />
                              AI生成参考图
                            </button>
                            <p className="text-xs text-[var(--text-tertiary)]">或</p>
                            <input
                              type="file"
                              accept="image/*"
                              className="hidden"
                              id="character-image-upload"
                              onChange={(e) => {
                                const file = e.target.files?.[0];
                                if (file) {
                                  const url = URL.createObjectURL(file);
                                  setFormData({
                                    ...formData,
                                    appearance: { ...formData.appearance!, referenceImage: url }
                                  });
                                }
                              }}
                            />
                            <label
                              htmlFor="character-image-upload"
                              className="btn-secondary w-full block text-center cursor-pointer"
                            >
                              上传本地图片
                            </label>
                          </div>
                        </>
                      )}
                    </div>
                  )}
                </div>
                <p className="text-xs text-[var(--text-tertiary)] mt-2">
                  提示：AI会根据角色描述自动生成参考图
                </p>
              </div>
              
              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                  角色描述
                </label>
                <textarea
                  value={formData.appearance?.description}
                  onChange={(e) => setFormData({
                    ...formData,
                    appearance: { ...formData.appearance!, description: e.target.value }
                  })}
                  rows={3}
                  className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                  placeholder="描述角色的外貌特征、穿着等"
                />
              </div>
              
              {/* Gender & Age */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">性别</label>
                  <select
                    value={formData.appearance?.gender}
                    onChange={(e) => setFormData({
                      ...formData,
                      appearance: { ...formData.appearance!, gender: e.target.value as CharacterCard['appearance']['gender'] }
                    })}
                    className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                  >
                    <option value="male">男性</option>
                    <option value="female">女性</option>
                    <option value="other">其他</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">年龄段</label>
                  <select
                    value={formData.appearance?.ageRange}
                    onChange={(e) => setFormData({
                      ...formData,
                      appearance: { ...formData.appearance!, ageRange: e.target.value as CharacterCard['appearance']['ageRange'] }
                    })}
                    className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                  >
                    <option value="child">儿童 (6-12岁)</option>
                    <option value="teenager">青少年 (13-19岁)</option>
                    <option value="young_adult">青年 (20-35岁)</option>
                    <option value="middle_aged">中年 (36-55岁)</option>
                    <option value="elderly">老年 (56岁以上)</option>
                  </select>
                </div>
              </div>
              
              {/* Style */}
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">风格</label>
                <select
                  value={formData.consistency?.style}
                  onChange={(e) => setFormData({
                    ...formData,
                    consistency: { ...formData.consistency!, style: e.target.value as CharacterCard['consistency']['style'] }
                  })}
                  className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                >
                  <option value="realistic">写实风格</option>
                  <option value="anime">动漫风格</option>
                  <option value="cartoon">卡通风格</option>
                  <option value="artistic">艺术风格</option>
                </select>
              </div>
            </div>
          )}
          
          {activeTab === 'voice' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                  TTS引擎
                </label>
                <select
                  value={formData.voice?.engine}
                  onChange={(e) => setFormData({
                    ...formData,
                    voice: { ...formData.voice!, engine: e.target.value as CharacterCard['voice']['engine'] }
                  })}
                  className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                >
                  <option value="minimax">Minimax TTS (中文优化)</option>
                  <option value="openai">OpenAI TTS (多语言)</option>
                  <option value="elevenlabs">ElevenLabs (高质量)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                  音色风格
                </label>
                <select
                  value={formData.voice?.voiceStyle}
                  onChange={(e) => setFormData({
                    ...formData,
                    voice: { ...formData.voice!, voiceStyle: e.target.value }
                  })}
                  className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                >
                  <option value="gentle">温柔</option>
                  <option value="energetic">活力</option>
                  <option value="calm">平静</option>
                  <option value="serious">严肃</option>
                  <option value="cheerful">愉快</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                  语速: {formData.voice?.speechRate}x
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  value={formData.voice?.speechRate}
                  onChange={(e) => setFormData({
                    ...formData,
                    voice: { ...formData.voice!, speechRate: parseFloat(e.target.value) }
                  })}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                  音调: {formData.voice?.pitch}x
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  value={formData.voice?.pitch}
                  onChange={(e) => setFormData({
                    ...formData,
                    voice: { ...formData.voice!, pitch: parseFloat(e.target.value) }
                  })}
                  className="w-full"
                />
              </div>
            </div>
          )}
          
          {activeTab === 'personality' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                  背景故事
                </label>
                <textarea
                  value={formData.personality?.background}
                  onChange={(e) => setFormData({
                    ...formData,
                    personality: { ...formData.personality!, background: e.target.value }
                  })}
                  rows={4}
                  className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                  placeholder="角色的背景故事、经历等"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-[var(--text-primary)] mb-2">
                  角色动机
                </label>
                <textarea
                  value={formData.personality?.motivation}
                  onChange={(e) => setFormData({
                    ...formData,
                    personality: { ...formData.personality!, motivation: e.target.value }
                  })}
                  rows={2}
                  className="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] text-[var(--text-primary)]"
                  placeholder="角色的目标、动机等"
                />
              </div>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="sticky bottom-0 bg-[var(--bg-primary)] px-6 py-4 border-t flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-[var(--border-default)] rounded-lg hover:bg-[var(--bg-secondary)]"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-[var(--accent-primary)] text-white rounded-lg hover:opacity-90"
          >
            保存角色卡
          </button>
        </div>
      </div>
    </div>
  );
}
