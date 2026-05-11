/**
 * 分镜转小说格式转换器
 * 将用户编辑的分镜转换为NovelToDramaWorkflowNode可识别的小说格式
 */

import { Shot } from '@/types/project';

export interface NovelFormat {
  text: string;
  sceneCount: number;
  totalDuration: number;
  metadata: {
    style: string;
    mood: string;
    pace: string;
  };
}

export class StoryboardToNovelConverter {
  /**
   * 将分镜数组转换为小说文本格式
   */
  static convertToNovel(shots: Shot[]): NovelFormat {
    let novelText = '';
    let totalDuration = 0;
    
    shots.forEach((shot, index) => {
      const sceneNumber = index + 1;
      totalDuration += shot.duration || 5;
      
      // 场景标题
      novelText += `\n【场景${sceneNumber}】\n`;
      novelText += `━━━━━━━━━━━━━━━━━━\n`;
      
      // 场景描述
      novelText += `\n${shot.description || '镜头描述'}\n`;
      
      // 技术参数
      novelText += `\n【技术参数】\n`;
      novelText += `景别：${this.mapShotSize(shot.shotSize)}\n`;
      novelText += `运镜：${this.mapCameraMove(shot.cameraMove)}\n`;
      novelText += `时长：${shot.duration || 5}秒\n`;
      
      // 提示词
      if (shot.prompt) {
        novelText += `\n【画面提示词】\n`;
        novelText += `${shot.prompt}\n`;
      }
      
      // 备注
      if (shot.notes) {
        novelText += `\n【导演备注】\n`;
        novelText += `${shot.notes}\n`;
      }
      
      novelText += `\n${'─'.repeat(40)}\n`;
    });
    
    // 分析整体风格
    const metadata = this.analyzeMetadata(shots);
    
    return {
      text: novelText.trim(),
      sceneCount: shots.length,
      totalDuration,
      metadata
    };
  }
  
  /**
   * 景别映射（英文）
   */
  private static mapShotSize(size?: string): string {
    const mapping: Record<string, string> = {
      'extreme-long': 'extreme long shot, vast establishing view',
      'long': 'long shot, full environment visible',
      'medium-long': 'medium long shot, character in context',
      'medium': 'medium shot, waist up framing',
      'medium-close': 'medium close-up, chest up',
      'close': 'close-up shot, face and shoulders',
      'extreme-close': 'extreme close-up, detailed focus',
      '远景': 'extreme long shot, vast establishing view',
      '全景': 'long shot, full environment visible',
      '中景': 'medium shot, waist up framing',
      '近景': 'medium close-up, chest up',
      '特写': 'close-up shot, face and shoulders',
      '大特写': 'extreme close-up, detailed focus'
    };
    
    return mapping[size || 'medium'] || 'medium shot, waist up framing';
  }
  
  /**
   * 运镜映射（英文）
   */
  private static mapCameraMove(move?: string): string {
    const mapping: Record<string, string> = {
      'static': 'static camera, locked tripod shot',
      'dolly-in': 'dolly in, camera moves forward',
      'dolly-out': 'dolly out, camera moves backward',
      'dolly-left': 'dolly left, tracking shot',
      'dolly-right': 'dolly right, tracking shot',
      'truck-left': 'truck left, lateral movement',
      'truck-right': 'truck right, lateral movement',
      'pedestal-up': 'pedestal up, camera rises',
      'pedestal-down': 'pedestal down, camera lowers',
      'pan-left': 'pan left, horizontal rotation',
      'pan-right': 'pan right, horizontal rotation',
      'tilt-up': 'tilt up, vertical rotation upward',
      'tilt-down': 'tilt down, vertical rotation downward',
      'zoom-in': 'zoom in, optical magnification',
      'zoom-out': 'zoom out, optical widening',
      'crane-up': 'crane up, elevated movement',
      'crane-down': 'crane down, descending movement',
      'handheld': 'handheld camera, organic movement',
      '推镜': 'dolly in, camera moves forward',
      '拉镜': 'dolly out, camera moves backward',
      '左移': 'truck left, lateral movement',
      '右移': 'truck right, lateral movement',
      '上升': 'pedestal up, camera rises',
      '下降': 'pedestal down, camera lowers',
      '左摇': 'pan left, horizontal rotation',
      '右摇': 'pan right, horizontal rotation',
      '上仰': 'tilt up, vertical rotation upward',
      '下俯': 'tilt down, vertical rotation downward'
    };
    
    return mapping[move || 'static'] || 'static camera, locked tripod shot';
  }
  
  /**
   * 分析整体风格
   */
  private static analyzeMetadata(shots: Shot[]): { style: string; mood: string; pace: string } {
    const avgDuration = shots.reduce((sum, s) => sum + (s.duration || 5), 0) / shots.length;
    
    // 根据平均时长判断节奏
    let pace = 'moderate';
    if (avgDuration < 4) {
      pace = 'fast, dynamic rhythm';
    } else if (avgDuration > 8) {
      pace = 'slow, contemplative rhythm';
    }
    
    // 分析景别多样性
    const shotSizes = new Set(shots.map(s => s.shotSize).filter(Boolean));
    const cameraMoves = new Set(shots.map(s => s.cameraMove).filter(Boolean));
    
    // 根据变化丰富度判断风格
    let style = 'cinematic';
    if (shotSizes.size > 4 && cameraMoves.size > 4) {
      style = 'dynamic, visually rich';
    } else if (shotSizes.size <= 2 && cameraMoves.size <= 2) {
      style = 'minimalist, focused';
    }
    
    // 根据提示词分析情绪（简单分析）
    const prompts = shots.map(s => s.prompt).filter(Boolean).join(' ').toLowerCase();
    let mood = 'neutral';
    
    if (prompts.includes('dark') || prompts.includes('night') || prompts.includes('shadow')) {
      mood = 'dramatic, moody atmosphere';
    } else if (prompts.includes('bright') || prompts.includes('sunny') || prompts.includes('colorful')) {
      mood = 'upbeat, vibrant atmosphere';
    } else if (prompts.includes('soft') || prompts.includes('gentle') || prompts.includes('warm')) {
      mood = 'warm, emotional atmosphere';
    }
    
    return { style, mood, pace };
  }
  
  /**
   * 转换为工作流参数格式
   */
  static toWorkflowParams(novel: NovelFormat, config: {
    apiKey?: string;
    imageModel?: string;
    videoModel?: string;
    audioEnabled?: boolean;
  } = {}) {
    return {
      novelText: novel.text,
      maxScenes: novel.sceneCount,
      totalDuration: novel.totalDuration,
      style: novel.metadata.style,
      mood: novel.metadata.mood,
      pace: novel.metadata.pace,
      imageModel: config.imageModel || 'kling-v2',
      videoModel: config.videoModel || 'kling-v2-master',
      audioEnabled: config.audioEnabled !== false,
      ...config
    };
  }
}
