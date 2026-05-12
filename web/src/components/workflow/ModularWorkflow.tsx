/**
 * 模块化工作流组件 - 完整实现版
 * 
 * 已实现：
 * 1. 所有5个模块的API调用
 * 2. 完整的数据流管理
 * 3. 组件集成
 * 4. 用户确认流程
 * 5. 从项目配置读取API Key
 */

import { useState, useEffect } from 'react';
import { StoryboardEditor } from '@/components/StoryboardEditor';
import { CharacterImageSelector } from '@/components/workflow/CharacterImageSelector';
import { ProgressTracker } from '@/components/workflow/ProgressTracker';
import { useProjectStore } from '@/store/projectStore';
import { Shot } from '@/types/project';

interface ModuleInfo {
  id: number;
  key: '1_novel_analysis' | '2_character_creation' | '3_storyboard' | '4_resource_generation' | '5_final_composition';
  title: string;
  icon: string;
  description: string;
}

interface CharacterInfo {
  name: string;
  role: string;
  description: string;
}

interface GeneratedImage {
  index: number;
  url: string;
  prompt: string;
  composition: string;
  variation: string;
  seed: number;
  quality_score: number;
}

interface CharacterData {
  character_info: CharacterInfo;
  generated_images?: GeneratedImage[];
  selected_images?: GeneratedImage[];
}

interface ModuleData {
  total_characters?: number;
  characters?: CharacterData[];
  storyboard?: { shots: unknown[] };
  resources?: { images?: unknown[]; videos?: unknown[]; audios?: unknown[] };
  final_video_url?: string;
  project_id?: string;
  completed_at?: string;
  output_format?: string;
  quality?: string;
}

interface ModuleState {
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  data?: ModuleData;
  error?: string;
  cost?: number;
}

interface WorkflowState {
  projectId: string;
  currentModule: number;
  modules: {
    '1_novel_analysis': ModuleState;
    '2_character_creation': ModuleState;
    '3_storyboard': ModuleState;
    '4_resource_generation': ModuleState;
    '5_final_composition': ModuleState;
  };
  totalCost: number;
}

