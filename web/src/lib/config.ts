/**
 * 配置管理（已废弃，请使用 unified-config.ts）
 * 保留此文件是为了向后兼容
 */

import { getUnifiedConfig, getApiKey, saveGlobalApiKey, clearGlobalApiKey, hasApiKey as hasApiKeyUnified } from './unified-config';

interface Config {
  apiKey: string | null;
  apiBaseUrl: string;
}

const STORAGE_KEY = 'comfyui-unlimitai-config';

export function getConfig(): Config {
  // 使用统一配置
  return getUnifiedConfig();
}

export function saveConfig(config: Partial<Config>): void {
  // 如果保存apiKey，使用统一配置
  if (config.apiKey) {
    saveGlobalApiKey(config.apiKey);
  }
}

export function clearConfig(): void {
  clearGlobalApiKey();
}

export function hasApiKey(): boolean {
  return hasApiKeyUnified();
}
