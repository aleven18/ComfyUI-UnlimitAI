import { useState } from 'react';
import { Shot } from '@/types/project';
import { 
  BookOpen, 
  Sparkles, 
  Film, 
  Wand2,
  ChevronRight,
  FileText
} from 'lucide-react';
import { ProfessionalAssistant } from './ProfessionalAssistant';
import { StoryboardEditor } from './StoryboardEditor';
import { useProjectStore } from '@/store/projectStore';

type Tab = 'novel' | 'assistant' | 'storyboard';

export function CreationPanel() {
  const [activeTab, setActiveTab] = useState<Tab>('novel');
  const [novelText, setNovelText] = useState('');
  
  const { createScene } = useProjectStore();
  
  const handleStartGeneration = (shots: Shot[]) => {
    shots.forEach(shot => {
      createScene(shot as Partial<Shot>);
    });
    setActiveTab('storyboard');
  };
  
  const tabs: { id: Tab; label: string; icon: React.ReactNode; description: string }[] = [
    { 
      id: 'novel', 
      label: '小说输入', 
      icon: <BookOpen className="w-4 h-4" />,
      description: '输入或粘贴小说文本'
    },
    { 
      id: 'assistant', 
      label: 'AI助手', 
      icon: <Sparkles className="w-4 h-4" />,
      description: '专业分析和优化建议'
    },
    { 
      id: 'storyboard', 
      label: '分镜编辑', 
      icon: <Film className="w-4 h-4" />,
      description: '可视化和编辑分镜'
    }
  ];
  
  return (
    <div className="h-full flex flex-col bg-[var(--bg-primary)]">
      {/* Tab Header */}
      <div className="border-b border-[var(--border-subtle)] px-6 py-3">
        <div className="flex items-center gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                h-9 px-4 flex items-center gap-2 text-[13px] font-medium rounded-lg transition-all
                ${activeTab === tab.id 
                  ? 'bg-[var(--accent-primary)] text-white' 
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
                }
              `}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-auto">
        {activeTab === 'novel' && (
          <div className="h-full p-6">
            <div className="max-w-4xl mx-auto h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-semibold flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    小说文本输入
                  </h2>
                  <p className="text-xs text-[var(--text-tertiary)] mt-1">
                    输入您的小说内容，AI将帮助您分析和生成分镜
                  </p>
                </div>
                <div className="text-xs text-[var(--text-tertiary)]">
                  {novelText.length} 字
                </div>
              </div>
              
              <textarea
                value={novelText}
                onChange={(e) => setNovelText(e.target.value)}
                placeholder="在此输入或粘贴您的小说文本...

示例：
阳光透过窗帘的缝隙洒进房间，李明慢慢睁开眼睛。他看了看床头的闹钟，已经是上午十点了。昨晚熬夜完成的剧本终于得到了导演的认可，这让他感到欣慰。

他起身走到窗前，推开窗户，清新的空气扑面而来。街道上行人匆匆，每个人都在为生活奔波。他突然想到，或许这就是他想要在作品中表达的主题——普通人的奋斗与梦想。"
                className="flex-1 w-full p-4 bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg text-sm leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)] focus:border-transparent transition-all"
                style={{ minHeight: '400px' }}
              />
              
              <div className="mt-4 flex items-center justify-between">
                <div className="text-xs text-[var(--text-tertiary)]">
                  提示：建议输入至少100字的文本以获得更好的分析效果
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => setActiveTab('assistant')}
                    disabled={novelText.length < 50}
                    className="btn-secondary flex items-center gap-2 disabled:opacity-50"
                  >
                    <Sparkles className="w-4 h-4" />
                    AI分析
                    <ChevronRight className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => setActiveTab('storyboard')}
                    disabled={novelText.length < 50}
                    className="btn-primary flex items-center gap-2 disabled:opacity-50"
                  >
                    <Wand2 className="w-4 h-4" />
                    生成分镜
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'assistant' && (
          <div className="h-full p-6">
            <div className="max-w-5xl mx-auto">
              <ProfessionalAssistant novelText={novelText} />
            </div>
          </div>
        )}
        
        {activeTab === 'storyboard' && (
          <div className="h-full p-6">
            <div className="max-w-full mx-auto">
              <StoryboardEditor 
                novelText={novelText}
                shots={[]}
                onShotsChange={() => {}}
                onStartGeneration={handleStartGeneration}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
