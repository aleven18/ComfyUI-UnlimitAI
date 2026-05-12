import { comfyUIClient } from './comfyui-client';
import { HistoryEntry, ComfyUIOutputMedia, ComfyUIWorkflow } from '@/types';

export interface WorkflowOutput {
  type: 'image' | 'video' | 'audio' | 'text';
  nodeId: string;
  filename: string;
  subfolder?: string;
  type_folder: string;
  url: string;
  text?: string;
  outputName?: string;
}

export async function waitForWorkflowCompletion(
  promptId: string,
  timeout: number = 600000,
  checkInterval: number = 2000
): Promise<HistoryEntry> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    try {
      const history = await comfyUIClient.getHistory(promptId);
      
      if (!history) {
        await sleep(checkInterval);
        continue;
      }
      
      if (history.status.completed || history.outputs) {
        return {
          ...history,
          status: history.status
        };
      }
      
      if (!history.status.completed && history.status.status_str === 'error') {
        const errorEntry: HistoryEntry = {
          ...history,
          status: history.status
        };
        return errorEntry;
      }
      
      await sleep(checkInterval);
      
    } catch (error) {
      console.error('Error checking workflow status:', error);
      await sleep(checkInterval);
    }
  }
  
  throw new Error(`Workflow execution timeout after ${timeout / 1000} seconds`);
}

const KNOWN_ARRAY_KEYS = new Set(['images', 'videos', 'audio', 'text']);

export function extractOutputs(history: HistoryEntry): WorkflowOutput[] {
  const outputs: WorkflowOutput[] = [];
  
  if (!history.outputs) {
    return outputs;
  }
  
  for (const nodeId in history.outputs) {
    const nodeOutput = history.outputs[nodeId];
    
    if (nodeOutput.images && Array.isArray(nodeOutput.images)) {
      nodeOutput.images.forEach((img: ComfyUIOutputMedia) => {
        outputs.push({
          type: 'image',
          nodeId,
          filename: img.filename,
          subfolder: img.subfolder,
          type_folder: img.type || 'output',
          url: comfyUIClient.getImageUrl(img.filename, img.subfolder, img.type)
        });
      });
    }
    
    if (nodeOutput.videos && Array.isArray(nodeOutput.videos)) {
      nodeOutput.videos.forEach((vid: ComfyUIOutputMedia) => {
        outputs.push({
          type: 'video',
          nodeId,
          filename: vid.filename,
          subfolder: vid.subfolder,
          type_folder: vid.type || 'output',
          url: comfyUIClient.getImageUrl(vid.filename, vid.subfolder, vid.type)
        });
      });
    }
    
    if (nodeOutput.audio && Array.isArray(nodeOutput.audio)) {
      nodeOutput.audio.forEach((aud: ComfyUIOutputMedia) => {
        outputs.push({
          type: 'audio',
          nodeId,
          filename: aud.filename,
          subfolder: aud.subfolder,
          type_folder: aud.type || 'output',
          url: comfyUIClient.getImageUrl(aud.filename, aud.subfolder, aud.type)
        });
      });
    }

    if (nodeOutput.text && Array.isArray(nodeOutput.text)) {
      nodeOutput.text.forEach((txt: unknown) => {
        const txtRec = txt as Record<string, unknown>;
        outputs.push({
          type: 'text', nodeId, filename: '', type_folder: 'output', url: '',
          text: typeof txt === 'string' ? txt : String(txtRec.text || txt),
          outputName: txtRec.name as string | undefined,
        });
      });
    }

    for (const key of Object.keys(nodeOutput)) {
      if (KNOWN_ARRAY_KEYS.has(key)) continue;
      const val = (nodeOutput as Record<string, unknown>)[key];
      if (typeof val === 'string' && val.length > 0) {
        outputs.push({
          type: 'text', nodeId, filename: '', type_folder: 'output', url: '',
          text: val, outputName: key,
        });
      }
    }
  }
  
  return outputs;
}

export function filterOutputsByType(
  outputs: WorkflowOutput[],
  type: 'image' | 'video' | 'audio' | 'text'
): WorkflowOutput[] {
  return outputs.filter(output => output.type === type);
}

export function getFirstVideoOutput(outputs: WorkflowOutput[]): WorkflowOutput | null {
  return outputs.find(output => output.type === 'video') || null;
}

export function getVideoUrls(outputs: WorkflowOutput[]): string[] {
  return outputs
    .filter(output => output.type === 'video')
    .map(output => output.url);
}

export function getTextOutputs(outputs: WorkflowOutput[]): WorkflowOutput[] {
  return outputs.filter(output => output.type === 'text');
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function executeWorkflowWithProgress(
  workflow: ComfyUIWorkflow,
  onProgress?: (data: { value: number; max: number; nodeId?: string }) => void,
  onNodeStart?: (nodeId: string) => void,
  onNodeComplete?: (nodeId: string, output: Record<string, unknown>) => void
): Promise<{ promptId: string; outputs: WorkflowOutput[] }> {
  comfyUIClient.connectWebSocket({
    onProgress: (progressData) => {
      onProgress?.({
        value: progressData.value,
        max: progressData.max
      });
    },
    onExecuting: (nodeId) => {
      onNodeStart?.(nodeId);
    },
    onExecuted: (nodeId, output) => {
      onNodeComplete?.(nodeId, output);
    },
    onError: (error) => {
      console.error('Workflow WebSocket error:', error);
    },
  });

  try {
    const promptId = await comfyUIClient.queuePrompt(workflow);
    const history = await waitForWorkflowCompletion(promptId);

    if (!history.status.completed) {
      throw new Error('Workflow execution failed');
    }

    const outputs = extractOutputs(history);
    comfyUIClient.disconnectWebSocket();
    return { promptId, outputs };
  } catch (error) {
    comfyUIClient.disconnectWebSocket();
    throw error;
  }
}
