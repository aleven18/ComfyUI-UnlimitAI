import { useState } from 'react';
import { Film, Clock, Camera, Volume2, Music, ChevronDown, ChevronUp } from 'lucide-react';

interface StoryboardShot {
  shot_id: number;
  scene_number: number;
  shot_type: string;
  camera_movement: string;
  angle: string;
  description: string;
  action: string;
  dialogue: string;
  sound: string;
  music: string;
  duration: number;
  transition: string;
  emotion: string;
  visual_prompt: string;
}

interface StoryboardViewerProps {
  storyboard: {
    title: string;
    total_duration: number;
    shots: StoryboardShot[];
  };
}

export function StoryboardViewer({ storyboard }: StoryboardViewerProps) {
  const [expandedShot, setExpandedShot] = useState<number | null>(null);

  if (!storyboard || !storyboard.shots) {
    return null;
  }

  const shotTypeColors: Record<string, string> = {
    '大远景': 'bg-[var(--accent-primary)] bg-opacity-10 text-[var(--accent-primary)]',
    '远景': 'bg-[var(--accent-primary)] bg-opacity-10 text-[var(--accent-primary)]',
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
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">分镜脚本</h2>
        </div>
        <div className="flex items-center gap-4 text-sm text-[var(--text-secondary)]">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{storyboard.total_duration}秒</span>
          </div>
          <div className="flex items-center gap-1">
            <Camera className="w-4 h-4" />
            <span>{storyboard.shots.length}个镜头</span>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        {storyboard.shots.map((shot) => (
          <div key={shot.shot_id} className="border rounded-lg overflow-hidden">
            <div
              className="flex items-center justify-between p-3 cursor-pointer hover:bg-[var(--bg-tertiary)]"
              onClick={() => setExpandedShot(expandedShot === shot.shot_id ? null : shot.shot_id)}
            >
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 bg-[var(--accent-primary)] bg-opacity-10 rounded-full font-bold text-[var(--accent-primary)]">
                  {shot.shot_id}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded ${shotTypeColors[shot.shot_type] || 'bg-[var(--bg-tertiary)]'}`}>
                      {shot.shot_type}
                    </span>
                    <span className="text-sm text-[var(--text-secondary)]">{shot.camera_movement}</span>
                  </div>
                  <p className="text-sm text-[var(--text-primary)] mt-1">{shot.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium text-[var(--text-secondary)]">{shot.duration}秒</span>
                {expandedShot === shot.shot_id ?
                  <ChevronUp className="w-5 h-5 text-[var(--text-tertiary)]" /> :
                  <ChevronDown className="w-5 h-5 text-[var(--text-tertiary)]" />
                }
              </div>
            </div>

            {expandedShot === shot.shot_id && (
              <div className="border-t bg-[var(--bg-tertiary)] p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-[var(--text-tertiary)]">拍摄角度:</span>
                    <span className="ml-2 text-[var(--text-primary)]">{shot.angle}</span>
                  </div>
                  <div>
                    <span className="text-[var(--text-tertiary)]">转场方式:</span>
                    <span className="ml-2 text-[var(--text-primary)]">{shot.transition}</span>
                  </div>
                  <div>
                    <span className="text-[var(--text-tertiary)]">情绪氛围:</span>
                    <span className="ml-2 text-[var(--text-primary)]">{shot.emotion}</span>
                  </div>
                  <div>
                    <span className="text-[var(--text-tertiary)]">场景编号:</span>
                    <span className="ml-2 text-[var(--text-primary)]">{shot.scene_number}</span>
                  </div>
                </div>

                {shot.action && (
                  <div className="mt-3">
                    <span className="text-[var(--text-tertiary)] text-sm">动作:</span>
                    <p className="text-[var(--text-primary)] mt-1">{shot.action}</p>
                  </div>
                )}

                {shot.dialogue && (
                  <div className="mt-3 flex items-start gap-2">
                    <Volume2 className="w-4 h-4 text-[var(--text-tertiary)] mt-0.5" />
                    <div>
                      <span className="text-[var(--text-tertiary)] text-sm">对话/旁白:</span>
                      <p className="text-[var(--text-primary)] mt-1">{shot.dialogue}</p>
                    </div>
                  </div>
                )}

                {(shot.sound || shot.music) && (
                  <div className="mt-3 flex items-start gap-2">
                    <Music className="w-4 h-4 text-[var(--text-tertiary)] mt-0.5" />
                    <div>
                      <span className="text-[var(--text-tertiary)] text-sm">音效/配乐:</span>
                      <p className="text-[var(--text-primary)] mt-1">
                        {shot.sound && `音效: ${shot.sound}`}
                        {shot.sound && shot.music && ' | '}
                        {shot.music && `配乐: ${shot.music}`}
                      </p>
                    </div>
                  </div>
                )}

                {shot.visual_prompt && (
                  <div className="mt-3 p-2 bg-[var(--accent-primary)] bg-opacity-5 rounded">
                    <span className="text-[var(--text-tertiary)] text-sm">英文提示词:</span>
                    <p className="text-[var(--text-primary)] mt-1 text-sm font-mono">{shot.visual_prompt}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-[var(--bg-tertiary)] rounded-lg">
        <h3 className="text-sm font-medium text-[var(--text-secondary)] mb-2">时间线</h3>
        <div className="flex gap-1">
          {storyboard.shots.map((shot, index) => {
            const widthPercent = storyboard.total_duration > 0 ? (shot.duration / storyboard.total_duration) * 100 : 0;
            const colors = ['bg-blue-400', 'bg-green-400', 'bg-yellow-400', 'bg-orange-400', 'bg-red-400'];
            const color = colors[index % colors.length];

            return (
              <div
                key={shot.shot_id}
                className={`${color} h-8 rounded flex items-center justify-center text-xs text-white font-medium cursor-pointer hover:opacity-80`}
                style={{ width: `${widthPercent}%`, minWidth: '20px' }}
                title={`镜头${shot.shot_id}: ${shot.duration}秒`}
              >
                {widthPercent > 5 && shot.shot_id}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
