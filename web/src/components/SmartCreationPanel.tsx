/**
 * 智能创作面板 - 专注于分镜生成
 * 
 * 使用已有角色卡生成分镜
 */

import { useState } from 'react';
import { Loader2, CheckCircle, AlertCircle, Film, Wand2, Users, ArrowRight } from 'lucide-react';
import { useProjectStore } from '@/store/projectStore';
import { generateStoryboardWithCharacters } from '@/lib/smart-workflow';
import { hasApiKey } from '@/lib/unified-config';

type WorkflowStep = 'input' | 'generating' | 'completed';

interface SmartCreationPanelProps {
  onNavigate?: (tab: string) => void;
}

export function SmartCreationPanel({ onNavigate }: SmartCreationPanelProps) {
  const [step, setStep] = useState<WorkflowStep>('input');
  const [novelText, setNovelText] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  const { characters, createScene, addTask, updateTask } = useProjectStore();
  
  const handleGenerateStoryboard = async () => {
    if (!hasApiKey()) {
      setError('请先在右上角设置中配置API Key');
      return;
    }
    
    if (novelText.length < 50) {
      setError('请输入至少50字的小说文本');
      return;
    }
    
    if (characters.length === 0) {
      setError('请先在"角色卡"标签页创建角色');
      return;
    }
    
    setError(null);
    setStep('generating');
    
    const taskId = addTask({
      name: '生成分镜脚本',
      type: 'text_analysis',
      status: 'running'
    });
    
    try {
      // 将角色卡转换为提取的角色格式
      const extractedCharacters = characters.map(char => ({
        name: char.name,
        role: char.role === 'protagonist' ? '主角' : char.role === 'supporting' ? '配角' : '次要角色',
        description: char.personality.background,
        appearance: char.appearance.description,
        personality: char.personality.traits.join('、'),
        keyScenes: []
      }));
      
      const scenes = await generateStoryboardWithCharacters(novelText, extractedCharacters);
      
      scenes.forEach(scene => {
        createScene({
          shotNumber: scene.sceneNumber,
          shotSize: scene.shotSize,
          cameraMove: scene.cameraMove,
          duration: scene.duration,
          description: scene.description,
          characters: scene.characters,
          prompt: scene.prompt,
          notes: scene.notes
        });
      });
      
      updateTask(taskId, { 
        status: 'completed',
        cost: 0.02
      });
      
      setStep('completed');
    } catch (err: unknown) {
      setError((err instanceof Error ? err.message : String(err)) || '生成分镜失败');
      setStep('input');
      updateTask(taskId, { 
        status: 'failed',
        error: (err instanceof Error ? err.message : String(err))
      });
    }
  };
  
  const handleReset = () => {
    setStep('input');
    setNovelText('');
    setError(null);
  };
  
  return (
    <div className="h-full flex flex-col bg-[var(--bg-primary)]">
      <div className="border-b border-[var(--border-subtle)] px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold flex items-center gap-2">
              <Wand2 className="w-5 h-5" />
              生成分镜
            </h2>
            <p className="text-xs text-[var(--text-tertiary)] mt-1">
              基于小说文本和角色卡生成分镜脚本
            </p>
          </div>
          
          {step !== 'input' && (
            <button
              onClick={handleReset}
              className="text-xs px-3 py-1.5 border border-[var(--border-default)] rounded hover:bg-[var(--bg-hover)] transition-colors"
            >
              重新开始
            </button>
          )}
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-6">
        {error && (
          <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-500">操作失败</p>
              <p className="text-xs text-red-400 mt-1">{error}</p>
            </div>
          </div>
        )}
        
        {step === 'input' && (
          <div className="max-w-4xl mx-auto">
            {/* 角色卡状态 */}
            <div className="mb-6 p-4 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-[var(--accent-primary)]" />
                  <span className="text-sm font-medium">角色卡状态</span>
                </div>
                <span className={`text-xs font-medium ${characters.length > 0 ? 'text-[var(--success)]' : 'text-[var(--warning)]'}`}>
                  {characters.length > 0 ? `已创建 ${characters.length} 个角色` : '未创建角色'}
                </span>
              </div>
              
              {characters.length === 0 && (
                <div className="mt-3">
                  <p className="text-xs text-[var(--text-tertiary)] mb-3">
                    生成分镜需要先创建角色卡。您可以选择：
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => onNavigate?.('characters')}
                      className="flex-1 px-4 py-2 bg-[var(--accent-primary)] text-white text-sm font-medium rounded-lg hover:opacity-90 transition-all flex items-center justify-center gap-2"
                    >
                      创建角色卡
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
              
              {characters.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {characters.slice(0, 5).map(char => (
                    <span 
                      key={char.id}
                      className="px-2 py-1 bg-[var(--bg-primary)] rounded text-xs"
                    >
                      {char.name}
                    </span>
                  ))}
                  {characters.length > 5 && (
                    <span className="px-2 py-1 text-xs text-[var(--text-tertiary)]">
                      +{characters.length - 5} 个
                    </span>
                  )}
                </div>
              )}
            </div>
            
            {/* 小说文本输入 */}
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-semibold">小说文本</h3>
              <span className="text-xs text-[var(--text-tertiary)]">{novelText.length} 字</span>
            </div>
            
            <textarea
              value={novelText}
              onChange={(e) => setNovelText(e.target.value)}
              placeholder="在此输入或粘贴您的小说文本..."
              className="w-full h-96 p-4 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg text-sm leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
            />
            
            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-[var(--text-tertiary)]">
                建议：输入至少100字的文本以获得更好的分析效果
              </p>
              
              <button
                onClick={handleGenerateStoryboard}
                disabled={novelText.length < 50 || characters.length === 0}
                className="btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                <Film className="w-4 h-4" />
                生成分镜
              </button>
            </div>
          </div>
        )}
        
        {step === 'generating' && (
          <div className="flex flex-col items-center justify-center h-full">
            <Loader2 className="w-16 h-16 text-[var(--accent-primary)] animate-spin" />
            <p className="mt-4 text-sm text-[var(--text-secondary)]">正在生成分镜脚本...</p>
            <p className="mt-2 text-xs text-[var(--text-tertiary)]">使用角色信息优化分镜提示词</p>
          </div>
        )}
        
        {step === 'completed' && (
          <div className="flex flex-col items-center justify-center h-full">
            <CheckCircle className="w-16 h-16 text-[var(--success)]" />
            <p className="mt-4 text-base font-semibold text-[var(--text-primary)]">分镜生成完成！</p>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">
              请前往"分镜"标签页查看和编辑
            </p>
            
            <div className="mt-6">
              <button
                onClick={handleReset}
                className="btn-primary"
              >
                生成新分镜
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
