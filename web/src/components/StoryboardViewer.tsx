import { useState } from 'react';
import { Film, Clock, Camera, Volume2, ChevronDown, ChevronUp } from 'lucide-react';
import { Shot } from '@/types/project';

interface StoryboardViewerProps {
  shots: Shot[];
  title?: string;
}

export function StoryboardViewer({ shots, title = '分镜脚本' }: StoryboardViewerProps) {
  const [expandedShot, setExpandedShot] = useState<number | null>(null);

  if (!shots || shots.length === 0) {
    return null;
  }

  const totalDuration = shots.reduce((sum, s) => sum + s.duration, 0);

  const shotTypeLabels: Record<string, string> = {
    'extreme-long': '大远景',
    'long': '远景',
    'full': '全景',
    'medium': '中景',
    'medium-close': '近景',
    'close': '特写',
    'extreme-close': '大特写',
  };

  const shotTypeColors: Record<string, string> = {
    '大远景': 'bg-blue-100 text-blue-700',
    '远景': 'bg-blue-100 text-blue-700',
    '全景': 'bg-green-100 text-green-700',
    '中景': 'bg-yellow-100 text-yellow-700',
    '近景': 'bg-orange-100 text-orange-700',
    '特写': 'bg-red-100 text-red-700',
    '大特写': 'bg-red-100 text-red-800',
  };

  return (
    <div className="bg-[var(--bg-elevated)] rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Film className="w-5 h-5 text-[var(--accent-primary)]" />
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">{title}</h2>
        </div>
        <div className="flex items-center gap-4 text-sm text-[var(--text-secondary)]">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{totalDuration}秒</span>
          </div>
          <div className="flex items-center gap-1">
            <Camera className="w-4 h-4" />
            <span>{shots.length}个镜头</span>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        {shots.map((shot) => {
          const shotTypeLabel = shotTypeLabels[shot.shotSize] || shot.shotSize || '中景';
          const colorClass = shotTypeColors[shotTypeLabel] || 'bg-[var(--bg-tertiary)]';
          return (
            <div key={shot.id} className="border rounded-lg overflow-hidden">
              <div
                className="flex items-center justify-between p-3 cursor-pointer hover:bg-[var(--bg-tertiary)]"
                onClick={() => setExpandedShot(expandedShot === shot.shotNumber ? null : shot.shotNumber)}
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-10 h-10 bg-[var(--accent-primary)] bg-opacity-10 rounded-full font-bold text-[var(--accent-primary)]">
                    {shot.shotNumber}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-1 rounded ${colorClass}`}>
                        {shotTypeLabel}
                      </span>
                      <span className="text-sm text-[var(--text-secondary)]">{shot.cameraMove}</span>
                    </div>
                    <p className="text-sm text-[var(--text-primary)] mt-1">{shot.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-[var(--text-secondary)]">{shot.duration}秒</span>
                  {expandedShot === shot.shotNumber ?
                    <ChevronUp className="w-5 h-5 text-[var(--text-tertiary)]" /> :
                    <ChevronDown className="w-5 h-5 text-[var(--text-tertiary)]" />
                  }
                </div>
              </div>

              {expandedShot === shot.shotNumber && (
                <div className="border-t bg-[var(--bg-tertiary)] p-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-[var(--text-tertiary)]">景别:</span>
                      <span className="ml-2 text-[var(--text-primary)]">{shotTypeLabel}</span>
                    </div>
                    <div>
                      <span className="text-[var(--text-tertiary)]">运镜:</span>
                      <span className="ml-2 text-[var(--text-primary)]">{shot.cameraMove}</span>
                    </div>
                  </div>

                  {shot.prompt && (
                    <div className="mt-3">
                      <span className="text-[var(--text-tertiary)] text-sm">提示词:</span>
                      <p className="text-[var(--text-primary)] mt-1">{shot.prompt}</p>
                    </div>
                  )}

                  {shot.notes && (
                    <div className="mt-3">
                      <span className="text-[var(--text-tertiary)] text-sm">备注:</span>
                      <p className="text-[var(--text-primary)] mt-1">{shot.notes}</p>
                    </div>
                  )}

                  {shot.dialogues && shot.dialogues.length > 0 && (
                    <div className="mt-3 flex items-start gap-2">
                      <Volume2 className="w-4 h-4 text-[var(--text-tertiary)] mt-0.5" />
                      <div>
                        <span className="text-[var(--text-tertiary)] text-sm">对话/旁白:</span>
                        {shot.dialogues.map((d, i) => (
                          <p key={i} className="text-[var(--text-primary)] mt-1">
                            {d.characterId}: {d.text}
                            {d.emotion && <span className="text-[var(--text-tertiary)] ml-2">({d.emotion})</span>}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                  {shot.prompt && (
                    <div className="mt-3 p-2 bg-[var(--accent-primary)] bg-opacity-5 rounded">
                      <span className="text-[var(--text-tertiary)] text-sm">英文提示词:</span>
                      <p className="text-[var(--text-primary)] mt-1 text-sm font-mono">{shot.prompt}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 p-4 bg-[var(--bg-tertiary)] rounded-lg">
        <h3 className="text-sm font-medium text-[var(--text-secondary)] mb-2">时间线</h3>
        <div className="flex gap-1">
          {shots.map((shot, index) => {
            const widthPercent = totalDuration > 0 ? (shot.duration / totalDuration) * 100 : 0;
            const colors = ['bg-blue-400', 'bg-green-400', 'bg-yellow-400', 'bg-orange-400', 'bg-red-400'];
            const color = colors[index % colors.length];

            return (
              <div
                key={shot.id}
                className={`${color} h-8 rounded flex items-center justify-center text-xs text-white font-medium cursor-pointer hover:opacity-80`}
                style={{ width: `${widthPercent}%`, minWidth: '20px' }}
                title={`镜头${shot.shotNumber}: ${shot.duration}秒`}
              >
                {widthPercent > 5 && shot.shotNumber}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
