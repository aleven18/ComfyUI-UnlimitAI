export interface ComfyUINode {
  id: number;
  type: string;
  pos: [number, number];
  size: [number, number];
  flags: {};
  order: number;
  mode: number;
  properties: Record<string, any>;
  widgets_values?: any[];
}

export interface ComfyUIWorkflow {
  last_node_id: number;
  last_link_id: number;
  nodes: ComfyUINode[];
  links: any[];
}

export interface QueuePromptRequest {
  prompt: ComfyUIWorkflow;
  client_id: string;
}

export interface QueuePromptResponse {
  prompt_id: string;
  number: number;
  node_errors?: Record<string, any>;
}

export interface ProgressData {
  value: number;
  max: number;
}

export interface ExecutingData {
  node: string;
}

export interface ExecutedData {
  node: string;
  output: any;
}

export interface WebSocketMessage {
  type: 'status' | 'progress' | 'executing' | 'executed' | 'execution_error';
  data: ProgressData | ExecutingData | ExecutedData | any;
}

export interface UploadResponse {
  name: string;
  subfolder: string;
  type: string;
}

export interface HistoryEntry {
  prompt: ComfyUIWorkflow;
  outputs: Record<string, any>;
  status: {
    status_str: string;
    completed: boolean;
    messages: string[][];
  };
}

export interface ConversionParams {
  apiKey: string;
  novelText: string;
  maxScenes: number;
  projectName: string;
  textModel: string;
  language: string;
  style: string;
  imageModel: string;
  aspectRatio: string;
  videoModel: string;
  videoDuration: string;
  videoAspectRatio: string;
  voiceId: string;
  enableBackgroundMusic: boolean;
  imageReference: 'none' | 'subject' | 'face';
  imageFidelity: number;
  humanFidelity: number;
  storyboardMode: 'disabled' | 'combine_scenes';
  refImageUrl: string;
  preset: string;
}

export interface ConversionResult {
  promptId: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  currentNode?: string;
  outputs: any[];
  error?: string;
}

export type PresetType = 'budget' | 'balanced' | 'quality' | 'max_quality';

export interface StoryboardSegment {
  id: string;
  prompt: string;
  duration: number;
}

export interface StoryboardTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'ad' | 'drama' | 'mv' | 'tutorial' | 'brand';
  tags: string[];
  duration: 5 | 10;
  segments: Omit<StoryboardSegment, 'id'>[];
  example: {
    title: string;
    description: string;
    segments: Omit<StoryboardSegment, 'id'>[];
    thumbnailTip: string;
  };
}

export interface StoryboardProject {
  storyDescription: string;
  characterImageUrls: string[];
  imageReference: 'subject' | 'face';
  imageFidelity: number;
  humanFidelity: number;
  textModel: string;
  imageModel: string;
  videoModel: string;
  storyboardCount: number;
  segments: StoryboardSegment[];
  aspectRatio: string;
  duration: string;
  cfgScale: number;
  mode: string;
  negativePrompt: string;
  cameraControlJson: string;
  sound: 'off' | 'on';
  selectedTemplateId: string | null;
}
