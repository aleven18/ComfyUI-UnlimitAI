import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { DramaProject, CharacterCard, Shot, ProjectSettings, Task } from '@/types/project';
import { saveGlobalApiKey } from '@/lib/unified-config';

interface ProjectState {
  currentProject: DramaProject | null;
  projects: DramaProject[];
  
  characters: CharacterCard[];
  selectedCharacter: CharacterCard | null;
  
  scenes: Shot[];
  selectedScene: Shot | null;
  
  settings: ProjectSettings;
  
  tasks: Task[];
  
  workflowStatus: {
    isGenerating: boolean;
    currentStep: string;
    progress: number;
    errors: string[];
  };
  
  createProject: (project: Partial<DramaProject>) => string;
  loadProject: (projectId: string) => void;
  saveProject: () => void;
  updateProject: (updates: Partial<DramaProject>) => void;
  deleteProject: (projectId: string) => void;
  
  createCharacter: (character: Partial<CharacterCard>) => string;
  updateCharacter: (id: string, updates: Partial<CharacterCard>) => void;
  deleteCharacter: (id: string) => void;
  selectCharacter: (character: CharacterCard | null) => void;
  
  createScene: (scene: Partial<Shot>) => string;
  updateScene: (id: string, updates: Partial<Shot>) => void;
  deleteScene: (id: string) => void;
  selectScene: (scene: Shot | null) => void;
  reorderScenes: (fromIndex: number, toIndex: number) => void;
  
  updateSettings: (settings: Partial<ProjectSettings>) => void;
  
  addTask: (task: Partial<Task>) => string;
  updateTask: (id: string, updates: Partial<Task>) => void;
  removeTask: (id: string) => void;
  clearTasks: () => void;
  
  setWorkflowStatus: (status: Partial<ProjectState['workflowStatus']>) => void;
}

