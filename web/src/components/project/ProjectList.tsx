import { useState } from 'react';
import { Plus, Film, Users, Search, MoreVertical, Trash2 } from 'lucide-react';
import { useProjectStore } from '@/store/projectStore';
import { DramaProject } from '@/types/project';
import { CreateProjectModal } from '@/components/common/CreateProjectModal';

interface ProjectCardProps {
  project: DramaProject;
  isSelected: boolean;
  onClick: () => void;
  onDelete: () => void;
}

function ProjectCard({ project, isSelected, onClick, onDelete }: ProjectCardProps) {
  const [showMenu, setShowMenu] = useState(false);
  
  return (
    <div className="relative">
      <button
        onClick={onClick}
        className={`
          w-full text-left rounded-lg overflow-hidden transition-all duration-200
          ${isSelected 
            ? 'bg-[var(--bg-tertiary)] border-l-[3px] border-l-[var(--accent-primary)]' 
            : 'bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] border-l-[3px] border-l-transparent'
          }
        `}
      >
        {project.coverImage ? (
          <img 
            src={project.coverImage} 
            alt={project.name}
            className="w-full h-28 object-cover"
          />
        ) : (
          <div className="w-full h-28 bg-[var(--bg-tertiary)] flex items-center justify-center">
            <Film className="w-10 h-10 text-[var(--text-tertiary)] opacity-50" />
          </div>
        )}
        
        <div className="p-3">
          <h3 className="font-medium text-sm truncate">{project.name}</h3>
          <p className="text-xs text-[var(--text-tertiary)] mt-1">{project.genre}</p>
          
          <div className="flex items-center gap-3 mt-2 text-xs text-[var(--text-tertiary)]">
            <span className="flex items-center gap-1">
              <Users className="w-3 h-3" />
              {project.characters}
            </span>
            <span className="flex items-center gap-1">
              <Film className="w-3 h-3" />
              {project.scenes}
            </span>
          </div>
        </div>
      </button>
      
      <button
        onClick={(e) => {
          e.stopPropagation();
          setShowMenu(!showMenu);
        }}
        className="absolute top-2 right-2 p-1.5 rounded-lg bg-[var(--bg-primary)] hover:bg-[var(--bg-tertiary)] transition-all shadow-sm"
      >
        <MoreVertical className="w-4 h-4 text-[var(--text-secondary)]" />
      </button>
      
      {showMenu && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setShowMenu(false)}
          />
          <div className="absolute top-10 right-2 z-20 bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg shadow-lg overflow-hidden min-w-[120px]">
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (confirm(`确定要删除项目"${project.name}"吗？此操作不可撤销。`)) {
                  onDelete();
                  setShowMenu(false);
                }
              }}
              className="w-full px-3 py-2 text-left text-sm hover:bg-[var(--bg-hover)] text-[var(--accent-error)] flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              删除项目
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export function ProjectList() {
  const { projects, currentProject, loadProject, createProject, deleteProject } = useProjectStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  const filteredProjects = projects.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.genre.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  const handleCreateProject = (data: { name: string; description?: string; genre?: string }) => {
    const id = createProject(data);
    loadProject(id);
  };
  
  const handleDeleteProject = (projectId: string) => {
    deleteProject(projectId);
  };
  
  return (
    <div className="w-60 bg-[var(--bg-secondary)] h-full flex flex-col border-r border-[var(--border-subtle)]">
      <div className="p-4 border-b border-[var(--border-subtle)]">
        <h2 className="text-sm font-semibold text-[var(--text-primary)]">我的项目</h2>
      </div>
      
      <div className="p-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" />
          <input
            type="text"
            placeholder="搜索项目..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-base pl-9 h-8 text-xs"
          />
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {filteredProjects.length === 0 ? (
          <div className="empty-state">
            <Film className="empty-state-icon" />
            <p className="empty-state-text">还没有项目</p>
            <p className="text-xs text-[var(--text-tertiary)] mt-1">点击下方按钮创建</p>
          </div>
        ) : (
          filteredProjects.map(project => (
            <div key={project.id} className="group">
              <ProjectCard
                project={project}
                isSelected={currentProject?.id === project.id}
                onClick={() => loadProject(project.id)}
                onDelete={() => handleDeleteProject(project.id)}
              />
            </div>
          ))
        )}
      </div>
      
      <div className="p-3 border-t border-[var(--border-subtle)]">
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          新建项目
        </button>
      </div>
      
      <CreateProjectModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreate={handleCreateProject}
      />
    </div>
  );
}
