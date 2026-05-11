export interface DramaProject {
  id: string;
  name: string;
  coverImage: string;
  description: string;
  genre: string;
  status: 'draft' | 'in_progress' | 'completed' | 'published';
  createdAt: string;
  updatedAt: string;
  
  characters: number;
  scenes: number;
  duration: number;
  
  tags: string[];
  targetPlatform: string[];
}

export interface CharacterCard {
  id: string;
  projectId: string;
  
  name: string;
  nickname?: string;
  role: 'protagonist' | 'supporting' | 'antagonist' | 'minor';
  
  appearance: {
    referenceImage: string;
    description: string;
    gender: 'male' | 'female' | 'other';
    age: number;
    ageRange: 'child' | 'teenager' | 'young_adult' | 'middle_aged' | 'elderly';
    height?: string;
    bodyType?: string;
    hairColor?: string;
    hairStyle?: string;
    eyeColor?: string;
    distinctiveFeatures?: string[];
    defaultOutfit?: string;
    alternateOutfits?: string[];
  };
  
  voice: {
    engine: 'minimax' | 'openai' | 'elevenlabs';
    voiceId: string;
    voiceStyle: string;
    speechRate: number;
    pitch: number;
    previewUrl?: string;
    personality: string[];
  };
  
  personality: {
    traits: string[];
    background: string;
    motivation: string;
    relationships: {
      characterId: string;
      relationship: string;
    }[];
  };
  
  consistency: {
    seed: number;
    embedding?: number[];
    style: 'realistic' | 'anime' | 'cartoon' | 'artistic';
    tags: string[];
  };
  
  usage: {
    scenes: string[];
    totalDialogueLines: number;
    totalDuration: number;
  };
  
  createdAt: string;
  updatedAt: string;
}

export interface Shot {
  id: string;
  shotNumber: number;
  shotSize: string;
  cameraMove: string;
  duration: number;
  description: string;
  prompt: string;
  notes: string;
  characters: string[];
  dialogues?: {
    characterId: string;
    text: string;
    emotion?: string;
  }[];
}

export interface ProjectSettings {
  style: 'realistic' | 'anime' | 'cartoon' | 'artistic';
  aspectRatio: '16:9' | '9:16' | '1:1' | '4:3';
  defaultTextModel: string;
  defaultImageModel: string;
  defaultVideoModel: string;
  defaultAudioEngine: string;
  defaultTTSModel: string;
  defaultImageSize: string;
  defaultVideoFPS: number;
  apiKey?: string;
}

export interface GenerationProgress {
  current: number;
  total: number;
  sceneId: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  error?: string;
}

export interface Task {
  id: string;
  name: string;
  type: 'novel_analysis' | 'text_analysis' | 'character_creation' | 'storyboard' | 'resource_generation' | 'composition' | 'image_gen' | 'video_gen' | 'audio_gen';
  status: 'pending' | 'running' | 'completed' | 'failed';
  cost?: number;
  createdAt: string;
  completedAt?: string;
  error?: string;
  metadata?: Record<string, any>;
}
