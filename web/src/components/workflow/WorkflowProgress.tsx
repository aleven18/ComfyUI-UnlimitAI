/**
 * 工作流任务面板
 * 
 * 显示在右侧，动态显示用户执行的任务
 * 设计风格：简约、专业、高级
 */

import { useProjectStore } from '@/store/projectStore';

export function WorkflowProgress() {
  const { currentProject, tasks, updateTask, removeTask, clearTasks } = useProjectStore();
  
  if (!currentProject) {
    return null;
  }
  
  const getStatusIndicator = (status: string) => {
    switch (status) {
      case 'completed':
        return <div className="w-2 h-2 rounded-full bg-green-500" />;
      case 'running':
        return <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />;
      case 'failed':
        return <div className="w-2 h-2 rounded-full bg-red-500" />;
      default:
        return <div className="w-2 h-2 rounded-full bg-gray-400" />;
    }
  };
  
  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'running':
        return '运行中';
      case 'failed':
        return '失败';
      default:
        return '待执行';
    }
  };
  
  const handleRetry = (taskId: string) => {
    updateTask(taskId, { status: 'running' });
  };
  
  const handleInterrupt = (taskId: string) => {
    updateTask(taskId, { status: 'pending' });
  };
  
  const handleRemove = (taskId: string) => {
    removeTask(taskId);
  };
  
  const handleRefreshAll = () => {
    console.log('刷新所有任务');
  };
  
  const handleClearCompleted = () => {
    clearTasks();
  };
  
  const totalCost = tasks.reduce((sum, t) => sum + (t.cost || 0), 0);
  const completedCount = tasks.filter(t => t.status === 'completed').length;
  
  return (
    <div className="w-72 bg-[var(--bg-secondary)] border-l border-[var(--border-default)] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-[var(--border-default)]">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">任务列表</h3>
          <div className="flex gap-2">
            {tasks.length > 0 && (
              <button 
                onClick={handleClearCompleted}
                className="text-xs px-2 py-1 border border-[var(--border-default)] rounded hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                清空
              </button>
            )}
          </div>
        </div>
      </div>
      
      {/* Tasks List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {tasks.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm text-[var(--text-tertiary)]">暂无任务</p>
            <p className="text-xs text-[var(--text-tertiary)] mt-1">执行操作时会自动创建任务</p>
          </div>
        ) : (
          tasks.map((task) => (
            <div 
              key={task.id}
              className="border border-[var(--border-default)] rounded p-3"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getStatusIndicator(task.status)}
                  <span className="text-sm font-medium text-[var(--text-primary)]">{task.name}</span>
                </div>
                {task.status !== 'running' && task.status !== 'pending' && (
                  <button 
                    onClick={() => handleRemove(task.id)}
                    className="text-xs text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
                  >
                    ×
                  </button>
                )}
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-[var(--text-tertiary)]">
                  {getStatusLabel(task.status)}
                </span>
                
                <div className="flex gap-2">
                  {task.status === 'failed' && (
                    <button 
                      onClick={() => handleRetry(task.id)}
                      className="text-xs px-2 py-1 border border-[var(--border-default)] rounded hover:bg-[var(--bg-tertiary)] transition-colors"
                    >
                      重试
                    </button>
                  )}
                  
                  {task.status === 'running' && (
                    <button 
                      onClick={() => handleInterrupt(task.id)}
                      className="text-xs px-2 py-1 border border-red-500/30 text-red-500 rounded hover:bg-red-500/10 transition-colors"
                    >
                      中断
                    </button>
                  )}
                  
                  {task.status === 'completed' && task.cost !== undefined && (
                    <span className="text-xs text-[var(--text-tertiary)]">
                      ${task.cost.toFixed(4)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* Footer */}
      {tasks.length > 0 && (
        <div className="p-4 border-t border-[var(--border-default)]">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[var(--text-tertiary)]">任务状态</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-[var(--text-secondary)]">
                {completedCount}/{tasks.length} 完成
              </span>
              {totalCost > 0 && (
                <span className="text-xs font-medium text-[var(--text-primary)]">
                  ${totalCost.toFixed(4)}
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
