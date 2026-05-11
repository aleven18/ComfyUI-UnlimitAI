/**
 * 漫剧制作完整工作流服务
 * 
 * 整合以下模块：
 * 1. 角色提取与管理
 * 2. 分镜生成
 * 3. 图像生成
 * 4. 视频生成（角色一致性）
 * 5. 音频合成
 * 6. 批量队列管理
 */

import { chatWithAI } from './ai-assistant-api';
import { getConfig } from './config';

// ==================== 类型定义 ====================

export interface Character {
  id: string;
  name: string;
  role: string;
  description: string;
  appearance: string;
  personality: string;
  referenceImages: string[];
  voiceId?: string;
}

export interface Scene {
  id: string;
  sceneNumber: number;
  description: string;
  characters: string[];
  prompt: string;
  duration: number;
  shotSize: string;
  cameraMove: string;
  notes: string;
  audioText?: string;
  
  // 生成的资源
  image?: string;
  video?: string;
  audio?: string;
}

export interface DramaProduction {
  id: string;
  name: string;
  novelText: string;
  characters: Character[];
  scenes: Scene[];
  status: 'draft' | 'processing' | 'completed' | 'failed';
  createdAt: Date;
  updatedAt: Date;
}

export interface ProductionConfig {
  textModel: string;
  imageModel: string;
  videoModel: string;
  audioModel: string;
  style: string;
  aspectRatio: string;
  enableCharacterConsistency: boolean;
  minRequestInterval: number;
}

// ==================== 配置 ====================

const DEFAULT_CONFIG: ProductionConfig = {
  textModel: 'deepseek-chat',
  imageModel: 'kling-v2',
  videoModel: 'kling-v2-master',
  audioModel: 'minimax-male-qn-jingying',
  style: 'cinematic',
  aspectRatio: '16:9',
  enableCharacterConsistency: true,
  minRequestInterval: 120000
};

const API_BASE_URL = 'https://api.unlimitai.org';

