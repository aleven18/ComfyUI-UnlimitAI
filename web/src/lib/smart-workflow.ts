/**
 * 智能创作工作流
 * 
 * 自动化流程：
 * 1. 输入小说 → 自动提取角色
 * 2. 生成角色卡 → 用户选择参考图
 * 3. 生成分镜 → 自动使用角色卡信息
 */

import { chatWithAI } from './ai-assistant-api';
import { getConfig } from './config';

export interface ExtractedCharacter {
  name: string;
  role: string;
  description: string;
  appearance: string;
  personality: string;
  keyScenes: string[];
}

export interface StoryboardScene {
  sceneNumber: number;
  shotSize: string;
  cameraMove: string;
  duration: number;
  description: string;
  characters: string[];
  prompt: string;
  notes: string;
}

/**
 * 从小说中提取角色
 */
export async function extractCharactersFromNovel(novelText: string): Promise<ExtractedCharacter[]> {
  const config = getConfig();
  if (!config.apiKey) {
    throw new Error('请先配置API Key');
  }
  
  const prompt = `分析以下小说文本，提取所有重要角色。返回JSON格式：

小说文本：
${novelText}

返回格式：
{
  "characters": [
    {
      "name": "角色名称",
      "role": "主角/配角/路人",
      "description": "角色描述（外貌、性格、背景）",
      "appearance": "外貌特征（用于图像生成）",
      "personality": "性格特点",
      "keyScenes": ["关键场景1", "关键场景2"]
    }
  ]
}

注意：
1. 只提取有台词或重要情节的角色
2. 外貌描述要具体，适合AI图像生成
3. 关键场景要标注章节或段落`;

  try {
    const response = await chatWithAI(prompt, config.apiKey, { novelText }, 'deepseek-chat');
    const jsonMatch = response.content.match(/\{[\s\S]*\}/);
    
    if (jsonMatch) {
      const data = JSON.parse(jsonMatch[0]);
      return data.characters || [];
    }
    
    return [];
  } catch (error) {
    console.error('提取角色失败:', error);
    throw error;
  }
}

/**
 * 生成分镜脚本（使用角色卡）
 */
export async function generateStoryboardWithCharacters(
  novelText: string,
  characters: ExtractedCharacter[]
): Promise<StoryboardScene[]> {
  const config = getConfig();
  if (!config.apiKey) {
    throw new Error('请先配置API Key');
  }
  
  const characterInfo = characters.map(c => 
    `- ${c.name}（${c.role}）：${c.appearance}`
  ).join('\n');
  
  const prompt = `作为专业导演和分镜师，为以下小说生成分镜脚本。

角色信息：
${characterInfo}

小说文本：
${novelText}

要求：
1. 每个场景都要标注出场角色
2. 提示词要包含角色的外貌特征
3. 镜头语言要专业（远景/中景/近景/特写等）
4. 每个场景时长合理（3-10秒）

返回JSON格式：
{
  "scenes": [
    {
      "sceneNumber": 1,
      "shotSize": "medium",
      "cameraMove": "static",
      "duration": 5,
      "description": "场景描述",
      "characters": ["角色名1", "角色名2"],
      "prompt": "详细的图像生成提示词，包含角色外貌",
      "notes": "拍摄注意事项"
    }
  ]
}`;

  try {
    const response = await chatWithAI(prompt, config.apiKey, { novelText }, 'deepseek-chat');
    const jsonMatch = response.content.match(/\{[\s\S]*\}/);
    
    if (jsonMatch) {
      const data = JSON.parse(jsonMatch[0]);
      return data.scenes || [];
    }
    
    return [];
  } catch (error) {
    console.error('生成分镜失败:', error);
    throw error;
  }
}

/**
 * 根据角色卡生成角色参考图提示词
 */
export function generateCharacterPrompt(character: ExtractedCharacter): string {
  return `专业人物肖像摄影，${character.appearance}，${character.description}，高清，细节丰富，电影质感`;
}
