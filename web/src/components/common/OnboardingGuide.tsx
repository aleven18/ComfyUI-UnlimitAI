/**
 * 新手引导组件
 * 
 * 首次打开项目时显示，引导用户完成基本流程
 */

import { useState, useEffect } from 'react';
import { X, Users, Film, Settings, Sparkles, ArrowRight } from 'lucide-react';

interface OnboardingGuideProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (tab: string) => void;
}

export function OnboardingGuide({ isOpen, onClose, onNavigate }: OnboardingGuideProps) {
  const [currentStep, setCurrentStep] = useState(0);
  
  useEffect(() => {
    // 检查是否已经显示过引导
    const hasSeenGuide = localStorage.getItem('has_seen_onboarding');
    if (hasSeenGuide) {
      onClose();
    }
  }, [onClose]);
  
  if (!isOpen) return null;
  
  const handleComplete = () => {
    localStorage.setItem('has_seen_onboarding', 'true');
    onClose();
  };
  
  const handleSkip = () => {
    localStorage.setItem('has_seen_onboarding', 'true');
    onClose();
  };
  
  const steps = [
    {
      title: '欢迎使用 UnlimitAI',
      description: '一个专业的AI驱动视频创作工具',
      content: (
        <div className="space-y-4">
          <p className="text-sm text-[var(--text-secondary)]">
            我们将引导您完成第一次创作流程，只需3步即可生成您的第一个分镜脚本。
          </p>
        </div>
      )
    },
    {
      title: '第1步：创建角色卡',
      description: '为故事中的角色建立档案',
      icon: <Users className="w-6 h-6" />,
      content: (
        <div className="space-y-3">
          <div className="bg-[var(--bg-primary)] p-3 rounded-lg">
            <p className="text-xs text-[var(--text-tertiary)] mb-2">两种创建方式：</p>
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-[var(--accent-primary)] mt-0.5" />
                <div>
                  <p className="text-sm font-medium">AI提取（推荐）</p>
                  <p className="text-xs text-[var(--text-tertiary)]">粘贴小说文本，自动识别角色</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Users className="w-4 h-4 text-[var(--text-tertiary)] mt-0.5" />
                <div>
                  <p className="text-sm font-medium">手动创建</p>
                  <p className="text-xs text-[var(--text-tertiary)]">填写角色信息、外貌、性格</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: '第2步：生成分镜',
      description: 'AI自动生成专业的分镜脚本',
      icon: <Film className="w-6 h-6" />,
      content: (
        <div className="space-y-3">
          <p className="text-sm text-[var(--text-secondary)]">
            输入小说文本，系统将：
          </p>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
              分析情节结构
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
              自动划分场景
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
              生成镜头语言
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
              应用角色信息
            </li>
          </ul>
        </div>
      )
    },
    {
      title: '准备工作',
      description: '开始之前，请确保已完成以下配置',
      icon: <Settings className="w-6 h-6" />,
      content: (
        <div className="space-y-3">
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
            <p className="text-sm font-medium text-yellow-500 mb-2">重要提示</p>
            <p className="text-xs text-[var(--text-secondary)]">
              请确保已在右上角⚙️设置中配置您的 API Key，否则无法使用AI功能。
            </p>
          </div>
          <p className="text-xs text-[var(--text-tertiary)]">
            API Key 用于调用 AI 模型进行角色提取和分镜生成
          </p>
        </div>
      )
    }
  ];
  
  const currentStepData = steps[currentStep];
  
  return (
    <>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" />
      
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-[var(--bg-primary)] rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
          {/* 头部 */}
          <div className="relative px-6 py-5 border-b border-[var(--border-subtle)]">
            {currentStepData.icon && (
              <div className="absolute top-5 right-6 text-[var(--accent-primary)]">
                {currentStepData.icon}
              </div>
            )}
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              {currentStepData.title}
            </h2>
            <p className="text-sm text-[var(--text-tertiary)] mt-1">
              {currentStepData.description}
            </p>
          </div>
          
          {/* 内容 */}
          <div className="px-6 py-6">
            {currentStepData.content}
          </div>
          
          {/* 进度指示器 */}
          <div className="px-6 pb-4">
            <div className="flex items-center gap-2">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`h-1.5 flex-1 rounded-full transition-all ${
                    index === currentStep 
                      ? 'bg-[var(--accent-primary)]' 
                      : index < currentStep 
                        ? 'bg-[var(--accent-primary)]/50' 
                        : 'bg-[var(--bg-tertiary)]'
                  }`}
                />
              ))}
            </div>
            <p className="text-xs text-[var(--text-tertiary)] mt-2 text-center">
              {currentStep + 1} / {steps.length}
            </p>
          </div>
          
          {/* 底部按钮 */}
          <div className="px-6 py-4 bg-[var(--bg-secondary)] flex items-center justify-between">
            <button
              onClick={handleSkip}
              className="text-sm text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
            >
              跳过引导
            </button>
            
            <div className="flex gap-2">
              {currentStep > 0 && (
                <button
                  onClick={() => setCurrentStep(currentStep - 1)}
                  className="px-4 py-2 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                >
                  上一步
                </button>
              )}
              
              {currentStep < steps.length - 1 ? (
                <button
                  onClick={() => setCurrentStep(currentStep + 1)}
                  className="px-6 py-2 bg-[var(--accent-primary)] text-white text-sm font-medium rounded-lg hover:opacity-90 transition-all flex items-center gap-2"
                >
                  下一步
                  <ArrowRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  onClick={handleComplete}
                  className="px-6 py-2 bg-[var(--accent-primary)] text-white text-sm font-medium rounded-lg hover:opacity-90 transition-all"
                >
                  开始创作
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
