/**
 * 批量场景生成管理器
 * 管理多场景的并行/串行生成
 */

import { comfyUIClient } from './comfyui-client';
import { SceneGenerationParams } from './storyboard-to-workflow';

export interface SceneGenerationResult {
  sceneIndex: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  imageOutput?: string;
  videoOutput?: string;
  audioOutput?: string;
  error?: string;
  progress: number;
}

export interface BatchGenerationProgress {
  currentScene: number;
  totalScenes: number;
  sceneResults: SceneGenerationResult[];
  overallProgress: number;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  startTime?: Date;
  endTime?: Date;
  estimatedTimeRemaining?: number;
}

export class BatchSceneManager {
  private results: SceneGenerationResult[] = [];
  private isCancelled = false;
  private onProgressCallback?: (progress: BatchGenerationProgress) => void;

  /**
   * 设置进度回调
   */
  onProgress(callback: (progress: BatchGenerationProgress) => void) {
    this.onProgressCallback = callback;
  }

  /**
   * 生成单个场景
   */
  private async generateScene(
    scene: SceneGenerationParams,
    workflow: any
  ): Promise<SceneGenerationResult> {
    const result: SceneGenerationResult = {
      sceneIndex: scene.sceneIndex,
      status: 'processing',
      progress: 0
    };

    try {
      // 1. 生成图像
      const imageWorkflow = this.createImageWorkflow(scene, workflow);
      const imageResult = await comfyUIClient.queuePrompt(imageWorkflow);
      result.progress = 33;

      if (this.isCancelled) {
        result.status = 'failed';
        result.error = 'Cancelled by user';
        return result;
      }

      // 2. 生成视频
      const videoWorkflow = this.createVideoWorkflow(scene, imageResult, workflow);
      const videoResult = await comfyUIClient.queuePrompt(videoWorkflow);
      result.videoOutput = videoResult;
      result.progress = 66;

      if (this.isCancelled) {
        result.status = 'failed';
        result.error = 'Cancelled by user';
        return result;
      }

      // 3. 生成音频（如果有）
      if (scene.audioText) {
        const audioWorkflow = this.createAudioWorkflow(scene, workflow);
        const audioResult = await comfyUIClient.queuePrompt(audioWorkflow);
        result.audioOutput = audioResult;
      }

      result.progress = 100;
      result.status = 'completed';
      
    } catch (error) {
      result.status = 'failed';
      result.error = error instanceof Error ? error.message : 'Unknown error';
    }

    return result;
  }

  /**
   * 批量生成所有场景
   */
  async generateAllScenes(
    scenes: SceneGenerationParams[],
    workflow: any,
    options: {
      parallel?: boolean;
      maxParallel?: number;
    } = {}
  ): Promise<SceneGenerationResult[]> {
    const { parallel = false, maxParallel = 3 } = options;
    
    this.results = scenes.map(scene => ({
      sceneIndex: scene.sceneIndex,
      status: 'pending' as const,
      progress: 0
    }));

    const startTime = new Date();

    if (parallel) {
      // 并行生成
      const batches: SceneGenerationParams[][] = [];
      for (let i = 0; i < scenes.length; i += maxParallel) {
        batches.push(scenes.slice(i, i + maxParallel));
      }

      for (const batch of batches) {
        if (this.isCancelled) break;
        
        const batchResults = await Promise.all(
          batch.map(scene => this.generateScene(scene, workflow))
        );
        
        batchResults.forEach(result => {
          this.results[result.sceneIndex] = result;
          this.notifyProgress(startTime);
        });
      }
    } else {
      // 串行生成
      for (const scene of scenes) {
        if (this.isCancelled) break;
        
        const result = await this.generateScene(scene, workflow);
        this.results[scene.sceneIndex] = result;
        this.notifyProgress(startTime);
      }
    }

    return this.results;
  }

  /**
   * 取消生成
   */
  cancel() {
    this.isCancelled = true;
    comfyUIClient.interrupt();
  }

  /**
   * 通知进度更新
   */
  private notifyProgress(startTime: Date) {
    if (!this.onProgressCallback) return;

    const completedScenes = this.results.filter(r => r.status === 'completed').length;
    const totalScenes = this.results.length;
    const overallProgress = (completedScenes / totalScenes) * 100;

    const elapsed = Date.now() - startTime.getTime();
    const avgTimePerScene = completedScenes > 0 ? elapsed / completedScenes : 0;
    const remainingScenes = totalScenes - completedScenes;
    const estimatedTimeRemaining = avgTimePerScene * remainingScenes;

    this.onProgressCallback({
      currentScene: completedScenes,
      totalScenes,
      sceneResults: this.results,
      overallProgress,
      status: this.isCancelled ? 'cancelled' : 
              completedScenes === totalScenes ? 'completed' : 'processing',
      startTime,
      estimatedTimeRemaining
    });
  }

  /**
   * 创建图像生成工作流
   */
  private createImageWorkflow(scene: SceneGenerationParams, baseWorkflow: any): any {
    return {
      ...baseWorkflow,
      '1': {
        class_type: 'KlingImageGenV3Node',
        inputs: {
          api_key: '',
          prompt: scene.prompt,
          negative_prompt: scene.negativePrompt,
          model: scene.imageModel,
          aspect_ratio: '16:9',
        }
      }
    };
  }

  /**
   * 创建视频生成工作流
   */
  private createVideoWorkflow(
    scene: SceneGenerationParams,
    imageResult: any,
    baseWorkflow: any
  ): any {
    return {
      ...baseWorkflow,
      '2': {
        class_type: 'KlingImageToVideoV3Node',
        inputs: {
          api_key: '',
          image: imageResult,
          prompt: scene.prompt,
          model_name: 'kling-v2-master',
          duration: String(scene.duration),
        }
      }
    };
  }

  /**
   * 创建音频生成工作流
   */
  private createAudioWorkflow(scene: SceneGenerationParams, baseWorkflow: any): any {
    return {
      ...baseWorkflow,
      '3': {
        class_type: 'KlingTTSV3Node',
        inputs: {
          api_key: '',
          text: scene.audioText!,
          voice: 'Binbin',
        }
      }
    };
  }
}
