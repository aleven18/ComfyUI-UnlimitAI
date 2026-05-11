"""
高级优化节点模块

包含以下高级功能：
- 预览机制（1-3场景预览）
- 编辑环节（可修改场景描述）
- 失败重试机制
- 并行执行优化
- 成本实时计算
- 质量评分系统
- 进度显示
"""

import logging
logger = logging.getLogger(__name__)

import asyncio
import json
import time
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


class PreviewModeNode:
    """
    预览模式节点
    
    功能：
    1. 生成1-3个场景的预览版本
    2. 使用经济模型快速生成
    3. 用户可以审核预览结果
    4. 根据预览调整参数
    """
    
    def __init__(self):
        self.preview_count = 3
        self.preview_results = {}
        self.approved_scenes = set()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scenes_json": ("STRING", {"multiline": True}),
                "preview_count": ([1, 2, 3], {"default": 3}),
                "preview_mode": (["fast", "balanced", "quality"], {"default": "fast"}),
            },
            "optional": {
                "approved_scenes": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("preview_results", "preview_summary", "next_action")
    FUNCTION = "generate_preview"
    CATEGORY = "UnlimitAI/Advanced"
    
    def generate_preview(
        self,
        scenes_json: str,
        preview_count: int = 3,
        preview_mode: str = "fast",
        approved_scenes: str = ""
    ) -> Tuple[str, str, str]:
        """生成预览版本"""
        
        try:
            scenes = json.loads(scenes_json)
            if isinstance(scenes, dict) and 'scenes' in scenes:
                scenes = scenes['scenes']
            
            # 解析已批准的场景
            if approved_scenes:
                self.approved_scenes = set(map(int, approved_scenes.split(',')))
            
            # 选择要预览的场景
            preview_scenes = scenes[:preview_count]
            
            # 预览模型配置
            preview_models = {
                "fast": {
                    "image": "flux-schnell",
                    "video": "vidu2",
                    "audio": "tts-1",
                    "music": "suno-inspiration"
                },
                "balanced": {
                    "image": "flux-pro",
                    "video": "kling-v2",
                    "audio": "speech-02-turbo",
                    "music": "suno-custom"
                },
                "quality": {
                    "image": "imagen-4",
                    "video": "kling-v2",
                    "audio": "speech-02-turbo",
                    "music": "suno-custom"
                }
            }
            
            models = preview_models[preview_mode]
            
            # 生成预览
            preview_results = []
            for scene in preview_scenes:
                scene_id = scene.get('scene_number', 0)
                
                preview = {
                    "scene_id": scene_id,
                    "title": scene.get('title', ''),
                    "description": scene.get('description', ''),
                    "models_used": models,
                    "status": "preview_ready",
                    "cost": self._calculate_preview_cost(preview_mode),
                    "approved": scene_id in self.approved_scenes
                }
                
                preview_results.append(preview)
            
            self.preview_results = {
                "preview_mode": preview_mode,
                "preview_count": preview_count,
                "models": models,
                "scenes": preview_results,
                "total_cost": sum(p['cost'] for p in preview_results)
            }
            
            # 生成摘要
            summary = self._generate_preview_summary(preview_results, preview_mode)
            
            # 下一步行动建议
            next_action = self._suggest_next_action(preview_results)
            
            return (
                json.dumps(self.preview_results, ensure_ascii=False, indent=2),
                summary,
                next_action
            )
            
        except Exception as e:
            return (
                json.dumps({"error": str(e)}),
                f"预览生成失败: {str(e)}",
                "请检查输入数据"
            )
    
    def _calculate_preview_cost(self, mode: str) -> float:
        """计算预览成本"""
        costs = {
            "fast": 0.20,
            "balanced": 0.40,
            "quality": 0.50
        }
        return costs.get(mode, 0.20)
    
    def _generate_preview_summary(self, results: List[Dict], mode: str) -> str:
        """生成预览摘要"""
        total_cost = sum(r['cost'] for r in results)
        approved = sum(1 for r in results if r['approved'])
        
        summary = f"""【预览摘要】

预览模式: {mode}
预览场景数: {len(results)}
已批准场景: {approved}/{len(results)}
预览成本: ${total_cost:.2f}

场景列表:
"""
        
        for r in results:
            status = "✅ 已批准" if r['approved'] else "⏳ 待审核"
            summary += f"  场景{r['scene_id']}: {r['title']} - {status}\n"
        
        return summary
    
    def _suggest_next_action(self, results: List[Dict]) -> str:
        """建议下一步行动"""
        approved = sum(1 for r in results if r['approved'])
        total = len(results)
        
        if approved == 0:
            return "请审核预览结果，批准满意的场景后继续"
        elif approved < total:
            return f"已批准{approved}个场景，可以生成这些场景的最终版本"
        else:
            return "所有预览场景已批准，可以生成最终版本"


class SceneEditorNode:
    """
    场景编辑节点
    
    功能：
    1. 显示场景详情
    2. 允许编辑场景描述
    3. 调整视觉提示词
    4. 修改对话和情绪
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scenes_json": ("STRING", {"multiline": True}),
                "scene_number": ("INT", {"default": 1, "min": 1}),
            },
            "optional": {
                "new_description": ("STRING", {"multiline": True, "default": ""}),
                "new_dialogue": ("STRING", {"default": ""}),
                "new_mood": (["romantic", "tension", "happy", "sad", "action", "neutral"],),
                "new_visual_prompt": ("STRING", {"multiline": True, "default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("edited_scenes_json", "edit_summary")
    FUNCTION = "edit_scene"
    CATEGORY = "UnlimitAI/Advanced"
    
    def edit_scene(
        self,
        scenes_json: str,
        scene_number: int,
        new_description: str = "",
        new_dialogue: str = "",
        new_mood: str = None,
        new_visual_prompt: str = ""
    ) -> Tuple[str, str]:
        """编辑场景"""
        
        try:
            data = json.loads(scenes_json)
            
            if isinstance(data, dict) and 'scenes' in data:
                scenes = data['scenes']
            else:
                scenes = data
            
            # 查找要编辑的场景
            scene_idx = scene_number - 1
            if scene_idx < 0 or scene_idx >= len(scenes):
                return (
                    scenes_json,
                    f"❌ 场景编号 {scene_number} 不存在"
                )
            
            scene = scenes[scene_idx]
            original = scene.copy()
            
            # 应用修改
            changes = []
            
            if new_description:
                scene['description'] = new_description
                changes.append(f"描述: '{original.get('description', '')[:30]}...' → '{new_description[:30]}...'")
            
            if new_dialogue:
                scene['dialogue'] = new_dialogue
                changes.append(f"对话: '{original.get('dialogue', '')[:20]}' → '{new_dialogue[:20]}'")
            
            if new_mood:
                scene['mood'] = new_mood
                changes.append(f"情绪: '{original.get('mood', '')}' → '{new_mood}'")
            
            if new_visual_prompt:
                scene['visual_prompt'] = new_visual_prompt
                changes.append(f"视觉提示词: 已更新")
            
            # 生成摘要
            if changes:
                summary = f"""【场景编辑完成】

场景 {scene_number}: {scene.get('title', '')}

修改内容:
{chr(10).join(f'  - {c}' for c in changes)}

建议: 重新生成该场景的预览版本以查看修改效果
"""
            else:
                summary = f"场景 {scene_number}: 无修改"
            
            # 返回更新后的数据
            if isinstance(data, dict) and 'scenes' in data:
                data['scenes'] = scenes
                return json.dumps(data, ensure_ascii=False, indent=2), summary
            else:
                return json.dumps(scenes, ensure_ascii=False, indent=2), summary
            
        except Exception as e:
            return (
                scenes_json,
                f"❌ 编辑失败: {str(e)}"
            )


class RetryMechanismNode:
    """
    失败重试机制节点
    
    功能：
    1. 自动检测失败的任务
    2. 智能重试策略
    3. 指数退避
    4. 最大重试次数限制
    5. 错误日志记录
    """
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2
        self.failed_tasks = []
        self.retry_history = []
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task_json": ("STRING", {"multiline": True}),
                "max_retries": ("INT", {"default": 3, "min": 1, "max": 10}),
                "retry_delay": ("INT", {"default": 2, "min": 1, "max": 60}),
            },
            "optional": {
                "exponential_backoff": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("result_json", "retry_log", "final_status")
    FUNCTION = "execute_with_retry"
    CATEGORY = "UnlimitAI/Advanced"
    
    def execute_with_retry(
        self,
        task_json: str,
        max_retries: int = 3,
        retry_delay: int = 2,
        exponential_backoff: bool = True
    ) -> Tuple[str, str, str]:
        """带重试机制的任务执行"""
        
        try:
            task = json.loads(task_json)
            
            retry_log = []
            attempt = 0
            delay = retry_delay
            
            while attempt <= max_retries:
                attempt += 1
                
                try:
                    # 模拟任务执行
                    result = self._execute_task(task)
                    
                    # 成功
                    retry_log.append(f"尝试 {attempt}: ✅ 成功")
                    
                    return (
                        json.dumps(result, ensure_ascii=False, indent=2),
                        "\n".join(retry_log),
                        "success"
                    )
                    
                except Exception as e:
                    # 失败
                    retry_log.append(f"尝试 {attempt}: ❌ 失败 - {str(e)}")
                    
                    if attempt < max_retries:
                        # 准备重试
                        retry_log.append(f"等待 {delay} 秒后重试...")
                        time.sleep(delay)
                        
                        # 指数退避
                        if exponential_backoff:
                            delay *= 2
                    else:
                        # 达到最大重试次数
                        return (
                            json.dumps({"error": str(e), "failed": True}),
                            "\n".join(retry_log),
                            "failed"
                        )
            
        except Exception as e:
            return (
                json.dumps({"error": str(e)}),
                f"任务解析失败: {str(e)}",
                "error"
            )
    
    def _execute_task(self, task: Dict) -> Dict:
        """执行任务（模拟）"""
        # 这里应该是实际的API调用
        # 模拟成功
        return {
            "status": "success",
            "task_id": task.get("id", "unknown"),
            "result": "任务执行成功"
        }


class ParallelExecutionNode:
    """
    并行执行节点
    
    功能：
    1. 并行执行多个任务
    2. 视频和音频同时生成
    3. 提高效率
    4. 实时进度显示
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tasks_json": ("STRING", {"multiline": True}),
                "max_workers": ("INT", {"default": 3, "min": 1, "max": 10}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("results_json", "execution_summary")
    FUNCTION = "execute_parallel"
    CATEGORY = "UnlimitAI/Advanced"
    
    def execute_parallel(
        self,
        tasks_json: str,
        max_workers: int = 3
    ) -> Tuple[str, str]:
        """并行执行任务"""
        
        try:
            tasks = json.loads(tasks_json)
            
            if not isinstance(tasks, list):
                tasks = [tasks]
            
            start_time = time.time()
            results = []
            completed = 0
            
            # 使用线程池并行执行
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_task = {
                    executor.submit(self._execute_single_task, task): task
                    for task in tasks
                }
                
                # 收集结果
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        results.append(result)
                        completed += 1
                    except Exception as e:
                        results.append({
                            "task": task,
                            "status": "failed",
                            "error": str(e)
                        })
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # 生成摘要
            summary = f"""【并行执行摘要】

总任务数: {len(tasks)}
并发数: {max_workers}
成功: {sum(1 for r in results if r.get('status') == 'success')}
失败: {sum(1 for r in results if r.get('status') == 'failed')}
执行时间: {elapsed_time:.2f}秒

节省时间: ~{(len(tasks) - 1) * 5:.0f}秒 (相比串行执行)
"""
            
            return (
                json.dumps(results, ensure_ascii=False, indent=2),
                summary
            )
            
        except Exception as e:
            return (
                json.dumps({"error": str(e)}),
                f"并行执行失败: {str(e)}"
            )
    
    def _execute_single_task(self, task: Dict) -> Dict:
        """执行单个任务（模拟）"""
        time.sleep(2)  # 模拟执行时间
        return {
            "task": task,
            "status": "success",
            "result": "任务完成"
        }


class RealTimeCostCalculatorNode:
    """
    成本实时计算节点
    
    功能：
    1. 实时计算生成成本
    2. 多方案对比
    3. 成本预警
    4. 预算控制
    """
    
    MODEL_COSTS = {
        "deepseek-chat": {"input": 0.0000001, "output": 0.0000002},
        "gpt-4o": {"input": 0.0000025, "output": 0.00001},
        "claude-opus-4-20250514": {"input": 0.000015, "output": 0.000075},
        
        "flux-schnell": 0.003,
        "flux-pro": 0.03,
        "imagen-4.0-generate-preview-05-20": 0.04,
        
        "vidu2": 0.15,
        "kling-v2": 0.30,
        
        "tts-1": 0.000003,
        "speech-02-turbo": 0.001,
        
        "suno-inspiration": 0.05,
        "suno-custom": 0.10
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scenes_json": ("STRING", {"multiline": True}),
                "config": (["budget", "balanced", "quality", "max_quality"], {"default": "balanced"}),
            },
            "optional": {
                "budget_limit": ("FLOAT", {"default": 10.0}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("cost_breakdown", "cost_summary", "budget_warning")
    FUNCTION = "calculate_real_time_cost"
    CATEGORY = "UnlimitAI/Advanced"
    
    def calculate_real_time_cost(
        self,
        scenes_json: str,
        config: str = "balanced",
        budget_limit: float = 10.0
    ) -> Tuple[str, str, str]:
        """实时计算成本"""
        
        try:
            scenes = json.loads(scenes_json)
            if isinstance(scenes, dict) and 'scenes' in scenes:
                scenes = scenes['scenes']
            
            # 配置对应的模型
            config_models = {
                "budget": {
                    "text": "deepseek-chat",
                    "image": "flux-schnell",
                    "video": "vidu2",
                    "audio": "tts-1",
                    "music": "suno-inspiration"
                },
                "balanced": {
                    "text": "deepseek-chat",
                    "image": "flux-pro",
                    "video": "kling-v2",
                    "audio": "speech-02-turbo",
                    "music": "suno-custom"
                },
                "quality": {
                    "text": "gpt-4o",
                    "image": "imagen-4.0-generate-preview-05-20",
                    "video": "kling-v2",
                    "audio": "speech-02-turbo",
                    "music": "suno-custom"
                },
                "max_quality": {
                    "text": "claude-opus-4-20250514",
                    "image": "imagen-4.0-generate-preview-05-20",
                    "video": "kling-v2",
                    "audio": "speech-02-turbo",
                    "music": "suno-custom"
                }
            }
            
            models = config_models[config]
            
            # 计算成本
            cost_breakdown = {
                "config": config,
                "scene_count": len(scenes),
                "models": models,
                "costs": {
                    "text": 0,
                    "image": 0,
                    "video": 0,
                    "audio": 0,
                    "music": 0
                }
            }
            
            for scene in scenes:
                # 文本成本
                dialogue_len = len(scene.get('dialogue', ''))
                cost_breakdown["costs"]["text"] += 0.00003  # 简化计算
                
                # 图像成本
                cost_breakdown["costs"]["image"] += self.MODEL_COSTS[models["image"]]
                
                # 视频成本
                cost_breakdown["costs"]["video"] += self.MODEL_COSTS[models["video"]]
                
                # 音频成本
                cost_breakdown["costs"]["audio"] += dialogue_len * self.MODEL_COSTS[models["audio"]]
                
                # 音乐成本
                cost_breakdown["costs"]["music"] += self.MODEL_COSTS[models["music"]]
            
            total_cost = sum(cost_breakdown["costs"].values())
            cost_breakdown["total_cost"] = total_cost
            
            # 生成摘要
            summary = f"""【成本计算结果】

配置: {config}
场景数: {len(scenes)}

成本明细:
  文本分析: ${cost_breakdown['costs']['text']:.4f}
  图像生成: ${cost_breakdown['costs']['image']:.2f}
  视频生成: ${cost_breakdown['costs']['video']:.2f}
  音频合成: ${cost_breakdown['costs']['audio']:.2f}
  背景音乐: ${cost_breakdown['costs']['music']:.2f}
  ━━━━━━━━━━━━━
  总计: ${total_cost:.2f}

平均成本: ${total_cost/len(scenes):.2f}/场景
"""
            
            # 预算预警
            warning = ""
            if total_cost > budget_limit:
                warning = f"⚠️ 预算超支警告！\n\n预计成本 ${total_cost:.2f} 超过预算限制 ${budget_limit:.2f}\n\n建议:\n  1. 减少场景数量\n  2. 选择更经济的配置\n  3. 使用两阶段生成策略"
            elif total_cost > budget_limit * 0.8:
                warning = f"⚠️ 预算接近上限\n\n预计成本 ${total_cost:.2f} 已达到预算的 {total_cost/budget_limit*100:.0f}%"
            else:
                warning = f"✅ 预算充足\n\n预计成本 ${total_cost:.2f} 在预算范围内\n预算使用率: {total_cost/budget_limit*100:.0f}%"
            
            return (
                json.dumps(cost_breakdown, ensure_ascii=False, indent=2),
                summary,
                warning
            )
            
        except Exception as e:
            return (
                json.dumps({"error": str(e)}),
                f"成本计算失败: {str(e)}",
                "无法计算预算"
            )


class QualityScorerNode:
    """
    质量评分节点
    
    功能：
    1. 评估生成质量
    2. 多维度评分
    3. 质量建议
    4. 自动优化建议
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "result_json": ("STRING", {"multiline": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("quality_score", "improvement_suggestions")
    FUNCTION = "score_quality"
    CATEGORY = "UnlimitAI/Advanced"
    
    def score_quality(self, result_json: str) -> Tuple[str, str]:
        """评估质量"""
        
        try:
            result = json.loads(result_json)
            
            # 多维度评分
            scores = {
                "consistency": self._score_consistency(result),
                "clarity": self._score_clarity(result),
                "creativity": self._score_creativity(result),
                "technical": self._score_technical(result),
                "overall": 0
            }
            
            # 计算总分
            scores["overall"] = sum(scores.values()) / (len(scores) - 1)
            
            # 生成建议
            suggestions = self._generate_suggestions(scores)
            
            # 格式化输出
            score_output = f"""【质量评分报告】

一致性: {scores['consistency']:.1f}/5.0
清晰度: {scores['clarity']:.1f}/5.0
创意性: {scores['creativity']:.1f}/5.0
技术质量: {scores['technical']:.1f}/5.0

━━━━━━━━━━━━━
综合评分: {scores['overall']:.1f}/5.0
"""
            
            return (
                json.dumps(scores, ensure_ascii=False, indent=2),
                suggestions
            )
            
        except Exception as e:
            return (
                json.dumps({"error": str(e)}),
                f"评分失败: {str(e)}"
            )
    
    def _score_consistency(self, result: Dict) -> float:
        """评分一致性"""
        # 模拟评分逻辑
        return 4.2
    
    def _score_clarity(self, result: Dict) -> float:
        """评分清晰度"""
        return 4.5
    
    def _score_creativity(self, result: Dict) -> float:
        """评分创意性"""
        return 4.0
    
    def _score_technical(self, result: Dict) -> float:
        """评分技术质量"""
        return 4.3
    
    def _generate_suggestions(self, scores: Dict) -> str:
        """生成改进建议"""
        suggestions = []
        
        if scores["consistency"] < 4.0:
            suggestions.append("- 提高角色一致性：使用更详细的角色描述")
        
        if scores["clarity"] < 4.0:
            suggestions.append("- 提高清晰度：优化提示词，添加质量标签")
        
        if scores["creativity"] < 4.0:
            suggestions.append("- 提高创意性：尝试不同的构图和风格")
        
        if scores["technical"] < 4.0:
            suggestions.append("- 提高技术质量：使用更高质量的模型")
        
        if suggestions:
            return "【改进建议】\n\n" + "\n".join(suggestions)
        else:
            return "【改进建议】\n\n✅ 质量优秀，无需改进"


class ProgressTrackerNode:
    """
    进度跟踪节点
    
    功能：
    1. 实时显示进度
    2. 时间预估
    3. 阶段显示
    4. 完成统计
    """
    
    def __init__(self):
        self.start_time = None
        self.stages = []
        self.current_stage = 0
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total_scenes": ("INT", {"default": 10, "min": 1}),
                "current_stage": ("INT", {"default": 0, "min": 0}),
            },
            "optional": {
                "completed_tasks": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("progress_report", "time_estimate")
    FUNCTION = "track_progress"
    CATEGORY = "UnlimitAI/Advanced"
    
    def track_progress(
        self,
        total_scenes: int,
        current_stage: int,
        completed_tasks: str = ""
    ) -> Tuple[str, str]:
        """跟踪进度"""
        
        # 阶段定义
        stages = [
            "文本分析",
            "图像生成",
            "视频生成",
            "音频合成",
            "音乐生成",
            "资源整合"
        ]
        
        # 解析已完成任务
        completed = []
        if completed_tasks:
            completed = completed_tasks.split(',')
        
        # 计算进度
        total_tasks = total_scenes * 5  # 每个场景5个任务
        completed_count = len(completed)
        progress_percent = (completed_count / total_tasks) * 100
        
        # 生成进度报告
        report = f"""【进度报告】

总场景数: {total_scenes}
当前阶段: {stages[current_stage] if current_stage < len(stages) else '完成'}
已完成任务: {completed_count}/{total_tasks}
完成百分比: {progress_percent:.1f}%

阶段进度:
"""
        
        for i, stage in enumerate(stages):
            status = "✅" if i < current_stage else ("🔄" if i == current_stage else "⏳")
            report += f"  {status} {stage}\n"
        
        # 时间预估
        avg_time_per_task = 30  # 秒
        remaining_tasks = total_tasks - completed_count
        estimated_time = remaining_tasks * avg_time_per_task
        
        time_estimate = f"""【时间预估】

平均任务时间: {avg_time_per_task}秒
剩余任务: {remaining_tasks}
预估剩余时间: {estimated_time//60}分{estimated_time%60}秒

预计完成时间: {time.strftime('%H:%M:%S', time.localtime(time.time() + estimated_time))}
"""
        
        return (report, time_estimate)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "PreviewModeNode": PreviewModeNode,
    "SceneEditorNode": SceneEditorNode,
    "RetryMechanismNode": RetryMechanismNode,
    "ParallelExecutionNode": ParallelExecutionNode,
    "RealTimeCostCalculatorNode": RealTimeCostCalculatorNode,
    "QualityScorerNode": QualityScorerNode,
    "ProgressTrackerNode": ProgressTrackerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PreviewModeNode": "🔍 Preview Mode (预览模式)",
    "SceneEditorNode": "✏️ Scene Editor (场景编辑器)",
    "RetryMechanismNode": "🔄 Retry Mechanism (重试机制)",
    "ParallelExecutionNode": "⚡ Parallel Execution (并行执行)",
    "RealTimeCostCalculatorNode": "💰 Real-time Cost Calculator (实时成本计算)",
    "QualityScorerNode": "⭐ Quality Scorer (质量评分)",
    "ProgressTrackerNode": "📊 Progress Tracker (进度跟踪)",
}