// ==================== 工具函数 ====================

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function generateId(): string {
  return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// ==================== 核心服务类 ====================

export class DramaProductionWorkflow {
  private config: ProductionConfig;
  private apiKey: string;
  private lastRequestTime: number = 0;

  constructor(config?: Partial<ProductionConfig>) {
    const appConfig = getConfig();
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.apiKey = appConfig.apiKey || '';
  }

  /**
   * 步骤1: 从小说中提取角色
   */
  async extractCharacters(novelText: string): Promise<Character[]> {
    console.log('\n📝 步骤1: 提取角色信息...');
    
    const prompt = `分析以下小说，提取所有重要角色。返回JSON格式：

小说文本：
${novelText.substring(0, 3000)}

返回格式：
{
  "characters": [
    {
      "name": "角色名",
      "role": "主角/配角",
      "description": "详细描述",
      "appearance": "外貌特征（用于图像生成，要具体）",
      "personality": "性格特点"
    }
  ]
}`;

    try {
      const response = await this.callTextAPI(prompt);
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      
      if (jsonMatch) {
        const data = JSON.parse(jsonMatch[0]);
        return (data.characters || []).map((c: any) => ({
          id: generateId(),
          ...c,
          referenceImages: []
        }));
      }
      
      return [];
    } catch (error) {
      console.error('提取角色失败:', error);
      throw error;
    }
  }

  /**
   * 步骤2: 为角色生成参考图
   */
  async generateCharacterReferences(
    character: Character,
    count: number = 3
  ): Promise<string[]> {
    console.log(`\n🎨 步骤2: 生成角色参考图 (${character.name})...`);
    
    const angles = ['正面', '侧面', '背面'];
    const images: string[] = [];

    for (let i = 0; i < Math.min(count, 3); i++) {
      const prompt = `${character.appearance}，${angles[i]}视角，${this.config.style}风格，高质量，细节清晰`;
      
      try {
        const imageUrl = await this.generateImage(prompt);
        images.push(imageUrl);
        console.log(`   ✅ ${angles[i]}视角已生成`);
        
        // 速率限制
        if (i < count - 1) {
          await this.waitForRateLimit();
        }
      } catch (error) {
        console.error(`   ❌ ${angles[i]}视角生成失败:`, error);
      }
    }

    return images;
  }

  /**
   * 步骤3: 生成分镜脚本
   */
  async generateStoryboard(
    novelText: string,
    characters: Character[]
  ): Promise<Scene[]> {
    console.log('\n🎬 步骤3: 生成分镜脚本...');
    
    const characterInfo = characters.map(c => 
      `- ${c.name}（${c.role}）：${c.appearance}`
    ).join('\n');

    const prompt = `作为专业导演，为以下小说生成分镜脚本。

角色信息：
${characterInfo}

小说文本：
${novelText.substring(0, 3000)}

要求：
1. 每个场景标注角色和镜头语言
2. 提示词包含角色外貌特征
3. 场景时长3-10秒
4. 总共10-15个场景

返回JSON格式：
{
  "scenes": [
    {
      "sceneNumber": 1,
      "description": "场景描述",
      "characters": ["角色名"],
      "prompt": "详细提示词（包含角色外貌）",
      "duration": 5,
      "shotSize": "medium",
      "cameraMove": "static",
      "notes": "注意事项",
      "audioText": "旁白或对话"
    }
  ]
}`;

    try {
      const response = await this.callTextAPI(prompt);
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      
      if (jsonMatch) {
        const data = JSON.parse(jsonMatch[0]);
        return (data.scenes || []).map((s: any) => ({
          id: generateId(),
          ...s
        }));
      }
      
      return [];
    } catch (error) {
      console.error('生成分镜失败:', error);
      throw error;
    }
  }

  /**
   * 步骤4: 批量生成场景（图像+视频）
   */
  async generateScenes(
    scenes: Scene[],
    characters: Character[],
    onProgress?: (index: number, scene: Scene) => void
  ): Promise<Scene[]> {
    console.log(`\n🎬 步骤4: 批量生成 ${scenes.length} 个场景...`);
    
    const results: Scene[] = [];

    for (let i = 0; i < scenes.length; i++) {
      const scene = scenes[i];
      console.log(`\n${'='.repeat(70)}`);
      console.log(`场景 ${i + 1}/${scenes.length}`);
      console.log(`${'='.repeat(70)}`);

      try {
        // 4.1 生成图像
        console.log(`   📸 生成图像...`);
        const image = await this.generateImage(scene.prompt);
        scene.image = image;
        console.log(`   ✅ 图像已生成`);

        // 等待速率限制
        await this.waitForRateLimit();

        // 4.2 生成视频（使用角色参考图）
        if (this.config.enableCharacterConsistency && scene.characters.length > 0) {
          console.log(`   🎥 生成视频（角色一致性模式）...`);
          
          const characterImages = this.getCharacterReferences(scene.characters, characters);
          
          if (characterImages.length > 0) {
            const video = await this.generateVideoWithReferences(
              scene.prompt,
              image,
              characterImages
            );
            scene.video = video;
            console.log(`   ✅ 视频已生成`);
          } else {
            // 无角色参考图，使用首帧生成
            const video = await this.generateVideo(scene.prompt, image);
            scene.video = video;
            console.log(`   ✅ 视频已生成（首帧模式）`);
          }
        } else {
          // 不启用角色一致性，直接图生视频
          console.log(`   🎥 生成视频（首帧模式）...`);
          const video = await this.generateVideo(scene.prompt, image);
          scene.video = video;
          console.log(`   ✅ 视频已生成`);
        }

        // 等待速率限制
        if (i < scenes.length - 1) {
          await this.waitForRateLimit();
        }

        results.push(scene);
        
        if (onProgress) {
          onProgress(i, scene);
        }

      } catch (error) {
        console.error(`   ❌ 场景 ${i + 1} 生成失败:`, error);
        results.push(scene);
      }
    }

    return results;
  }

  /**
   * 完整工作流执行
   */
  async execute(
    novelText: string,
    projectName: string,
    onProgress?: (step: string, data?: any) => void
  ): Promise<DramaProduction> {
    console.log('\n🎭 开始漫剧制作工作流...\n');

    const production: DramaProduction = {
      id: generateId(),
      name: projectName,
      novelText,
      characters: [],
      scenes: [],
      status: 'processing',
      createdAt: new Date(),
      updatedAt: new Date()
    };

    try {
      // 步骤1: 提取角色
      if (onProgress) onProgress('extracting_characters');
      production.characters = await this.extractCharacters(novelText);
      console.log(`✅ 提取到 ${production.characters.length} 个角色`);

      // 步骤2: 生成角色参考图
      if (onProgress) onProgress('generating_references');
      for (const character of production.characters) {
        character.referenceImages = await this.generateCharacterReferences(character, 3);
        await this.waitForRateLimit();
      }
      console.log(`✅ 角色参考图生成完成`);

      // 步骤3: 生成分镜
      if (onProgress) onProgress('generating_storyboard');
      production.scenes = await this.generateStoryboard(novelText, production.characters);
      console.log(`✅ 生成 ${production.scenes.length} 个场景`);

      // 步骤4: 批量生成场景
      if (onProgress) onProgress('generating_scenes');
      production.scenes = await this.generateScenes(
        production.scenes,
        production.characters,
        (index, scene) => {
          if (onProgress) onProgress('scene_progress', { index, total: production.scenes.length, scene });
        }
      );

      production.status = 'completed';
      production.updatedAt = new Date();
      
      console.log('\n✅ 漫剧制作完成！');
      return production;

    } catch (error) {
      console.error('\n❌ 漫剧制作失败:', error);
      production.status = 'failed';
      production.updatedAt = new Date();
      throw error;
    }
  }

  // ==================== 内部方法 ====================

  /**
   * 调用文本API
   */
  private async callTextAPI(prompt: string): Promise<string> {
    await this.waitForRateLimit();

    const response = await fetch(`${API_BASE_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: this.config.textModel,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`文本API调用失败: ${response.status}`);
    }

    const data = await response.json();
    this.lastRequestTime = Date.now();
    
    return data.choices[0].message.content;
  }

  /**
   * 生成图像
   */
  private async generateImage(prompt: string): Promise<string> {
    await this.waitForRateLimit();

    const response = await fetch(`${API_BASE_URL}/v1/images/generations`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: this.config.imageModel,
        prompt,
        n: 1,
        size: this.config.aspectRatio === '16:9' ? '1024x576' : '576x1024'
      })
    });

    if (!response.ok) {
      throw new Error(`图像生成失败: ${response.status}`);
    }

    const data = await response.json();
    this.lastRequestTime = Date.now();
    
    return data.data[0].url;
  }

  /**
   * 生成视频（首帧模式）
   */
  private async generateVideo(prompt: string, firstFrame: string): Promise<string> {
    await this.waitForRateLimit();

    const content = [
      { type: 'text', text: prompt },
      { type: 'image_url', image_url: { url: firstFrame } }
    ];

    const response = await fetch(`${API_BASE_URL}/volc/v1/contents/generations/tasks`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: this.config.videoModel,
        content
      })
    });

    if (!response.ok) {
      throw new Error(`视频任务创建失败: ${response.status}`);
    }

    const data = await response.json();
    const taskId = data.id || data.task_id;
    this.lastRequestTime = Date.now();

    // 轮询状态
    return await this.pollVideoTask(taskId);
  }

  /**
   * 生成视频（多参考图模式 - 角色一致性）
   */
  private async generateVideoWithReferences(
    prompt: string,
    firstFrame: string,
    referenceImages: string[]
  ): Promise<string> {
    await this.waitForRateLimit();

    const content: any[] = [
      { type: 'text', text: prompt }
    ];

    // 添加角色参考图
    referenceImages.forEach(imgUrl => {
      content.push({
        type: 'image_url',
        image_url: { url: imgUrl },
        role: 'reference_image'
      });
    });

    // 添加首帧
    content.push({
      type: 'image_url',
      image_url: { url: firstFrame }
    });

    const response = await fetch(`${API_BASE_URL}/volc/v1/contents/generations/tasks`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: this.config.videoModel,
        content
      })
    });

    if (!response.ok) {
      throw new Error(`视频任务创建失败: ${response.status}`);
    }

    const data = await response.json();
    const taskId = data.id || data.task_id;
    this.lastRequestTime = Date.now();

    return await this.pollVideoTask(taskId);
  }

  /**
   * 轮询视频任务状态
   */
  private async pollVideoTask(taskId: string): Promise<string> {
    const startTime = Date.now();
    let interval = 5000;

    for (let attempt = 1; attempt <= 60; attempt++) {
      const response = await fetch(
        `${API_BASE_URL}/volc/v1/contents/generations/tasks/${taskId}`,
        {
          headers: { 'Authorization': `Bearer ${this.apiKey}` }
        }
      );

      if (!response.ok) {
        throw new Error(`视频查询失败: ${response.status}`);
      }

      const data = await response.json();
      const status = (data.status || data.task_status || '').toLowerCase();
      const elapsed = Math.round((Date.now() - startTime) / 1000);

      console.log(`      [${attempt}] ${status} (${elapsed}秒)`);

      if (status === 'completed' || status === 'succeeded') {
        return data.video_url || data.output?.video_url;
      }

      if (status === 'failed' || status === 'error') {
        throw new Error(data.error || data.error_message || '视频生成失败');
      }

      await delay(interval);
      interval = Math.min(interval * 1.2, 15000);
    }

    throw new Error('视频生成超时');
  }

  /**
   * 获取角色参考图
   */
  private getCharacterReferences(
    characterNames: string[],
    characters: Character[]
  ): string[] {
    const images: string[] = [];
    
    characterNames.forEach(name => {
      const character = characters.find(c => c.name === name);
      if (character && character.referenceImages.length > 0) {
        images.push(...character.referenceImages.slice(0, 2));
      }
    });

    return images;
  }

  /**
   * 速率限制等待
   */
  private async waitForRateLimit(): Promise<void> {
    const elapsed = Date.now() - this.lastRequestTime;
    
    if (elapsed < this.config.minRequestInterval) {
      const waitTime = this.config.minRequestInterval - elapsed;
      console.log(`⏳ 速率限制：等待 ${Math.round(waitTime / 1000)}秒...`);
      await delay(waitTime);
    }
  }
}
