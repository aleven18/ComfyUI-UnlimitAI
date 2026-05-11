import { ComfyUIWorkflow, ConversionParams, StoryboardProject, PresetType } from '@/types';
import dramaV3Workflow from '../workflows/drama_v3_workflow.json';
import storyboardWorkflow from '../workflows/storyboard_workflow.json';
import storyboardProWorkflow from '../workflows/storyboard_pro_workflow.json';
import balancedWorkflow from '../workflows/balanced_workflow.json';
import budgetWorkflow from '../workflows/budget_workflow.json';
import qualityWorkflow from '../workflows/quality_workflow.json';
import maxQualityWorkflow from '../workflows/max_quality_workflow.json';

// PresetType re-exported from types
export type { PresetType } from '@/types';
export type WorkflowVersion = 'v1v2' | 'v3';

interface PresetConfig {
  label: string;
  textModel: string;
  imageModel: string;
  videoModel: string;
  videoDuration: string;
  videoMode: string;
  imageReference: 'none' | 'subject' | 'face';
  voiceId: string;
  maxScenes: number;
  version: WorkflowVersion;
}

const PRESET_CONFIGS: Record<PresetType, PresetConfig> = {
  budget: {
    label: '经济模式',
    textModel: 'deepseek-chat',
    imageModel: 'kling-v2',
    videoModel: 'kling-v2',
    videoDuration: '5',
    videoMode: 'std',
    imageReference: 'none',
    voiceId: 'minimax-male-qn-jingying',
    maxScenes: 8,
    version: 'v1v2',
  },
  balanced: {
    label: '平衡模式',
    textModel: 'deepseek-chat',
    imageModel: 'flux-pro',
    videoModel: 'kling-v2',
    videoDuration: '10',
    videoMode: 'std',
    imageReference: 'none',
    voiceId: 'minimax-male-qn-jingying',
    maxScenes: 10,
    version: 'v1v2',
  },
  quality: {
    label: '质量模式',
    textModel: 'gpt-4o',
    imageModel: 'kling-v2',
    videoModel: 'kling-v2',
    videoDuration: '10',
    videoMode: 'pro',
    imageReference: 'subject',
    voiceId: 'minimax-male-qn-qingse',
    maxScenes: 12,
    version: 'v1v2',
  },
  max_quality: {
    label: '最高质量',
    textModel: 'claude-3-5-sonnet-20241022',
    imageModel: 'kling-v2',
    videoModel: 'kling-v2',
    videoDuration: '10',
    videoMode: 'pro',
    imageReference: 'subject',
    voiceId: 'minimax-female-yujie',
    maxScenes: 15,
    version: 'v1v2',
  },
};

const V1V2_TEMPLATES: Record<PresetType, any> = {
  budget: budgetWorkflow,
  balanced: balancedWorkflow,
  quality: qualityWorkflow,
  max_quality: maxQualityWorkflow,
};

export class WorkflowManager {
  static getTemplate(preset: PresetType, version?: WorkflowVersion): ComfyUIWorkflow {
    const ver = version || PRESET_CONFIGS[preset].version;
    if (ver === 'v3') {
      return JSON.parse(JSON.stringify(dramaV3Workflow));
    }
    return JSON.parse(JSON.stringify(V1V2_TEMPLATES[preset] || balancedWorkflow));
  }

  static getV3Template(): ComfyUIWorkflow {
    return JSON.parse(JSON.stringify(dramaV3Workflow));
  }

  static getStoryboardTemplate(): ComfyUIWorkflow {
    return JSON.parse(JSON.stringify(storyboardWorkflow));
  }

  static getStoryboardProTemplate(): ComfyUIWorkflow {
    return JSON.parse(JSON.stringify(storyboardProWorkflow));
  }

