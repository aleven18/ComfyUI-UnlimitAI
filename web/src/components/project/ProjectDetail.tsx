import { useState, useEffect } from 'react';
import { Users, Film, Workflow, FolderOpen, Settings, PenTool, Clapperboard } from 'lucide-react';
import { useProjectStore } from '@/store/projectStore';
import { ProjectSettings } from '@/types/project';
import { CharacterManager } from '@/components/character/CharacterManager';
import { SceneList } from '@/components/scene/SceneList';
import { WorkflowConfig } from '@/components/workflow/WorkflowConfig';
import { WorkflowProgress } from '@/components/workflow/WorkflowProgress';
import { SmartCreationPanel } from '@/components/SmartCreationPanel';
import { ResourceManager } from '@/components/ResourceManager';
import { OnboardingGuide } from '@/components/common/OnboardingGuide';
import { StoryboardPanel } from '@/components/StoryboardPanel';
import { useComfyUI } from '@/hooks/useComfyUI';

type Tab = 'creation' | 'characters' | 'scenes' | 'workflow' | 'storyboard' | 'resources' | 'settings';

const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'characters', label: '角色卡', icon: <Users className="w-4 h-4" /> },
  { id: 'creation', label: '创作', icon: <PenTool className="w-4 h-4" /> },
  { id: 'scenes', label: '分镜', icon: <Film className="w-4 h-4" /> },
  { id: 'storyboard', label: '故事板视频', icon: <Clapperboard className="w-4 h-4" /> },
  { id: 'workflow', label: '工作流', icon: <Workflow className="w-4 h-4" /> },
  { id: 'resources', label: '资源', icon: <FolderOpen className="w-4 h-4" /> },
  { id: 'settings', label: '设置', icon: <Settings className="w-4 h-4" /> }
];

function StoryboardTabContent() {
  const { startStoryboardConversion, isConverting, progress, currentNode, logs, error } = useComfyUI();
  return (
    <div className="p-6 overflow-auto h-full">
      <StoryboardPanel
        onGenerate={startStoryboardConversion}
        isConverting={isConverting}
        progress={progress}
        currentNode={currentNode}
        logs={logs}
        error={error}
      />
    </div>
  );
}

export function ProjectDetail() {
  const { currentProject } = useProjectStore();
  const [activeTab, setActiveTab] = useState<Tab>('characters');
  const [showOnboarding, setShowOnboarding] = useState(false);
  
  useEffect(() => {
    if (currentProject) {
      const hasSeenGuide = localStorage.getItem('has_seen_onboarding');
      if (!hasSeenGuide) {
        setShowOnboarding(true);
      }
    }
  }, [currentProject]);
  
  if (!currentProject) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[var(--bg-primary)]">
        <div className="text-center">
          <Film className="w-16 h-16 mx-auto mb-4 text-[var(--text-tertiary)] opacity-50" />
          <h2 className="text-lg font-semibold text-[var(--text-secondary)]">选择或创建一个项目</h2>
          <p className="text-sm text-[var(--text-tertiary)] mt-2">从左侧列表选择项目，或点击"新建项目"开始</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex-1 flex bg-[var(--bg-primary)]">
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="px-6 py-4 border-b border-[var(--border-subtle)]">
          <h1 className="text-lg font-semibold">{currentProject.name}</h1>
          {currentProject.description && (
            <p className="text-sm text-[var(--text-tertiary)] mt-1">{currentProject.description}</p>
          )}
        </div>
        
        <div className="border-b border-[var(--border-subtle)]">
          <div className="flex px-6 gap-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  h-10 px-4 flex items-center gap-2 text-[13px] font-medium transition-colors relative
                  ${activeTab === tab.id 
                    ? 'text-[var(--text-primary)]' 
                    : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]'
                  }
                `}
              >
                {tab.icon}
                {tab.label}
                {activeTab === tab.id && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--accent-primary)]" />
                )}
              </button>
            ))}
          </div>
        </div>
        
        <div className="flex-1 overflow-hidden">
          {activeTab === 'creation' && <SmartCreationPanel onNavigate={(tab: string) => setActiveTab(tab as Tab)} />}
          {activeTab === 'characters' && <CharacterManager />}
          {activeTab === 'scenes' && <SceneList />}
          {activeTab === 'storyboard' && <StoryboardTabContent />}
          {activeTab === 'workflow' && <WorkflowConfig />}
          {activeTab === 'resources' && <ResourceManager />}
          {activeTab === 'settings' && <ProjectSettingsPanel />}
        </div>
      </div>
      
      <WorkflowProgress />
      
      <OnboardingGuide
        isOpen={showOnboarding}
        onClose={() => setShowOnboarding(false)}
        onNavigate={(tab: string) => setActiveTab(tab as Tab)}
      />
    </div>
  );
}

function ProjectSettingsPanel() {
  const { currentProject, updateProject, settings, updateSettings } = useProjectStore();
  
  if (!currentProject) return null;
  
  return (
    <div className="p-6 max-w-2xl">
      <h2 className="text-base font-semibold mb-6">项目设置</h2>
      
      <div className="space-y-6">
        <div>
          <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">
            项目名称
          </label>
          <input
            type="text"
            value={currentProject.name}
            onChange={(e) => updateProject({ name: e.target.value })}
            className="input-base"
          />
        </div>
        
        <div>
          <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">
            项目描述
          </label>
          <textarea
            value={currentProject.description}
            onChange={(e) => updateProject({ description: e.target.value })}
            rows={3}
            className="input-base"
          />
        </div>
        
        <div>
          <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">
            画面风格
          </label>
          <select
            value={settings.style}
            onChange={(e) => updateSettings({ style: e.target.value as ProjectSettings['style'] })}
            className="input-base"
          >
            <option value="realistic">写实风格</option>
            <option value="anime">动漫风格</option>
            <option value="cartoon">卡通风格</option>
            <option value="artistic">艺术风格</option>
          </select>
        </div>
        
        <div>
          <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">
            画面比例
          </label>
          <select
            value={settings.aspectRatio}
            onChange={(e) => updateSettings({ aspectRatio: e.target.value as ProjectSettings['aspectRatio'] })}
            className="input-base"
          >
            <option value="16:9">16:9 (横屏)</option>
            <option value="9:16">9:16 (竖屏)</option>
            <option value="1:1">1:1 (正方形)</option>
            <option value="4:3">4:3 (传统)</option>
          </select>
        </div>
        
        <div className="pt-4 border-t border-[var(--border-subtle)]">
          <h3 className="text-sm font-semibold mb-4">API 配置</h3>
          
          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">
              UnlimitAI API Key
            </label>
            <input
              type="password"
              value={settings.apiKey || ''}
              onChange={(e) => updateSettings({ apiKey: e.target.value })}
              placeholder="sk-..."
              className="input-base"
            />
            <p className="text-xs text-[var(--text-tertiary)] mt-1">
              用于调用AI模型生成内容。在工作流中会自动使用此Key。
            </p>
          </div>
          
          {settings.apiKey && (
            <div className="mt-3 p-3 bg-[var(--bg-secondary)] rounded-lg">
              <div className="text-xs text-[var(--text-secondary)]">
                已配置 API Key: {settings.apiKey.length > 12 ? `${settings.apiKey.substring(0, 4)}...${settings.apiKey.substring(settings.apiKey.length - 4)}` : '****'}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
