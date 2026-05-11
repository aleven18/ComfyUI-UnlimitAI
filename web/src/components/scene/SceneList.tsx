import { Plus, Film, Clock, User, Trash2, Edit } from 'lucide-react';
import { useProjectStore } from '@/store/projectStore';

export function SceneList() {
  const { scenes, characters, createScene, deleteScene, selectScene } = useProjectStore();

  const handleCreateScene = () => {
    createScene({
      description: '新场景',
      shotSize: 'medium',
      cameraMove: 'static',
      duration: 5
    });
  };

  const getCharacterNames = (characterIds: string[]) => {
    return characterIds
      .map(id => characters.find(c => c.id === id)?.name)
      .filter(Boolean)
      .join(', ');
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold">分镜列表</h2>
          <p className="text-sm text-[var(--text-tertiary)] mt-1">共 {scenes.length} 个场景</p>
        </div>
        <button
          onClick={handleCreateScene}
          className="px-4 py-2 bg-[var(--accent-primary)] text-white rounded-lg hover:opacity-90 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          添加场景
        </button>
      </div>

      {scenes.length === 0 ? (
        <div className="text-center py-12">
          <Film className="w-16 h-16 mx-auto mb-4 text-[var(--text-tertiary)]" />
          <p className="text-[var(--text-tertiary)] mb-2">还没有创建场景</p>
          <p className="text-sm text-[var(--text-tertiary)]">点击"添加场景"开始</p>
        </div>
      ) : (
        <div className="space-y-4">
          {scenes.map(scene => (
            <div
              key={scene.id}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-2 py-1 bg-[var(--accent-primary)] bg-opacity-10 text-[var(--accent-primary)] text-sm font-medium rounded">
                      场景 {scene.shotNumber}
                    </span>
                    <h3 className="font-medium text-[var(--text-primary)]">{scene.description}</h3>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-[var(--text-tertiary)]">
                    <span>景别: {getShotSizeLabel(scene.shotSize)}</span>
                    <span>运镜: {getCameraMoveLabel(scene.cameraMove)}</span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {scene.duration}秒
                    </span>
                  </div>

                  {scene.characters.length > 0 && (
                    <div className="flex items-center gap-2 mt-2 text-sm text-[var(--text-secondary)]">
                      <User className="w-3 h-3" />
                      <span>{getCharacterNames(scene.characters)}</span>
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => selectScene(scene)}
                    className="px-3 py-1.5 border border-[var(--border-default)] rounded text-sm hover:bg-[var(--bg-tertiary)] flex items-center gap-1"
                  >
                    <Edit className="w-3 h-3" />
                    编辑
                  </button>
                  <button
                    onClick={() => deleteScene(scene.id)}
                    className="px-3 py-1.5 border border-red-300 text-red-600 rounded text-sm hover:bg-red-50"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function getShotSizeLabel(size: string): string {
  const labels: Record<string, string> = {
    'extreme-long': '远景',
    'long': '全景',
    'medium-long': '中远景',
    'medium': '中景',
    'medium-close': '中近景',
    'close': '近景',
    'extreme-close': '特写'
  };
  return labels[size] || size;
}

function getCameraMoveLabel(move: string): string {
  const labels: Record<string, string> = {
    'static': '静止',
    'dolly-in': '推镜',
    'dolly-out': '拉镜',
    'dolly-left': '左移',
    'dolly-right': '右移',
    'pan-left': '左摇',
    'pan-right': '右摇',
    'tilt-up': '上仰',
    'tilt-down': '下俯',
    'zoom-in': '放大',
    'zoom-out': '缩小'
  };
  return labels[move] || move;
}