  static fillWorkflow(template: ComfyUIWorkflow, params: ConversionParams): ComfyUIWorkflow {
    const workflow = JSON.parse(JSON.stringify(template));
    const preset = PRESET_CONFIGS[params.preset as PresetType] || PRESET_CONFIGS.balanced;

    workflow.nodes.forEach((node: any) => {
      switch (node.type) {
        case 'NovelToDramaV3Node': {
          node.widgets_values = [
            params.apiKey,
            params.novelText,
            params.maxScenes || preset.maxScenes,
            params.textModel || preset.textModel,
            params.language || 'chinese',
            params.style || 'cinematic',
          ];
          break;
        }
        case 'SceneImageGeneratorV3Node': {
          node.widgets_values = [
            params.apiKey,
            '',
            params.imageModel || preset.imageModel,
            params.aspectRatio || '16:9',
            params.maxScenes || preset.maxScenes,
            params.refImageUrl || '',
            params.imageReference || preset.imageReference,
            params.imageFidelity ?? 0.5,
            params.humanFidelity ?? 0.45,
          ];
          break;
        }
        case 'SceneVideoGeneratorV3Node': {
          node.widgets_values = [
            params.apiKey,
            '',
            params.videoModel || preset.videoModel,
            params.videoDuration || preset.videoDuration,
            params.aspectRatio || '16:9',
            params.storyboardMode || 'disabled',
          ];
          break;
        }
        case 'SceneAudioGeneratorV3Node': {
          node.widgets_values = [
            params.apiKey,
            '',
            params.voiceId || preset.voiceId,
            params.enableBackgroundMusic ?? true,
            params.maxScenes || preset.maxScenes,
          ];
          break;
        }
        case 'DramaManifestV3Node': {
          node.widgets_values = [
            '',
            '',
            '',
            '',
            params.projectName || '我的漫剧作品',
          ];
          break;
        }

        case 'DramaConfigNode': {
          node.widgets_values = [
            params.apiKey,
            params.maxScenes || preset.maxScenes,
            params.projectName || '我的漫剧作品',
            params.textModel || preset.textModel,
            params.language || 'chinese',
            params.style || 'cinematic',
            params.imageModel || preset.imageModel,
            params.aspectRatio || '16:9',
            params.videoModel || preset.videoModel,
            params.videoDuration || preset.videoDuration,
            params.videoAspectRatio || '16:9',
            params.voiceId || preset.voiceId,
            params.enableBackgroundMusic ?? true,
          ];
          break;
        }
        case 'NovelToDramaWorkflowNode': {
          const values = node.widgets_values || [];
          values[0] = params.apiKey || '';
          values[1] = params.novelText || '';
          values[2] = params.maxScenes || preset.maxScenes;
          values[3] = params.textModel || preset.textModel;
          values[4] = params.language || 'chinese';
          values[5] = params.style || 'cinematic';
          node.widgets_values = values;
          break;
        }
        case 'SceneImageGeneratorNode': {
          const values = node.widgets_values || [];
          values[0] = params.apiKey || '';
          values[1] = '';
          values[2] = params.imageModel || preset.imageModel;
          values[3] = params.aspectRatio || '16:9';
          values[4] = params.maxScenes || preset.maxScenes;
          node.widgets_values = values;
          break;
        }
        case 'SceneVideoGeneratorNode': {
          const values = node.widgets_values || [];
          values[0] = params.apiKey || '';
          values[1] = '';
          values[2] = params.videoModel || preset.videoModel;
          values[3] = params.videoDuration || preset.videoDuration;
          values[4] = params.aspectRatio || '16:9';
          node.widgets_values = values;
          break;
        }
        case 'SceneAudioGeneratorNode': {
          const values = node.widgets_values || [];
          values[0] = params.apiKey || '';
          values[1] = '';
          values[2] = params.voiceId || preset.voiceId;
          values[3] = params.enableBackgroundMusic ?? true;
          values[4] = params.maxScenes || preset.maxScenes;
          node.widgets_values = values;
          break;
        }
        case 'DramaManifestNode': {
          const values = node.widgets_values || [];
          values[0] = params.projectName || '我的漫剧作品';
          node.widgets_values = values;
          break;
        }
        case 'CostEstimatorNode': {
          const values = node.widgets_values || [];
          values[0] = params.maxScenes || preset.maxScenes;
          values[1] = params.textModel || preset.textModel;
          values[2] = params.imageModel || preset.imageModel;
          values[3] = params.videoModel || preset.videoModel;
          values[4] = params.videoDuration || preset.videoDuration;
          values[5] = params.enableBackgroundMusic ?? true;
          node.widgets_values = values;
          break;
        }
      }
    });

    return workflow;
  }

  static fillStoryboardWorkflow(
    template: ComfyUIWorkflow,
    apiKey: string,
    project: StoryboardProject,
  ): ComfyUIWorkflow {
    const workflow = JSON.parse(JSON.stringify(template));
    const segmentsJson = JSON.stringify(
      project.segments.map((s) => ({ prompt: s.prompt, duration: s.duration }))
    );

    workflow.nodes.forEach((node: any) => {
      if (node.type === 'StoryboardVideoV3Node') {
        node.widgets_values = [
          apiKey,
          segmentsJson,
          project.videoModel,
          project.duration,
          project.aspectRatio,
          project.cfgScale,
          project.mode,
          project.negativePrompt,
          project.cameraControlJson,
        ];
      }
    });

    return workflow;
  }

  static fillStoryboardProWorkflow(
    template: ComfyUIWorkflow,
    apiKey: string,
    project: StoryboardProject,
  ): ComfyUIWorkflow {
    const workflow = JSON.parse(JSON.stringify(template));

    workflow.nodes.forEach((node: any) => {
      if (node.type === 'StoryboardProV3Node') {
        node.widgets_values = [
          apiKey,
          project.storyDescription,
          project.characterImageUrls.join('\n'),
          project.imageReference,
          project.imageFidelity,
          project.humanFidelity,
          project.textModel,
          project.imageModel,
          project.videoModel,
          project.storyboardCount,
          project.duration,
          project.aspectRatio,
          project.cfgScale,
          project.mode,
          project.negativePrompt,
          project.sound,
          project.cameraStyle,
          project.voice,
          project.generateDialogue,
        ];
      }
    });

    return workflow;
  }