export function ModularWorkflow() {
  const { settings } = useProjectStore();
  
  const [workflowState, setWorkflowState] = useState<WorkflowState>({
    projectId: '',
    currentModule: 1,
    modules: {
      '1_novel_analysis': { status: 'pending' },
      '2_character_creation': { status: 'pending' },
      '3_storyboard': { status: 'pending' },
      '4_resource_generation': { status: 'pending' },
      '5_final_composition': { status: 'pending' }
    },
    totalCost: 0
  });

  const [novelText, setNovelText] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [characterSelections, setCharacterSelections] = useState<Map<number, GeneratedImage[]>>(new Map());
  
  // 从项目设置读取API Key
  useEffect(() => {
    if (settings.apiKey) {
      setApiKey(settings.apiKey);
    }
  }, [settings.apiKey]);

  const modules: ModuleInfo[] = [
    { id: 1, key: '1_novel_analysis' as const, title: '小说分析与场景规划', icon: '📖', description: '智能分析小说，自动识别场景' },
    { id: 2, key: '2_character_creation' as const, title: '角色创建', icon: '🎭', description: '提取角色信息，生成参考图' },
    { id: 3, key: '3_storyboard' as const, title: '分镜脚本生成', icon: '🎬', description: '为每个场景生成详细分镜' },
    { id: 4, key: '4_resource_generation' as const, title: '资源生成', icon: '🎨', description: '批量生成图像、视频、音频' },
    { id: 5, key: '5_final_composition' as const, title: '合成输出', icon: '🎥', description: '合成最终视频' }
  ];

  // 更新模块状态
  const updateModuleState = (moduleKey: keyof WorkflowState['modules'], update: Partial<ModuleState>) => {
    setWorkflowState(prev => {
      const newModules = { ...prev.modules, [moduleKey]: { ...prev.modules[moduleKey], ...update } };
      const totalCost = Object.values(newModules).reduce((sum, m) => sum + (m.cost || 0), 0);
      return { ...prev, modules: newModules, totalCost };
    });
  };

  // ✅ 模块1：小说分析
  const handleModule1 = async () => {
    if (!novelText || !apiKey) {
      alert('请填写小说文本和API Key');
      return;
    }

    setIsProcessing(true);
    updateModuleState('1_novel_analysis', { status: 'in_progress' });

    try {
      const response = await fetch('/api/module1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          novel_text: novelText,
          max_scenes: 15,
          language: 'chinese'
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'API请求失败');
      }
      

      const data = await response.json();

      updateModuleState('1_novel_analysis', {
        status: 'completed',
        data: JSON.parse(data.module_data),
        cost: 0.002
      });

      setWorkflowState(prev => ({
        ...prev,
        currentModule: 2,
        projectId: data.project_id
      }));

    } catch (error: unknown) {
      updateModuleState('1_novel_analysis', {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // ✅ 模块2：角色创建
  const handleModule2 = async () => {
    setIsProcessing(true);
    updateModuleState('2_character_creation', { status: 'in_progress' });

    try {
      const module1Data = workflowState.modules['1_novel_analysis'].data;
      
      const response = await fetch('/api/module2/characters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module1_data: JSON.stringify(module1Data),
          max_characters: 5,
          reference_images_per_character: 5,
          min_selected_images: 3,
          image_model: 'kling-v2'
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'API请求失败');
      }
      

      const data = await response.json();

      updateModuleState('2_character_creation', {
        status: 'completed',
        data: JSON.parse(data.module_data),
        cost: 0.33
      });

      // 不自动跳转到模块3，让用户先选择图片
      // setWorkflowState(prev => ({ ...prev, currentModule: 3 }));

    } catch (error: unknown) {
      updateModuleState('2_character_creation', {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // ✅ 用户选择角色图片
  const handleImageSelection = async (characterIndex: number, selectedImages: GeneratedImage[]) => {
    try {
      const response = await fetch('/api/module2/select-images', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: workflowState.projectId,
          character_index: characterIndex,
          selected_image_indices: selectedImages.map(img => img.index)
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'API请求失败');
      }
      

      const data = await response.json();

      if (data.success) {
        // 更新本地状态
        const newSelections = new Map(characterSelections);
        newSelections.set(characterIndex, selectedImages);
        setCharacterSelections(newSelections);

        // 更新模块数据
        const module2Data = workflowState.modules['2_character_creation'].data;
        if (module2Data && module2Data.characters && module2Data.characters[characterIndex]) {
          module2Data.characters[characterIndex].selected_images = selectedImages;
          updateModuleState('2_character_creation', {
            data: module2Data
          });
        }

        console.log(`✓ 角色 ${characterIndex + 1} 已选择 ${selectedImages.length} 张图片`);
      } else {
        alert(`保存失败: ${data.error}`);
      }
    } catch (error: unknown) {
      console.error('保存图片选择失败:', error);
      alert(`保存失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  // ✅ 检查所有角色是否都选择了足够的图片
  const checkAllCharactersHaveEnoughImages = () => {
    const module2Data = workflowState.modules['2_character_creation'].data;
    if (!module2Data || !module2Data.characters) return false;

    return module2Data.characters.every((char: CharacterData) => {
      return char.selected_images && char.selected_images.length >= 3;
    });
  };

  // ✅ 模块3：分镜脚本
  const handleModule3 = async () => {
    setIsProcessing(true);
    updateModuleState('3_storyboard', { status: 'in_progress' });

    try {
      const module1Data = workflowState.modules['1_novel_analysis'].data;
      const module2Data = workflowState.modules['2_character_creation'].data;
      
      const response = await fetch('/api/module3/storyboard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module1_data: JSON.stringify(module1Data),
          module2_data: JSON.stringify(module2Data),
          detail_level: 'standard',
          target_duration: 60
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'API请求失败');
      }
      

      const data = await response.json();

      updateModuleState('3_storyboard', {
        status: 'completed',
        data: JSON.parse(data.module_data),
        cost: 0.005
      });

      setWorkflowState(prev => ({ ...prev, currentModule: 4 }));

    } catch (error: unknown) {
      updateModuleState('3_storyboard', {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // ✅ 模块4：资源生成
  const handleModule4 = async () => {
    setIsProcessing(true);
    updateModuleState('4_resource_generation', { status: 'in_progress' });

    try {
      const module1Data = workflowState.modules['1_novel_analysis'].data;
      const module2Data = workflowState.modules['2_character_creation'].data;
      const module3Data = workflowState.modules['3_storyboard'].data;
      
      const response = await fetch('/api/module4/resources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module1_data: JSON.stringify(module1Data),
          module2_data: JSON.stringify(module2Data),
          module3_data: JSON.stringify(module3Data),
          batch_size: 5,
          image_model: settings.defaultImageModel || 'kling-v2',
          video_model: settings.defaultVideoModel || 'kling-v2-master'
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'API请求失败');
      }
      

      const data = await response.json();

      updateModuleState('4_resource_generation', {
        status: 'completed',
        data: JSON.parse(data.module_data),
        cost: 4.40
      });

      setWorkflowState(prev => ({ ...prev, currentModule: 5 }));

    } catch (error: unknown) {
      updateModuleState('4_resource_generation', {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // ✅ 模块5：合成输出
  const handleModule5 = async () => {
    setIsProcessing(true);
    updateModuleState('5_final_composition', { status: 'in_progress' });

    try {
      const module4Data = workflowState.modules['4_resource_generation'].data;
      
      const response = await fetch('/api/module5/compose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module4_data: JSON.stringify(module4Data),
          output_format: 'mp4',
          quality: 'standard'
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'API请求失败');
      }
      

      const data = await response.json();

      updateModuleState('5_final_composition', {
        status: 'completed',
        data: JSON.parse(data.module_data),
        cost: 0.10
      });

    } catch (error: unknown) {
      updateModuleState('5_final_composition', {
        status: 'error',
        error: error instanceof Error ? error.message : String(error)
      });
    } finally {
      setIsProcessing(false);
    }
  };

  // 用户确认当前模块
  const handleUserConfirm = (moduleId: number) => {
    switch (moduleId) {
      case 1:
        handleModule2();
        break;
      case 2:
        // 检查是否所有角色都选择了足够的图片
        if (!checkAllCharactersHaveEnoughImages()) {
          alert('请为每个角色至少选择3张参考图片');
          return;
        }
        setWorkflowState(prev => ({ ...prev, currentModule: 3 }));
        break;
      case 3:
        handleModule4();
        break;
      case 4:
        handleModule5();
        break;
      case 5:
        alert('🎉 项目完成！视频已生成。');
        break;
    }
  };

  return (
    <div className="h-full flex flex-col bg-[var(--bg-primary)]">
      {/* 顶部进度条 */}
      <div className="h-16 bg-[var(--bg-secondary)] border-b border-[var(--border-default)] px-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold">模块化工作流</h2>
          {workflowState.projectId && (
            <span className="text-xs text-[var(--text-tertiary)] font-mono">
              项目ID: {workflowState.projectId}
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-6">
          {/* 进度指示器 */}
          <div className="flex items-center gap-2">
            {modules.map((module, index) => (
              <div key={module.id} className="flex items-center">
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                  ${workflowState.currentModule === module.id 
                    ? 'bg-[var(--accent-primary)] text-white' 
                    : workflowState.modules[module.key].status === 'completed'
                    ? 'bg-[var(--success)] text-white'
                    : 'bg-[var(--bg-tertiary)] text-[var(--text-tertiary)]'
                  }
                `}>
                  {workflowState.modules[module.key].status === 'completed' ? '✓' : module.id}
                </div>
                {index < modules.length - 1 && (
                  <div className={`w-12 h-1 mx-1 ${workflowState.currentModule > module.id ? 'bg-[var(--success)]' : 'bg-[var(--bg-tertiary)]'}`} />
                )}
              </div>
            ))}
          </div>

          {/* 累计成本 */}
          <div className="text-sm">
            <span className="text-[var(--text-tertiary)]">累计成本:</span>
            <span className="ml-2 font-semibold text-[var(--text-primary)]">
              ${workflowState.totalCost.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧：模块列表 */}
        <div className="w-80 bg-[var(--bg-secondary)] border-r border-[var(--border-default)] overflow-y-auto">
          <div className="p-4 space-y-2">
            {modules.map(module => (
              <ModuleCard
                key={module.id}
                module={module}
                state={workflowState.modules[module.key]}
                isActive={workflowState.currentModule === module.id}
                onClick={() => setWorkflowState(prev => ({ ...prev, currentModule: module.id }))}
              />
            ))}
          </div>
          
          {/* 实时进度追踪器 */}
          {workflowState.projectId && (
            <div className="p-4 border-t border-[var(--border-default)]">
              <ProgressTracker 
                projectId={workflowState.projectId}
                autoRefresh={true}
                refreshInterval={3000}
              />
            </div>
          )}
        </div>

        {/* 右侧：模块详情 */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">
            <ModuleDetail
              moduleId={workflowState.currentModule}
              moduleState={workflowState.modules[modules[workflowState.currentModule - 1].key]}
              novelText={novelText}
              setNovelText={setNovelText}
              apiKey={apiKey}
              setApiKey={setApiKey}
              isProcessing={isProcessing}
              onConfirm={handleUserConfirm}
              onImageSelection={handleImageSelection}
              onProcess={
                workflowState.currentModule === 1 ? handleModule1 :
                workflowState.currentModule === 2 ? handleModule2 :
                workflowState.currentModule === 3 ? handleModule3 :
                workflowState.currentModule === 4 ? handleModule4 :
                workflowState.currentModule === 5 ? handleModule5 : undefined
              }
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// 模块卡片组件
function ModuleCard({ module, state, isActive, onClick }: { 
  module: ModuleInfo; 
  state: { status: 'pending' | 'in_progress' | 'completed' | 'error'; cost?: number }; 
  isActive: boolean; 
  onClick: () => void 
}) {
  const statusColors = {
    pending: 'text-[var(--text-tertiary)]',
    in_progress: 'text-[var(--warning)]',
    completed: 'text-[var(--success)]',
    error: 'text-[var(--error)]'
  };

  const statusIcons = {
    pending: '⏸️',
    in_progress: '⏳',
    completed: '✅',
    error: '❌'
  };

  return (
    <div
      onClick={onClick}
      className={`
        p-4 rounded-lg cursor-pointer transition-all
        ${isActive 
          ? 'bg-[var(--accent-primary)]/10 border-2 border-[var(--accent-primary)]' 
          : 'bg-[var(--bg-tertiary)] border-2 border-transparent hover:border-[var(--border-default)]'
        }
      `}
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl">{module.icon}</span>
        <div className="flex-1">
          <h3 className="font-medium text-sm">{module.title}</h3>
          <p className="text-xs text-[var(--text-tertiary)] mt-0.5">{module.description}</p>
        </div>
        <span className={`text-lg ${statusColors[state.status]}`}>
          {statusIcons[state.status]}
        </span>
      </div>
      
      {state.cost !== undefined && (
        <div className="mt-2 text-xs text-[var(--text-tertiary)]">
          成本: ${state.cost.toFixed(3)}
        </div>
      )}
    </div>
  );
}

// 模块详情组件
interface ModuleDetailProps {
  moduleId: number;
  moduleState: ModuleState;
  novelText: string;
  setNovelText: (text: string) => void;
  apiKey: string;
  setApiKey: (key: string) => void;
  isProcessing: boolean;
  onConfirm: (moduleId: number) => void;
  onProcess?: () => void;
  onImageSelection: (characterIndex: number, selectedImages: GeneratedImage[]) => void;
}

function ModuleDetail({ 
  moduleId, 
  moduleState, 
  novelText, 
  setNovelText, 
  apiKey, 
  setApiKey, 
  isProcessing, 
  onConfirm, 
  onProcess,
  onImageSelection 
}: ModuleDetailProps) {
  const moduleConfigs = {
    1: { title: '📖 模块1：小说分析与场景规划', description: '输入小说文本，系统将自动分析并识别场景' },
    2: { title: '🎭 模块2：角色创建', description: '系统将提取角色信息并生成参考图' },
    3: { title: '🎬 模块3：分镜脚本生成', description: '为每个场景生成详细的分镜脚本' },
    4: { title: '🎨 模块4：资源生成', description: '批量生成图像、视频、音频' },
    5: { title: '🎥 模块5：合成输出', description: '合成最终视频' }
  };

  const config = moduleConfigs[moduleId as keyof typeof moduleConfigs];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">{config.title}</h2>
        <p className="text-[var(--text-tertiary)]">{config.description}</p>
      </div>

      {/* 模块1：输入小说 */}
      {moduleId === 1 && moduleState.status === 'pending' && (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">API Key</label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="输入您的UnlimitAI API Key"
              className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:border-[var(--accent-primary)]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">小说文本</label>
            <textarea
              value={novelText}
              onChange={(e) => setNovelText(e.target.value)}
              placeholder="粘贴您的小说文本..."
              rows={15}
              className="w-full px-4 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-default)] rounded-lg focus:outline-none focus:border-[var(--accent-primary)] font-mono text-sm"
            />
            <p className="mt-2 text-xs text-[var(--text-tertiary)]">
              已输入 {novelText.length} 字
            </p>
          </div>

          <button
            onClick={onProcess}
            disabled={isProcessing || !novelText || !apiKey}
            className="w-full py-3 bg-[var(--accent-primary)] text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? '分析中...' : '开始分析'}
          </button>
        </div>
      )}

      {/* 模块2：角色创建 */}
      {moduleId === 2 && (
        <div className="space-y-6">
          {moduleState.status === 'pending' && (
            <div className="text-center py-12">
              <p className="text-[var(--text-tertiary)]">请先完成模块1</p>
            </div>
          )}
          
          {moduleState.status === 'in_progress' && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[var(--accent-primary)]"></div>
              <p className="mt-4 text-[var(--text-tertiary)]">生成角色和参考图中...</p>
            </div>
          )}
          
          {moduleState.status === 'completed' && moduleState.data && (
            <div className="space-y-6">
              <div className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4">
                <h3 className="font-semibold mb-2">📋 角色创建说明</h3>
                <p className="text-sm text-[var(--text-tertiary)]">
                  已提取 <strong>{moduleState.data.total_characters}</strong> 个角色。请为每个角色选择至少 <strong>3张</strong> 参考图片。
                </p>
              </div>

              {(moduleState.data.characters || []).map((char: CharacterData, index: number) => (
                <div key={index} className="bg-[var(--bg-tertiary)] rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-lg">{char.character_info.name}</h3>
                      <p className="text-sm text-[var(--text-tertiary)]">{char.character_info.role}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-[var(--text-tertiary)]">
                        已生成: {char.generated_images?.length || 0}张
                      </div>
                      <div className="text-xs font-medium mt-1">
                        {(char.selected_images || []).length >= 3 ? (
                          <span className="text-[var(--success)]">✓ 已选择 {(char.selected_images || []).length}张</span>
                        ) : (
                          <span className="text-[var(--warning)]">需选择 {3 - (char.selected_images?.length || 0)}张</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="mb-4 text-sm text-[var(--text-tertiary)]">{char.character_info.description}</div>

                  {char.generated_images && char.generated_images.length > 0 && (
                    <CharacterImageSelector
                      characterName={char.character_info.name}
                      generatedImages={char.generated_images}
                      minSelections={3}
                      maxSelections={5}
                      onConfirm={(selectedImages) => onImageSelection(index, selectedImages)}
                      onRegenerate={() => console.log('重新生成:', index)}
                    />
                  )}
                </div>
              ))}

              <div className="flex gap-3">
                <button
                  onClick={() => onConfirm(2)}
                  disabled={!(moduleState.data.characters || []).every((char: CharacterData) => (char.selected_images || []).length >= 3)}
                  className="flex-1 py-3 bg-[var(--success)] text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ✅ 确认角色并继续到模块3
                </button>
              </div>
              
              {!(moduleState.data.characters || []).every((char: CharacterData) => (char.selected_images || []).length >= 3) && (
                <div className="text-sm text-[var(--warning)] bg-[var(--warning)]/10 border border-[var(--warning)]/20 rounded-lg p-3">
                  ⚠️ 请为所有角色选择至少3张参考图片后才能继续
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 模块3：分镜脚本 */}
      {moduleId === 3 && (
        <div className="space-y-6">
          {moduleState.status === 'pending' && (
            <div className="text-center py-12">
              <p className="text-[var(--text-tertiary)]">请先完成模块1和2</p>
            </div>
          )}
          
          {moduleState.status === 'in_progress' && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[var(--accent-primary)]"></div>
              <p className="mt-4 text-[var(--text-tertiary)]">生成分镜脚本中...</p>
            </div>
          )}
          
          {moduleState.status === 'completed' && moduleState.data && (
            <div className="space-y-6">
              {/* 分镜编辑器 */}
              <StoryboardEditor
                novelText={novelText}
                shots={(moduleState.data.storyboard?.shots || []) as Shot[]}
                onShotsChange={(shots: unknown[]) => {
                  console.log('用户编辑了分镜:', shots);
                }}
                onStartGeneration={(shots: unknown[]) => {
                  console.log('开始生成分镜:', shots);
                }}
              />

              {/* 用户确认 */}
              <div className="flex gap-3">
                <button
                  onClick={() => onConfirm(3)}
                  className="flex-1 py-3 bg-[var(--success)] text-white rounded-lg font-medium hover:opacity-90"
                >
                  ✅ 确认分镜并继续
                </button>
                <button
                  onClick={onProcess}
                  className="px-6 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-default)] rounded-lg font-medium hover:bg-[var(--bg-primary)]"
                >
                  🔄 重新生成
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 模块4：资源生成 */}
      {moduleId === 4 && (
        <div className="space-y-6">
          {moduleState.status === 'pending' && (
            <div className="text-center py-12">
              <p className="text-[var(--text-tertiary)]">请先完成模块1-3</p>
            </div>
          )}
          
          {moduleState.status === 'in_progress' && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[var(--accent-primary)]"></div>
              <p className="mt-4 text-[var(--text-tertiary)]">生成资源中...</p>
              <p className="text-xs text-[var(--text-tertiary)] mt-2">这可能需要几分钟时间</p>
            </div>
          )}
          
          {moduleState.status === 'completed' && moduleState.data && (
            <div className="space-y-6">
              <div className="bg-[var(--bg-tertiary)] rounded-lg p-6">
                <h3 className="font-semibold mb-4">✅ 资源生成完成</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-[var(--accent-primary)]">
                      {moduleState.data.resources?.images?.length || 0}
                    </div>
                    <div className="text-xs text-[var(--text-tertiary)]">图像</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-[var(--accent-primary)]">
                      {moduleState.data.resources?.videos?.length || 0}
                    </div>
                    <div className="text-xs text-[var(--text-tertiary)]">视频</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-[var(--accent-primary)]">
                      {moduleState.data.resources?.audios?.length || 0}
                    </div>
                    <div className="text-xs text-[var(--text-tertiary)]">音频</div>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => onConfirm(4)}
                  className="flex-1 py-3 bg-[var(--success)] text-white rounded-lg font-medium hover:opacity-90"
                >
                  ✅ 确认资源并继续
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 模块5：合成输出 */}
      {moduleId === 5 && (
        <div className="space-y-6">
          {moduleState.status === 'pending' && (
            <div className="text-center py-12">
              <p className="text-[var(--text-tertiary)]">请先完成模块1-4</p>
            </div>
          )}
          
          {moduleState.status === 'in_progress' && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[var(--accent-primary)]"></div>
              <p className="mt-4 text-[var(--text-tertiary)]">合成视频中...</p>
            </div>
          )}
          
          {moduleState.status === 'completed' && moduleState.data && (
            <div className="space-y-6">
              <div className="bg-[var(--bg-tertiary)] rounded-lg p-6 text-center">
                <div className="text-6xl mb-4">🎉</div>
                <h3 className="text-xl font-bold mb-2">视频生成完成！</h3>
                <p className="text-sm text-[var(--text-tertiary)] mb-4">
                  您的漫剧视频已准备就绪
                </p>
                
                {moduleState.data.final_video_url && (
                  <div className="space-y-3">
                    <a
                      href={moduleState.data.final_video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block px-6 py-3 bg-[var(--success)] text-white rounded-lg font-medium hover:opacity-90"
                    >
                      📥 下载视频
                    </a>
                    <br />
                    <a
                      href={moduleState.data.final_video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block text-sm text-[var(--accent-primary)] hover:underline"
                    >
                      👁️ 在线预览
                    </a>
                  </div>
                )}
              </div>

              <div className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4">
                <h4 className="font-semibold mb-2">项目统计</h4>
                <div className="text-sm text-[var(--text-tertiary)] space-y-1">
                  <div>项目ID: {moduleState.data.project_id}</div>
                  <div>完成时间: {moduleState.data.completed_at}</div>
                  <div>输出格式: {moduleState.data.output_format}</div>
                  <div>质量: {moduleState.data.quality}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 错误状态 */}
      {moduleState.status === 'error' && (
        <div className="bg-[var(--error)]/10 border border-[var(--error)] rounded-lg p-6">
          <h3 className="font-semibold text-[var(--error)] mb-2">❌ 处理失败</h3>
          <p className="text-sm text-[var(--text-primary)]">{moduleState.error}</p>
          <button
            onClick={onProcess}
            className="mt-4 px-6 py-2 bg-[var(--accent-primary)] text-white rounded-lg"
          >
            重试
          </button>
        </div>
      )}
    </div>
  );
}
