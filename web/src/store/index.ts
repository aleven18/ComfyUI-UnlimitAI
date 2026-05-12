import { create } from 'zustand';
import { ConversionParams, ConversionResult, PresetType, StoryboardProject } from '@/types';

const DEFAULT_STORYBOARD: StoryboardProject = {
  storyDescription: '',
  characterImageUrls: [],
  imageReference: 'subject',
  imageFidelity: 0.5,
  humanFidelity: 0.45,
  textModel: 'gpt-4o',
  imageModel: 'kling-v2',
  videoModel: 'kling-v2-master',
  storyboardCount: 4,
  segments: [],
  aspectRatio: '16:9',
  duration: '5',
  cfgScale: 0.5,
  mode: 'std',
  negativePrompt: '',
  cameraControlJson: '',
  sound: 'off',
  selectedTemplateId: null,
  cameraStyle: 'none',
  voice: 'minimax-male-qn-jingying',
  generateDialogue: 'off',
};

interface AppState {
  params: Partial<ConversionParams>;
  setParams: (params: Partial<ConversionParams>) => void;
  
  preset: PresetType;
  setPreset: (preset: PresetType) => void;
  
  storyboard: StoryboardProject;
  setStoryboard: (sb: StoryboardProject | ((prev: StoryboardProject) => StoryboardProject)) => void;
  
  result: ConversionResult | null;
  setResult: (result: ConversionResult | null) => void;
  
  progress: number;
  setProgress: (progress: number) => void;
  
  currentNode: string | null;
  setCurrentNode: (node: string | null) => void;
  
  outputs: any[];
  addOutput: (output: any) => void;
  clearOutputs: () => void;
  
  logs: string[];
  addLog: (log: string) => void;
  clearLogs: () => void;
  
  reset: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  params: {},
  setParams: (params) => set((state) => ({ params: { ...state.params, ...params } })),
  
  preset: 'balanced',
  setPreset: (preset) => set({ preset }),
  
  storyboard: { ...DEFAULT_STORYBOARD },
  setStoryboard: (sb) => set((state) => ({ storyboard: typeof sb === 'function' ? sb(state.storyboard) : sb })),
  
  result: null,
  setResult: (result) => set({ result }),
  
  progress: 0,
  setProgress: (progress) => set({ progress }),
  
  currentNode: null,
  setCurrentNode: (currentNode) => set({ currentNode }),
  
  outputs: [],
  addOutput: (output) => set((state) => ({ outputs: [...state.outputs, output] })),
  clearOutputs: () => set({ outputs: [] }),
  
  logs: [],
  addLog: (log) => set((state) => ({ logs: [...state.logs, log] })),
  clearLogs: () => set({ logs: [] }),
  
  reset: () => set({
    params: {},
    preset: 'balanced',
    storyboard: { ...DEFAULT_STORYBOARD },
    result: null,
    progress: 0,
    currentNode: null,
    outputs: [],
    logs: [],
  }),
}));
