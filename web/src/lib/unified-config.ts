/**
 * 统一配置管理
 * 
 * API Key 优先级：
 * 1. 项目级 API Key (最高优先级)
 * 2. 全局 API Key
 * 3. 环境变量
 */

import { useProjectStore } from '@/store/projectStore';

const GLOBAL_API_KEY_STORAGE = 'unlimitai_api_key';

export interface UnifiedConfig {
  apiKey: string | null;
  apiBaseUrl: string;
}

/**
 * 获取API Key（统一入口）
 */
export function getApiKey(): string | null {
  // 1. 优先检查项目级API Key
  try {
    const projectStore = useProjectStore.getState();
    if (projectStore.settings.apiKey) {
      return projectStore.settings.apiKey;
    }
  } catch (e) {
    // 项目store可能还未初始化
  }
  
  // 2. 检查全局API Key
  const globalKey = localStorage.getItem(GLOBAL_API_KEY_STORAGE);
  if (globalKey) {
    return globalKey;
  }
  
  // 3. 环境变量
  return import.meta.env.VITE_UNLIMITAI_API_KEY || null;
}

/**
 * 保存全局API Key
 */
export function saveGlobalApiKey(apiKey: string): void {
  localStorage.setItem(GLOBAL_API_KEY_STORAGE, apiKey);
}

/**
 * 清除全局API Key
 */
export function clearGlobalApiKey(): void {
  localStorage.removeItem(GLOBAL_API_KEY_STORAGE);
}

/**
 * 检查是否有可用的API Key
 */
export function hasApiKey(): boolean {
  const key = getApiKey();
  return key !== null && key !== '' && key !== 'your_api_key_here';
}

/**
 * 获取统一配置
 */
export function getUnifiedConfig(): UnifiedConfig {
  return {
    apiKey: getApiKey(),
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'https://api.unlimitai.org'
  };
}