const generateId = () => {
  return crypto.randomUUID();
};

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      currentProject: null,
      projects: [],
      characters: [],
      selectedCharacter: null,
      scenes: [],
      selectedScene: null,
      settings: {
        style: 'realistic',
        aspectRatio: '16:9',
        defaultTextModel: 'deepseek-chat',
        defaultImageModel: 'doubao-seedream-4-0-250828',  // 豆包图像模型（最快）
        defaultVideoModel: 'doubao-seedance-1-0-lite-i2v-250428',  // 豆包视频模型（角色一致性最佳）
        defaultAudioEngine: 'minimax',
        defaultTTSModel: 'tts-1',  // TTS语音合成模型（最快）
        defaultImageSize: '1920x1080',
        defaultVideoFPS: 24,
        apiKey: ''
      },
      tasks: [],
      workflowStatus: {
        isGenerating: false,
        currentStep: '',
        progress: 0,
        errors: []
      },
      
      createProject: (project) => {
        const id = generateId();
        const newProject: DramaProject = {
          id,
          name: project.name || '未命名项目',
          coverImage: project.coverImage || '',
          description: project.description || '',
          genre: project.genre || '都市言情',
          status: 'draft',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          characters: 0,
          scenes: 0,
          duration: 0,
          tags: project.tags || [],
          targetPlatform: project.targetPlatform || []
        };
        
        set(state => ({
          projects: [...state.projects, newProject],
          currentProject: newProject,
          characters: [],
          scenes: []
        }));
        
        return id;
      },
      
      loadProject: (projectId) => {
        const project = get().projects.find(p => p.id === projectId);
        if (project) {
          const savedChars = (get() as any)[`chars_${projectId}`] || [];
          const savedScenes = (get() as any)[`scenes_${projectId}`] || [];
          const { currentProject: prevProject } = get();
          if (prevProject) {
            set({
              [`chars_${prevProject.id}`]: get().characters,
              [`scenes_${prevProject.id}`]: get().scenes,
            } as any);
          }
          set({
            currentProject: project,
            characters: savedChars,
            scenes: savedScenes,
          });
        }
      },
      
      saveProject: () => {
        const { currentProject, characters, scenes } = get();
        if (!currentProject) return;
        
        const updatedProject: DramaProject = {
          ...currentProject,
          updatedAt: new Date().toISOString(),
          characters: characters.length,
          scenes: scenes.length,
          duration: scenes.reduce((sum, s) => sum + s.duration, 0)
        };
        
        set(state => ({
          currentProject: updatedProject,
          projects: state.projects.map(p => 
            p.id === updatedProject.id ? updatedProject : p
          ),
          [`chars_${currentProject.id}`]: characters,
          [`scenes_${currentProject.id}`]: scenes,
        } as any));
      },
      
      updateProject: (updates) => {
        set(state => {
          if (!state.currentProject) return state;
          
          const updatedProject = {
            ...state.currentProject,
            ...updates,
            updatedAt: new Date().toISOString()
          };
          
          return {
            currentProject: updatedProject,
            projects: state.projects.map(p =>
              p.id === updatedProject.id ? updatedProject : p
            )
          };
        });
      },
      
      deleteProject: (projectId) => {
        set(state => ({
          projects: state.projects.filter(p => p.id !== projectId),
          currentProject: state.currentProject?.id === projectId 
            ? null 
            : state.currentProject
        }));
      },
      
      createCharacter: (character) => {
        const id = generateId();
        const newCharacter: CharacterCard = {
          id,
          projectId: get().currentProject?.id || '',
          name: character.name || '未命名角色',
          role: character.role || 'supporting',
          appearance: {
            referenceImage: character.appearance?.referenceImage || '',
            description: character.appearance?.description || '',
            gender: character.appearance?.gender || 'female',
            age: character.appearance?.age || 25,
            ageRange: character.appearance?.ageRange || 'young_adult',
            ...character.appearance
          },
          voice: {
            engine: character.voice?.engine || 'minimax',
            voiceId: character.voice?.voiceId || '',
            voiceStyle: character.voice?.voiceStyle || 'gentle',
            speechRate: character.voice?.speechRate || 1.0,
            pitch: character.voice?.pitch || 1.0,
            personality: character.voice?.personality || []
          },
          personality: {
            traits: character.personality?.traits || [],
            background: character.personality?.background || '',
            motivation: character.personality?.motivation || '',
            relationships: character.personality?.relationships || []
          },
          consistency: {
            seed: Math.floor(Math.random() * 1000000),
            style: character.consistency?.style || 'realistic',
            tags: character.consistency?.tags || []
          },
          usage: {
            scenes: [],
            totalDialogueLines: 0,
            totalDuration: 0
          },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
        
        set(state => ({
          characters: [...state.characters, newCharacter]
        }));
        
        get().saveProject();
        return id;
      },
      
      updateCharacter: (id, updates) => {
        set(state => ({
          characters: state.characters.map(c =>
            c.id === id 
              ? { ...c, ...updates, updatedAt: new Date().toISOString() }
              : c
          )
        }));
        get().saveProject();
      },
      
      deleteCharacter: (id) => {
        set(state => ({
          characters: state.characters.filter(c => c.id !== id),
          selectedCharacter: state.selectedCharacter?.id === id 
            ? null 
            : state.selectedCharacter
        }));
        get().saveProject();
      },
      
      selectCharacter: (character) => {
        set({ selectedCharacter: character });
      },
      
      createScene: (scene) => {
        const id = generateId();
        const newScene: Shot = {
          id,
          shotNumber: get().scenes.length + 1,
          shotSize: scene.shotSize || 'medium',
          cameraMove: scene.cameraMove || 'static',
          duration: scene.duration || 5,
          description: scene.description || '',
          prompt: scene.prompt || '',
          notes: scene.notes || '',
          characters: scene.characters || [],
          dialogues: scene.dialogues || []
        };
        
        set(state => ({
          scenes: [...state.scenes, newScene]
        }));
        
        get().saveProject();
        return id;
      },
      
      updateScene: (id, updates) => {
        set(state => ({
          scenes: state.scenes.map(s =>
            s.id === id ? { ...s, ...updates } : s
          )
        }));
        get().saveProject();
      },
      
      deleteScene: (id) => {
        set(state => {
          const filtered = state.scenes.filter(s => s.id !== id);
          const renumbered = filtered.map((s, index) => ({
            ...s,
            shotNumber: index + 1
          }));
          
          return {
            scenes: renumbered,
            selectedScene: state.selectedScene?.id === id 
              ? null 
              : state.selectedScene
          };
        });
        get().saveProject();
      },
      
      selectScene: (scene) => {
        set({ selectedScene: scene });
      },
      
      reorderScenes: (fromIndex, toIndex) => {
        set(state => {
          const scenes = [...state.scenes];
          const [removed] = scenes.splice(fromIndex, 1);
          scenes.splice(toIndex, 0, removed);
          
          const renumbered = scenes.map((s, index) => ({
            ...s,
            shotNumber: index + 1
          }));
          
          return { scenes: renumbered };
        });
        get().saveProject();
      },
      
      
      updateSettings: (settings) => {
        if (settings.apiKey) {
          saveGlobalApiKey(settings.apiKey);
        }
        
        set(state => ({
          settings: { ...state.settings, ...settings }
        }));
      },
      
      addTask: (task) => {
        const id = generateId();
        const newTask: Task = {
          id,
          name: task.name || '未命名任务',
          type: task.type || 'image_gen',
          status: 'pending',
          createdAt: new Date().toISOString(),
          ...task
        };
        
        set(state => ({
          tasks: [...state.tasks, newTask]
        }));
        
        return id;
      },
      
      updateTask: (id, updates) => {
        set(state => ({
          tasks: state.tasks.map(task =>
            task.id === id ? { ...task, ...updates } : task
          )
        }));
      },
      
      removeTask: (id) => {
        set(state => ({
          tasks: state.tasks.filter(task => task.id !== id)
        }));
      },
      
      clearTasks: () => {
        set({ tasks: [] });
      },
      
      setWorkflowStatus: (status) => {
        set(state => ({
          workflowStatus: { ...state.workflowStatus, ...status }
        }));
      }
    }),
    {
      name: 'drama-project-storage',
      version: 1
    }
  )
);
