import { useEffect, useState } from 'react';
import { comfyUIClient } from '@/lib/comfyui-client';
import { WorkflowManager } from '@/lib/workflow-manager';
import { useAppStore } from '@/store';
import { Shot } from '@/lib/storyboard-to-workflow';
import { StoryboardToNovelConverter } from '@/lib/storyboard-to-novel';
import { 
  executeWorkflowWithProgress, 
  filterOutputsByType,
  WorkflowOutput 
} from '@/lib/comfyui-helpers';
import { getApiKey } from '@/lib/unified-config';

export function useComfyUI() {
  const {
    params,
    preset,
    storyboard,
    result,
    setResult,
    progress,
    setProgress,
    currentNode,
    setCurrentNode,
    outputs,
    addOutput,
    clearOutputs,
    logs,
    addLog,
    clearLogs,
  } = useAppStore();

  const [isConverting, setIsConverting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [workflowOutputs, setWorkflowOutputs] = useState<WorkflowOutput[]>([]);

  useEffect(() => {
    return () => {
      comfyUIClient.disconnectWebSocket();
    };
  }, []);

  const getEffectiveApiKey = () => {
    return params.apiKey || getApiKey() || '';
  };

  const ts = () => new Date().toLocaleTimeString();

  const startConversionWithStoryboard = async (shots: Shot[]) => {
    if (isConverting) return;
    try {
      setIsConverting(true);
      setError(null);
      clearOutputs();
      clearLogs();
      setProgress(0);
      setWorkflowOutputs([]);
      
      const apiKey = getEffectiveApiKey();

      addLog(`[${ts()}] 开始分镜视频生成...`);
      addLog(`[${ts()}] 总镜头数: ${shots.length}`);
      
      const novel = StoryboardToNovelConverter.convertToNovel(shots);
      
      addLog(`[${ts()}] 分镜已转换为小说格式`);
      
      const workflowParams = StoryboardToNovelConverter.toWorkflowParams(novel, {
        apiKey,
        imageModel: params.imageModel || 'flux-pro',
        videoModel: params.videoModel || 'kling-v2',
        audioEnabled: true
      });
      
      const template = WorkflowManager.getTemplate(preset);
      
      const fullParams = {
        ...WorkflowManager.getDefaultParams(preset),
        ...params,
        ...workflowParams,
        apiKey,
      } as any;
      
      const workflow = WorkflowManager.fillWorkflow(template, fullParams);
      
      addLog(`[${ts()}] 工作流已准备完成`);
      
      const { promptId, outputs: wfOutputs } = await executeWorkflowWithProgress(
        workflow,
        (progressData) => {
          const percent = (progressData.value / progressData.max) * 100;
          setProgress(percent);
        },
        (nodeId) => {
          setCurrentNode(nodeId);
        },
        () => {}
      );
      
      setWorkflowOutputs(wfOutputs);

      wfOutputs.forEach(output => {
        addOutput({ type: output.type, filename: output.filename, url: output.url });
      });
      
      setResult({
        promptId,
        status: 'completed',
        progress: 100,
        outputs: wfOutputs.map(o => ({ type: o.type, filename: o.filename, url: o.url }))
      });
      
      setIsConverting(false);
      
    } catch (err: any) {
      setError(err.message || '转换失败');
      setIsConverting(false);
      addLog(`[${ts()}] 错误: ${err.message}`);
    }
  };

  const startStoryboardConversion = async () => {
    if (isConverting) return;
    try {
      setIsConverting(true);
      setError(null);
      clearOutputs();
      clearLogs();
      setProgress(0);
      setWorkflowOutputs([]);

      const apiKey = getEffectiveApiKey();

      const errors = WorkflowManager.validateStoryboardPro(apiKey, storyboard);
      if (errors.length > 0) throw new Error(errors.join('\n'));

      addLog(`[${ts()}] 开始 Storyboard Pro 生成...`);
      addLog(`[${ts()}] ${storyboard.storyboardCount} 段分镜 · ${storyboard.duration}s · ${storyboard.videoModel}`);

      const template = WorkflowManager.getStoryboardProTemplate();
      const workflow = WorkflowManager.fillStoryboardProWorkflow(template, apiKey, storyboard);

      const STEP_LABELS = [
        'Step 1/6: 角色与故事分析',
        'Step 2/6: 生成视频脚本',
        'Step 3/6: 生成参考图',
        'Step 4/6: 生成对白音频',
        'Step 5/6: 生成故事板视频',
        'Step 6/6: 音视频混合',
      ];

      const { promptId, outputs: wfOutputs } = await executeWorkflowWithProgress(
        workflow,
        (progressData) => {
          const percent = progressData.max > 0
            ? (progressData.value / progressData.max) * 100
            : 0;
          setProgress(percent);
          const stepIdx = Math.min(5, Math.floor(percent * 6 / 100));
          setCurrentNode(STEP_LABELS[stepIdx]);
        },
        (nodeId) => {
          setCurrentNode(nodeId);
          addLog(`[${ts()}] 执行节点: ${nodeId}`);
        },
        (nodeId, output) => {
          addOutput(output);
        },
      );

      setWorkflowOutputs(wfOutputs);

      setResult({
        promptId,
        status: 'completed',
        progress: 100,
        outputs: wfOutputs.map(o => ({ type: o.type, filename: o.filename, url: o.url })),
      });

      addLog(`[${ts()}] Storyboard Pro 生成完成!`);
      setIsConverting(false);
    } catch (err: any) {
      setError(err.message || '转换失败');
      setIsConverting(false);
      addLog(`[${ts()}] 错误: ${err.message}`);
    }
  };

  const startConversion = async () => {
    if (isConverting) return;
    try {
      setIsConverting(true);
      setError(null);
      clearOutputs();
      clearLogs();
      setProgress(0);
      setWorkflowOutputs([]);

      const apiKey = getEffectiveApiKey();
      const fullParams = { ...WorkflowManager.getDefaultParams(preset), ...params, apiKey, preset } as any;
      
      const errors = WorkflowManager.validateParams(fullParams);
      if (errors.length > 0) throw new Error(errors.join('\n'));
      
      addLog(`[${ts()}] 开始转换...`);
      addLog(`[${ts()}] 使用预设: ${preset}`);
      
      const template = WorkflowManager.getTemplate(preset);
      const workflow = WorkflowManager.fillWorkflow(template, fullParams);

      const { promptId, outputs: wfOutputs } = await executeWorkflowWithProgress(
        workflow,
        (progressData) => {
          const percent = progressData.max > 0
            ? (progressData.value / progressData.max) * 100
            : 0;
          setProgress(percent);
          addLog(`[${ts()}] 进度: ${percent.toFixed(1)}%`);
        },
        (nodeId) => {
          setCurrentNode(nodeId);
          addLog(`[${ts()}] 执行节点: ${nodeId}`);
        },
        (nodeId, output) => {
          addLog(`[${ts()}] 节点完成: ${nodeId}`);
        },
      );

      setWorkflowOutputs(wfOutputs);

      setResult({
        promptId,
        status: 'completed',
        progress: 100,
        outputs: wfOutputs.map(o => ({ type: o.type, filename: o.filename, url: o.url })),
      });

      addLog(`[${ts()}] 转换完成!`);
      setIsConverting(false);
    } catch (err: any) {
      setError(err.message || '转换失败');
      setIsConverting(false);
      addLog(`[${ts()}] 错误: ${err.message}`);
    }
  };

  const stopConversion = async () => {
    try {
      await comfyUIClient.interrupt();
      setIsConverting(false);
      setResult(result ? { ...result, status: 'error', error: '用户中断' } : null);
      addLog(`[${ts()}] 任务已中断`);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return {
    startConversion,
    startConversionWithStoryboard,
    startStoryboardConversion,
    stopConversion,
    isConverting,
    error,
    progress,
    currentNode,
    outputs,
    logs,
    workflowOutputs,
  };
}
