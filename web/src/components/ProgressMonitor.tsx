import { Activity, AlertCircle } from 'lucide-react';

interface ProgressMonitorProps {
  progress: number;
  currentNode: string | null;
  logs: string[];
  error: string | null;
}

export function ProgressMonitor({ progress, currentNode, logs, error }: ProgressMonitorProps) {
  if (logs.length === 0 && !error) return null;

  return (
    <div className="card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-[var(--accent-primary)]" />
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">转换进度</h2>
      </div>

      {progress > 0 && (
        <div className="mb-4">
          <div className="flex justify-between text-sm text-[var(--text-secondary)] mb-1">
            <span>进度</span>
            <span>{progress.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-[var(--bg-tertiary)] rounded-full h-3">
            <div
              className="bg-[var(--accent-primary)] h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {currentNode && (
        <div className="mb-4 p-3 bg-[var(--bg-tertiary)] rounded-lg border border-[var(--border-default)]">
          <p className="text-sm text-[var(--text-tertiary)]">当前节点</p>
          <p className="font-semibold text-[var(--accent-primary)]">{currentNode}</p>
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-[var(--accent-error)] bg-opacity-10 rounded-lg border border-[var(--accent-error)] border-opacity-30">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-[var(--accent-error)] flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-[var(--accent-error)]">错误</p>
              <p className="text-sm text-[var(--accent-error)] opacity-80">{error}</p>
            </div>
          </div>
        </div>
      )}

      {logs.length > 0 && (
        <div className="bg-[var(--bg-primary)] rounded-lg p-4 max-h-64 overflow-y-auto border border-[var(--border-subtle)]">
          <div className="space-y-1 font-mono text-xs">
            {logs.map((log, idx) => (
              <div key={idx} className="text-[var(--text-secondary)]">
                {log}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