  static getDefaultParams(preset: PresetType = 'balanced'): Partial<ConversionParams> {
    const cfg = PRESET_CONFIGS[preset];
    return {
      maxScenes: cfg.maxScenes,
      projectName: '我的漫剧作品',
      textModel: cfg.textModel,
      language: 'chinese',
      style: 'cinematic',
      imageModel: cfg.imageModel,
      aspectRatio: '16:9',
      videoModel: cfg.videoModel,
      videoDuration: cfg.videoDuration,
      videoAspectRatio: '16:9',
      voiceId: cfg.voiceId,
      enableBackgroundMusic: true,
      imageReference: cfg.imageReference,
      imageFidelity: 0.5,
      humanFidelity: 0.45,
      storyboardMode: 'disabled',
      refImageUrl: '',
    };
  }

  static validateParams(params: ConversionParams): string[] {
    const errors: string[] = [];
    if (!params.apiKey) errors.push('API Key 不能为空');
    if (!params.novelText) errors.push('小说文本不能为空');
    if (params.maxScenes < 1 || params.maxScenes > 50) errors.push('场景数必须在 1-50 之间');
    return errors;
  }

  static validateStoryboard(apiKey: string, project: StoryboardProject): string[] {
    const errors: string[] = [];
    if (!apiKey) errors.push('API Key 不能为空');
    if (project.segments.length < 2) errors.push('至少需要 2 个片段');
    if (project.segments.length > 6) errors.push('最多 6 个片段');

    const total = project.segments.reduce((s, seg) => s + seg.duration, 0);
    const target = parseInt(project.duration);
    if (total !== target) errors.push(`片段总时长 (${total}s) 与视频时长 (${target}s) 不匹配`);

    project.segments.forEach((seg, i) => {
      if (!seg.prompt.trim()) errors.push(`片段 ${i + 1} 提示词不能为空`);
      if (seg.prompt.length > 512) errors.push(`片段 ${i + 1} 提示词超过 512 字符`);
    });

    return errors;
  }

  static validateStoryboardPro(apiKey: string, project: StoryboardProject): string[] {
    const errors: string[] = [];
    if (!apiKey) errors.push('API Key 不能为空');
    if (!project.storyDescription.trim()) errors.push('请输入故事描述');
    if (project.storyboardCount < 2 || project.storyboardCount > 6) errors.push('分镜数必须在 2-6 之间');
    const dur = parseInt(project.duration);
    if (dur === 5 && project.storyboardCount > 3) errors.push('5 秒视频最多 3 段分镜');
    if (dur === 10 && project.storyboardCount > 5) errors.push('10 秒视频最多 5 段分镜');
    return errors;
  }

  static estimateCost(preset: PresetType, sceneCount: number): number {
    const baseCosts: Record<PresetType, number> = {
      budget: 0.4,
      balanced: 0.8,
      quality: 1.8,
      max_quality: 3.5,
    };
    return baseCosts[preset] * sceneCount;
  }

  static estimateStoryboardCost(project: StoryboardProject): number {
    const durationCost: Record<string, number> = { '5': 1.5, '10': 2.5 };
    const modeMultiplier = project.mode === 'pro' ? 1.5 : 1.0;
    return (durationCost[project.duration] || 1.5) * modeMultiplier;
  }

  static estimateStoryboardProCost(project: StoryboardProject): number {
    const textCost: Record<string, number> = { 'gpt-4o': 0.08, 'gpt-4o-mini': 0.02, 'deepseek-chat': 0.01, 'claude-3-5-sonnet-20241022': 0.06 };
    const imageCost: Record<string, number> = { 'kling-v2': 0.3, 'kling-v3': 0.5, 'flux-pro': 0.4, 'gpt-image': 0.3 };
    const videoCost: Record<string, number> = { 'kling-v2-master': 2.0, 'kling-v2-1-master': 2.5, 'kling-v2-5-turbo': 1.5, 'kling-v3': 3.0 };
    const modeMultiplier = project.mode === 'pro' ? 1.5 : 1.0;
    const t = textCost[project.textModel] || 0.05;
    const i = imageCost[project.imageModel] || 0.3;
    const v = videoCost[project.videoModel] || 2.0;
    return (t * 2 + i + v) * modeMultiplier;
  }

  static estimateTime(preset: PresetType, sceneCount: number): number {
    const baseTimes: Record<PresetType, number> = {
      budget: 1.2,
      balanced: 1.7,
      quality: 2.7,
      max_quality: 3.3,
    };
    return baseTimes[preset] * sceneCount;
  }
}
