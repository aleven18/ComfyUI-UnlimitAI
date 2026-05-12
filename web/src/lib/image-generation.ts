/**
 * 图像生成API
 * 
 * 支持多个模型，自动切换
 * 添加超时和速率限制保护
 */

import { getUnifiedConfig } from './unified-config';

const API_BASE_URL = () => getUnifiedConfig().apiBaseUrl;

// 默认的图像生成模型列表（按优先级）
const DEFAULT_IMAGE_MODELS = [
  'kling-v2',
  'flux-pro',
];

// 获取可用的图像模型列表
function getAvailableModels(): string[] {
  try {
    const saved = localStorage.getItem('available_image_models');
    if (saved) {
      const models = JSON.parse(saved);
      if (Array.isArray(models) && models.length > 0) {
        console.log('✅ 使用已保存的可用模型:', models);
        return models;
      }
    }
  } catch (e) {
    console.warn('读取保存的模型列表失败，使用默认列表');
  }
  return DEFAULT_IMAGE_MODELS;
}

// 请求超时时间（30秒）
const TIMEOUT = 30000;

// 记录上次请求时间，避免请求过快
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 3000; // 最小请求间隔3秒

/**
 * 延迟函数
 */
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 带超时的fetch请求
 */
async function fetchWithTimeout(url: string, options: RequestInit, timeout: number): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function generateCharacterImage(prompt: string): Promise<string> {
  const apiKey = localStorage.getItem('unlimitai_api_key');
  
  if (!apiKey) {
    throw new Error('请先配置API Key');
  }
  
  console.log('🎨 开始生成角色参考图...');
  console.log('📝 提示词:', prompt);
  
  // 获取可用的模型列表
  const IMAGE_MODELS = getAvailableModels();
  console.log('📋 可用模型列表:', IMAGE_MODELS);
  
  // 尝试不同的模型
  for (let i = 0; i < IMAGE_MODELS.length; i++) {
    const model = IMAGE_MODELS[i];
    
    try {
      // 检查请求间隔，避免触发速率限制
      const now = Date.now();
      const timeSinceLastRequest = now - lastRequestTime;
      
      if (timeSinceLastRequest < MIN_REQUEST_INTERVAL) {
        const waitTime = MIN_REQUEST_INTERVAL - timeSinceLastRequest;
        console.log(`⏳ 等待 ${waitTime}ms 以避免速率限制...`);
        await delay(waitTime);
      }
      
      console.log(`🔄 尝试使用模型: ${model} (${i + 1}/${IMAGE_MODELS.length})`);
      lastRequestTime = Date.now();
      
      // 所有可用模型都使用1024x1024尺寸
      const imageSize = '1024x1024';
      
      const response = await fetchWithTimeout(
        `${API_BASE_URL()}/v1/images/generations`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model: model,
            prompt: prompt,
            n: 1,
            size: imageSize
          })
        },
        TIMEOUT
      );
      
      if (!response.ok) {
        const error = await response.json();
        
        // 429错误：速率限制
        if (response.status === 429) {
          console.log(`⚠️ 模型 ${model} 遇到速率限制 (429)`);
          
          // 如果还有其他模型可以尝试，继续
          if (i < IMAGE_MODELS.length - 1) {
            console.log(`⏳ 等待3秒后尝试下一个模型...`);
            await delay(3000);
            continue;
          } else {
            throw new Error('API请求过于频繁，请等待几分钟后再试，或使用"上传本地图片"功能。');
          }
        }
        
        // 如果是模型不可用的错误，尝试下一个模型
        if (error.error?.message?.includes('无可用渠道') || 
            error.error?.message?.includes('no available channel')) {
          console.log(`⚠️ 模型 ${model} 无可用渠道，尝试下一个...`);
          continue;
        }
        
        console.error(`❌ 模型 ${model} 返回错误:`, error);
        throw new Error(error.error?.message || `API错误: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.data && data.data[0] && data.data[0].url) {
        console.log(`✅ 成功使用模型: ${model}`);
        console.log(`🖼️ 图片URL:`, data.data[0].url);
        return data.data[0].url;
      }
      
      throw new Error('未能获取生成的图片');
      
    } catch (error: any) {
      // 超时错误
      if (error.name === 'AbortError') {
        console.log(`⏱️ 模型 ${model} 请求超时，尝试下一个...`);
        continue;
      }
      
      // 如果是最后一个模型，抛出错误
      if (i === IMAGE_MODELS.length - 1) {
        console.error('❌ 所有模型都尝试失败:', error);
        
        // 提供更友好的错误提示
        if (error.message.includes('无可用渠道') || error.message.includes('请求过于频繁')) {
          throw error;
        }
        
        throw new Error('所有图像生成模型都暂时不可用。\n\n建议：\n1. 等待几分钟后重试\n2. 使用"上传本地图片"功能');
      }
      
      // 否则继续尝试下一个模型
      console.log(`⚠️ 模型 ${model} 失败:`, error.message);
      
      // 在尝试下一个模型前等待一下
      if (i < IMAGE_MODELS.length - 1) {
        await delay(2000);
      }
    }
  }
  
  throw new Error('所有图像生成模型都不可用，建议使用"上传本地图片"功能。');
}
