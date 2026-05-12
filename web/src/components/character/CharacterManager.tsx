import { useState } from 'react';
import { Plus, Search, User, Mic, Film, Trash2, Edit, MessageCircle } from 'lucide-react';
import { useProjectStore } from '@/store/projectStore';
import { CharacterCard } from '@/types/project';
import { CharacterEditor } from './CharacterEditor';
import { AIGuideCharacterCreation } from './AIGuideCharacterCreation';

export function CharacterManager() {
  const { characters, createCharacter, deleteCharacter } = useProjectStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [editingCharacter, setEditingCharacter] = useState<CharacterCard | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [showAIGuide, setShowAIGuide] = useState(false);
  
  const filteredCharacters = characters.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  const handleCreateNew = () => {
    setIsCreating(true);
    setEditingCharacter(null);
  };
  
  const handleEdit = (character: CharacterCard) => {
    setEditingCharacter(character);
    setIsCreating(false);
  };
  
  const handleDelete = (id: string) => {
    if (confirm('确定要删除这个角色吗？')) {
      deleteCharacter(id);
    }
  };
  
  const handleSave = (characterData: Partial<CharacterCard>) => {
    if (isCreating) {
      createCharacter(characterData);
    } else if (editingCharacter) {
      useProjectStore.getState().updateCharacter(editingCharacter.id, characterData);
    }
    setEditingCharacter(null);
    setIsCreating(false);
  };
  
  const handleAIGuideCreate = (characterData: Record<string, unknown>) => {
    createCharacter(characterData);
  };
  
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">角色卡管理</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAIGuide(true)}
            className="btn-secondary flex items-center gap-2"
          >
            <MessageCircle className="w-4 h-4" />
            AI引导创建
          </button>
          <button
            onClick={handleCreateNew}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            创建角色卡
          </button>
        </div>
      </div>
      
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--text-tertiary)] w-4 h-4" />
          <input
            type="text"
            placeholder="搜索角色..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-base pl-10"
          />
        </div>
      </div>
      
      {filteredCharacters.length === 0 ? (
        <div className="text-center py-12">
          <User className="w-16 h-16 mx-auto mb-4 text-[var(--text-tertiary)] opacity-50" />
          <p className="text-[var(--text-secondary)] mb-2">还没有创建角色</p>
          <p className="text-sm text-[var(--text-tertiary)]">点击"创建角色卡"开始</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredCharacters.map(character => (
            <div
              key={character.id}
              className="border border-[var(--border-default)] rounded-lg overflow-hidden hover:shadow-md transition-shadow bg-[var(--bg-primary)]"
            >
              <div className="aspect-square bg-[var(--bg-secondary)] flex items-center justify-center">
                {character.appearance.referenceImage ? (
                  <img
                    src={character.appearance.referenceImage}
                    alt={character.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <User className="w-16 h-16 text-[var(--text-tertiary)]" />
                )}
              </div>
              
              <div className="p-3">
                <h3 className="font-medium text-[var(--text-primary)] truncate">{character.name}</h3>
                <p className="text-sm text-[var(--text-secondary)] mt-1">
                  {getRoleLabel(character.role)}
                </p>
                
                <div className="flex items-center gap-2 mt-2 text-xs text-[var(--text-tertiary)]">
                  {character.voice.voiceId && (
                    <span className="flex items-center gap-1">
                      <Mic className="w-3 h-3" />
                      已配置音色
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Film className="w-3 h-3" />
                    {character.usage.scenes.length}场
                  </span>
                </div>
                
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => handleEdit(character)}
                    className="flex-1 px-3 py-1.5 border border-[var(--border-default)] rounded text-sm hover:bg-[var(--bg-hover)] flex items-center justify-center gap-1 text-[var(--text-primary)]"
                  >
                    <Edit className="w-3 h-3" />
                    编辑
                  </button>
                  <button
                    onClick={() => handleDelete(character.id)}
                    className="px-3 py-1.5 border border-[var(--accent-error)] text-[var(--accent-error)] rounded text-sm hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Character Editor Modal */}
      {(editingCharacter || isCreating) && (
        <CharacterEditor
          character={editingCharacter}
          onSave={handleSave}
          onClose={() => {
            setEditingCharacter(null);
            setIsCreating(false);
          }}
        />
      )}
      
      {/* AI Guide Character Creation Modal */}
      <AIGuideCharacterCreation
        isOpen={showAIGuide}
        onClose={() => setShowAIGuide(false)}
        onCreate={handleAIGuideCreate}
      />
    </div>
  );
}

function getRoleLabel(role: string): string {
  const labels: Record<string, string> = {
    protagonist: '主角',
    supporting: '配角',
    antagonist: '反派',
    minor: '次要角色'
  };
  return labels[role] || role;
}
