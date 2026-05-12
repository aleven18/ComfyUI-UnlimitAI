import { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle, Clock, AlertCircle, DollarSign, Loader2 } from 'lucide-react';

interface ModuleResources {
  images?: unknown[];
  videos?: unknown[];
  audios?: unknown[];
}

interface ModuleStatus {
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  data?: {
    scene_count?: number;
    total_characters?: number;
    shot_count?: number;
    total_duration?: number;
    final_video_url?: string;
    resources?: ModuleResources;
    [key: string]: unknown;
  };
  error?: string;
  cost?: number;
  updated_at?: string;
}

interface WorkflowState {
  project_id: string;
  created_at: string;
  current_module: number;
  modules: {
    [key: string]: ModuleStatus;
  };
  total_cost?: number;
}

interface ProgressTrackerProps {
  projectId: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function ProgressTracker({ 
  projectId, 
  autoRefresh = true, 
  refreshInterval = 5000 
}: ProgressTrackerProps) {
  const [workflowState, setWorkflowState] = useState<WorkflowState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const moduleNames: { [key: string]: string } = {
    '1_novel_analysis': '小说分析',
    '2_character_creation': '角色创建',
    '3_storyboard': '分镜脚本',
    '4_resource_generation': '资源生成',
    '5_final_composition': '合成输出'
  };

  const moduleIcons: { [key: string]: string } = {
    '1_novel_analysis': '📖',
    '2_character_creation': '🎭',
    '3_storyboard': '🎬',
    '4_resource_generation': '🎨',
    '5_final_composition': '🎥'
  };

  const fetchProgress = async () => {
    if (!projectId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8188/api/workflow/state/${projectId}`);
      
      if (!response.ok) {
        throw new Error('获取状态失败');
      }

      const data = await response.json();
      
      if (data.success) {
        setWorkflowState(data.state);
        setLastUpdate(new Date());
      } else {
        throw new Error(data.error || '获取状态失败');
      }
    } catch (err: unknown) {
      setError((err instanceof Error ? err.message : String(err)));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProgress();
    
    if (autoRefresh) {
      const interval = setInterval(fetchProgress, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [projectId, autoRefresh, refreshInterval]);

  if (!workflowState) {
    return (
      <div className="bg-[var(--bg-elevated)] rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">项目进度</h3>
          <button
            onClick={fetchProgress}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-1.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            刷新
          </button>
        </div>
        
        {error && (
          <div className="p-3 bg-red-50 text-red-600 rounded-lg mb-4">
            {error}
          </div>
        )}
        
        <p className="text-gray-500 text-center py-8">
          {isLoading ? '加载中...' : '暂无进度信息'}
        </p>
      </div>
    );
  }

  const completedModules = Object.values(workflowState.modules).filter(
    m => m.status === 'completed'
  ).length;
  const totalModules = Object.keys(workflowState.modules).length;
  const progress = (completedModules / totalModules) * 100;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in_progress':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '已完成';
      case 'in_progress': return '进行中';
      case 'error': return '失败';
      default: return '等待中';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50';
      case 'in_progress': return 'text-blue-600 bg-blue-50';
      case 'error': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="bg-[var(--bg-elevated)] rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">项目进度</h3>
        <div className="flex items-center gap-2">
          {lastUpdate && (
            <span className="text-xs text-gray-500">
              最后更新: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchProgress}
            disabled={isLoading}
            className="flex items-center gap-1 px-3 py-1.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 text-sm"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            刷新
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 text-red-600 rounded-lg mb-4 flex items-start gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">获取进度失败</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* 总体进度 */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">总进度</span>
          <span className="text-lg font-bold text-blue-600">
            {completedModules}/{totalModules} 模块 ({progress.toFixed(0)}%)
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div 
            className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* 成本统计 */}
      {workflowState.total_cost !== undefined && (
        <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center gap-2 mb-1">
            <DollarSign className="w-4 h-4 text-green-600" />
            <span className="text-sm text-gray-600">累计成本</span>
          </div>
          <p className="text-2xl font-bold text-green-600">
            ${workflowState.total_cost.toFixed(4)}
          </p>
        </div>
      )}

      {/* 模块详情 */}
      <div className="space-y-3">
        {Object.entries(workflowState.modules).map(([key, module]) => (
          <div 
            key={key}
            className={`border rounded-lg overflow-hidden transition-all ${
              module.status === 'in_progress' ? 'border-blue-300 shadow-sm' : 'border-gray-200'
            }`}
          >
            <div className="p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{moduleIcons[key]}</span>
                  <div>
                    <p className="font-medium text-gray-800">
                      {moduleNames[key]}
                    </p>
                    <span className={`text-xs px-2 py-1 rounded ${getStatusColor(module.status)}`}>
                      {getStatusText(module.status)}
                    </span>
                  </div>
                </div>
                {getStatusIcon(module.status)}
              </div>

              {/* 模块数据预览 */}
              {module.status === 'completed' && module.data && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  {key === '1_novel_analysis' && (
                    <p className="text-sm text-gray-600">
                      场景数: {module.data.scene_count || 0}
                    </p>
                  )}
                  {key === '2_character_creation' && (
                    <p className="text-sm text-gray-600">
                      角色数: {module.data.total_characters || 0}
                    </p>
                  )}
                  {key === '3_storyboard' && (
                    <p className="text-sm text-gray-600">
                      镜头数: {module.data.shot_count || 0} | 
                      总时长: {module.data.total_duration || 0}秒
                    </p>
                  )}
                  {key === '4_resource_generation' && module.data.resources && (
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>图像: {module.data.resources.images?.length || 0}张</p>
                      <p>视频: {module.data.resources.videos?.length || 0}个</p>
                      <p>音频: {module.data.resources.audios?.length || 0}个</p>
                    </div>
                  )}
                  {key === '5_final_composition' && (
                    <p className="text-sm text-gray-600">
                      视频: {module.data.final_video_url || '生成中...'}
                    </p>
                  )}
                  {module.cost !== undefined && (
                    <p className="text-xs text-green-600 mt-2">
                      成本: ${module.cost.toFixed(4)}
                    </p>
                  )}
                </div>
              )}

              {/* 错误信息 */}
              {module.status === 'error' && module.error && (
                <div className="mt-3 pt-3 border-t border-red-200">
                  <p className="text-sm text-red-600">{module.error}</p>
                </div>
              )}

              {/* 更新时间 */}
              {module.updated_at && (
                <p className="text-xs text-gray-400 mt-2">
                  更新于: {new Date(module.updated_at).toLocaleString()}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 项目信息 */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          项目ID: {workflowState.project_id}
        </p>
        <p className="text-xs text-gray-500">
          创建时间: {new Date(workflowState.created_at).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
