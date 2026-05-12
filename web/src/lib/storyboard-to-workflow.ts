import { Shot } from '@/types/project';
import { ComfyUIWorkflow } from '@/types';

export type { Shot };

export interface SceneGenerationParams {
  sceneIndex: number;
  prompt: string;
  negativePrompt: string;
  duration: number;
  cameraMotion: string;
  imageModel: string;
  videoModel: string;
  audioText?: string;
}

export class StoryboardToWorkflowConverter {

  private static SHOT_SIZE_PROMPTS: Record<string, string> = {
    'extreme-long': 'extreme long shot, wide establishing shot, environmental',
    'long': 'long shot, full body shot, wide angle',
    'full': 'full shot, showing entire figure',
    'medium': 'medium shot, waist up, medium distance',
    'medium-close': 'medium close-up, chest up',
    'close': 'close-up shot, face only, tight framing',
    'extreme-close': 'extreme close-up, macro shot, detailed'
  };

  private static CAMERA_MOTION_MAP: Record<string, string> = {
    'static': 'static camera, no movement',
    'pan': 'camera pan, horizontal movement',
    'tilt': 'camera tilt, vertical movement',
    'dolly': 'dolly shot, camera push in',
    'zoom': 'zoom in effect',
    'tracking': 'tracking shot, following movement',
    'crane': 'crane shot, vertical rising'
  };

  static convertShotToScene(
    shot: Shot,
    style: string = 'cinematic',
    index: number,
    imageModel?: string,
    videoModel?: string
  ): SceneGenerationParams {
    const shotSizePrompt = this.SHOT_SIZE_PROMPTS[shot.shotSize] || 'medium shot';
    const cameraMotion = this.CAMERA_MOTION_MAP[shot.cameraMove] || 'static camera';

    const fullPrompt = [
      shot.prompt || shot.description,
      shotSizePrompt,
      style === 'cinematic' ? 'cinematic, film look, professional' : '',
      cameraMotion
    ].filter(Boolean).join(', ');

    return {
      sceneIndex: index,
      prompt: fullPrompt,
      negativePrompt: 'blurry, bad quality, distorted, ugly, deformed',
      duration: shot.duration,
      cameraMotion: shot.cameraMove,
      imageModel: imageModel || 'kling-v2',
      videoModel: videoModel || 'kling-v2',
      audioText: shot.description
    };
  }

  static convertStoryboardToWorkflowParams(
    shots: Shot[],
    options: {
      style?: string;
      imageModel?: string;
      videoModel?: string;
      audioEnabled?: boolean;
    } = {}
  ): {
    scenes: SceneGenerationParams[];
    totalDuration: number;
    totalScenes: number;
    estimatedCost: number;
  } {
    const {
      style = 'cinematic',
      imageModel = 'kling-v2',
      videoModel = 'kling-v2',
      audioEnabled = true
    } = options;

    const scenes = shots.map((shot, index) => {
      const scene = this.convertShotToScene(shot, style, index, imageModel, videoModel);
      scene.imageModel = imageModel;
      scene.videoModel = videoModel;
      if (!audioEnabled) {
        delete scene.audioText;
      }
      return scene;
    });

    const totalDuration = shots.reduce((sum, shot) => sum + shot.duration, 0);

    const costPerImage = 0.3;
    const costPerVideoSecond = 0.05;
    const costPerAudioSecond = 0.001;

    const imageCost = scenes.length * costPerImage;
    const videoCost = totalDuration * costPerVideoSecond;
    const audioCost = audioEnabled ? totalDuration * costPerAudioSecond : 0;

    const estimatedCost = imageCost + videoCost + audioCost;

    return {
      scenes,
      totalDuration,
      totalScenes: scenes.length,
      estimatedCost
    };
  }

  static generateSceneWorkflowNodes(
    scene: SceneGenerationParams,
    nodeIdOffset: number
  ): Record<string, unknown> {
    const baseNodeId = nodeIdOffset;

    return {
      [`${baseNodeId}`]: {
        class_type: 'KlingImageGenV3Node',
        inputs: {
          api_key: '',
          prompt: scene.prompt,
          negative_prompt: scene.negativePrompt,
          model: scene.imageModel,
          aspect_ratio: '16:9',
          image_fidelity: 0.5,
        }
      },

      [`${baseNodeId + 1}`]: {
        class_type: 'KlingImageToVideoV3Node',
        inputs: {
          api_key: '',
          image: [`${baseNodeId}`, 0],
          prompt: scene.prompt,
          model_name: 'kling-v2-master',
          duration: scene.duration,
          cfg_scale: 0.5,
        }
      },

      ...(scene.audioText ? {
        [`${baseNodeId + 2}`]: {
          class_type: 'KlingTTSV3Node',
          inputs: {
            api_key: '',
            text: scene.audioText,
            voice: 'Binbin',
          }
        }
      } : {})
    };
  }

  static generateMultiSceneWorkflow(
    workflowParams: ReturnType<typeof this.convertStoryboardToWorkflowParams>,
    baseWorkflow: ComfyUIWorkflow
  ): ComfyUIWorkflow {
    const workflow = JSON.parse(JSON.stringify(baseWorkflow));

    let nodeIdOffset = 100;
    const allSceneNodes: Record<string, unknown> = {};
    const videoOutputs: [string, number][] = [];
    const audioOutputs: [string, number][] = [];

    workflowParams.scenes.forEach((scene) => {
      const sceneNodes = this.generateSceneWorkflowNodes(scene, nodeIdOffset);
      Object.assign(allSceneNodes, sceneNodes);

      videoOutputs.push([`${nodeIdOffset + 1}`, 0]);

      if (scene.audioText) {
        audioOutputs.push([`${nodeIdOffset + 2}`, 0]);
      }

      nodeIdOffset += 10;
    });

    Object.assign(workflow, allSceneNodes);

    return workflow;
  }
}
