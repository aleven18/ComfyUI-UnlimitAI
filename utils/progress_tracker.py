"""
时间预估和进度显示模块

功能：
1. 预估工作流执行时间
2. 实时进度跟踪
3. 详细时间分解
4. 可视化进度报告

使用方法:
    from utils.progress_tracker import TimeEstimator, ProgressTracker
    
    # 预估时间
    estimate = TimeEstimator.estimate_workflow_time(scenes, config)
    
    # 跟踪进度
    tracker = ProgressTracker(total_tasks=100)
    tracker.update("生成图像", completed=10)
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class TimeBreakdown:
    """时间分解"""
    text: float = 0.0
    image: float = 0.0
    video: float = 0.0
    audio: float = 0.0
    music: float = 0.0
    delay: float = 0.0  # 请求间隔延迟
    
    def total(self) -> float:
        return self.text + self.image + self.video + self.audio + self.music + self.delay
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "text": self.text,
            "image": self.image,
            "video": self.video,
            "audio": self.audio,
            "music": self.music,
            "delay": self.delay,
            "total": self.total()
        }


class TimeEstimator:
    """
    时间预估器
    
    预估工作流执行时间
    
    Examples:
        >>> estimate = TimeEstimator.estimate_workflow_time(
        ...     scenes=scenes,
        ...     config={"image_model": "flux-pro", "video_model": "kling-v2"}
        ... )
        >>> print(estimate["readable"])
        "预计15分30秒"
    """
    
    # 各API的平均响应时间（秒）- 基于实际测试数据
    AVG_RESPONSE_TIMES = {
        "text": {
            "deepseek-chat": 3.0,
            "deepseek-reasoner": 8.0,
            "gpt-4o": 5.0,
            "gpt-4-turbo": 6.0,
            "claude-3-5-sonnet": 5.0,
            "claude-3-opus": 8.0
        },
        "image": {
            "flux-schnell": 5.0,
            "flux-pro": 12.0,
            "flux-dev": 15.0,
            "imagen-4": 18.0,
            "ideogram-v3": 10.0,
            "kling-v2": 20.0,
            "dall-e-3": 12.0
        },
        "video": {
            "vidu2": 50.0,
            "kling-v1": 70.0,
            "kling-v2": 90.0,
            "runway-gen3": 120.0,
            "veo-3": 150.0,
            "veo-3.1": 180.0,
            "hailuo": 60.0
        },
        "audio": {
            "tts-1": 2.0,
            "tts-1-hd": 3.0,
            "minimax-tts": 2.5,
            "speech-01-turbo": 2.0,
            "speech-01-hd": 4.0
        },
        "music": {
            "suno-v3": 25.0,
            "suno-v3-5": 30.0,
            "suno-v4-5": 35.0,
            "suno-v5": 40.0
        }
    }
    
    # 轮询等待时间（异步任务）
    POLLING_TIMES = {
        "image": {
            "kling": 60.0  # Kling图像需要轮询
        },
        "video": {
            "vidu2": 60.0,
            "kling": 90.0,
            "runway": 120.0,
            "veo": 150.0,
            "hailuo": 60.0
        },
        "music": {
            "suno": 30.0
        }
    }
    
    # 平均请求间隔（秒）
    AVG_REQUEST_DELAY = 1.5
    
    @classmethod
    def estimate_workflow_time(
        cls,
        scenes: List[Dict],
        config: Dict[str, str],
        include_delay: bool = True
    ) -> Dict[str, Any]:
        """
        预估工作流时间
        
        Args:
            scenes: 场景列表
            config: 模型配置
            include_delay: 是否包含请求延迟
        
        Returns:
            预估结果字典
        """
        breakdown = TimeBreakdown()
        
        # 统计各类内容数量
        text_count = len(scenes)
        image_count = sum(1 for s in scenes if s.get("visual_prompt"))
        video_count = sum(1 for s in scenes if s.get("generate_video", True) and s.get("visual_prompt"))
        audio_count = sum(1 for s in scenes if s.get("dialogue"))
        music_count = sum(1 for s in scenes if s.get("generate_music", True))
        
        # 计算各类型时间
        breakdown.text = text_count * cls._get_avg_time("text", config.get("text_model", "deepseek-chat"))
        breakdown.image = image_count * cls._get_avg_time("image", config.get("image_model", "flux-pro"))
        breakdown.video = video_count * cls._get_avg_time("video", config.get("video_model", "kling-v2"))
        breakdown.audio = audio_count * cls._get_avg_time("audio", config.get("audio_model", "minimax-tts"))
        breakdown.music = music_count * cls._get_avg_time("music", config.get("music_model", "suno-v3-5"))
        
        # 计算请求延迟
        if include_delay:
            total_requests = image_count + video_count + audio_count + music_count
            breakdown.delay = total_requests * cls.AVG_REQUEST_DELAY
        
        # 总时间
        total_seconds = breakdown.total()
        
        return {
            "breakdown": breakdown.to_dict(),
            "total_seconds": total_seconds,
            "total_minutes": round(total_seconds / 60, 1),
            "readable": cls._format_time(total_seconds),
            "scene_counts": {
                "text": text_count,
                "image": image_count,
                "video": video_count,
                "audio": audio_count,
                "music": music_count
            },
            "config": config
        }
    
    @classmethod
    def estimate_scene_time(
        cls,
        scene: Dict,
        config: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        预估单个场景时间
        
        Args:
            scene: 场景数据
            config: 模型配置
        
        Returns:
            预估结果
        """
        breakdown = TimeBreakdown()
        
        # 文本处理（如果需要）
        if scene.get("needs_text_processing"):
            breakdown.text = cls._get_avg_time("text", config.get("text_model", "deepseek-chat"))
        
        # 图像生成
        if scene.get("visual_prompt"):
            breakdown.image = cls._get_avg_time("image", config.get("image_model", "flux-pro"))
        
        # 视频生成
        if scene.get("generate_video", True) and scene.get("visual_prompt"):
            breakdown.video = cls._get_avg_time("video", config.get("video_model", "kling-v2"))
        
        # 音频生成
        if scene.get("dialogue"):
            breakdown.audio = cls._get_avg_time("audio", config.get("audio_model", "minimax-tts"))
        
        # 音乐生成
        if scene.get("generate_music", True):
            breakdown.music = cls._get_avg_time("music", config.get("music_model", "suno-v3-5"))
        
        # 延迟
        request_count = sum([
            1 if scene.get("visual_prompt") else 0,
            1 if scene.get("generate_video") and scene.get("visual_prompt") else 0,
            1 if scene.get("dialogue") else 0,
            1 if scene.get("generate_music") else 0
        ])
        breakdown.delay = request_count * cls.AVG_REQUEST_DELAY
        
        return {
            "breakdown": breakdown.to_dict(),
            "total_seconds": breakdown.total(),
            "readable": cls._format_time(breakdown.total())
        }
    
    @classmethod
    def _get_avg_time(cls, api_type: str, model: str) -> float:
        """获取平均响应时间"""
        times = cls.AVG_RESPONSE_TIMES.get(api_type, {})
        return times.get(model, 10.0)  # 默认10秒
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            if secs == 0:
                return f"{minutes}分钟"
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}小时{minutes}分钟"


@dataclass
class ProgressState:
    """进度状态"""
    current_stage: str = ""
    current_task: str = ""
    completed_tasks: int = 0
    total_tasks: int = 0
    start_time: float = 0.0
    last_update_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ProgressTracker:
    """
    进度跟踪器
    
    实时跟踪工作流执行进度
    
    Examples:
        >>> tracker = ProgressTracker(total_tasks=100)
        >>> 
        >>> tracker.start("图像生成阶段")
        >>> for i, scene in enumerate(scenes):
        ...     tracker.update(f"生成场景 {i+1}", completed=i)
        ...     generate_image(scene)
        >>> 
        >>> tracker.finish()
        >>> print(tracker.get_summary())
    """
    
    def __init__(self, total_tasks: int, stage_name: str = "工作流"):
        """
        初始化
        
        Args:
            total_tasks: 总任务数
            stage_name: 阶段名称
        """
        self.state = ProgressState(total_tasks=total_tasks)
        self.stage_name = stage_name
        self.history: List[Dict[str, Any]] = []
    
    def start(self, stage: str = ""):
        """开始跟踪"""
        self.state.current_stage = stage or self.stage_name
        self.state.start_time = time.time()
        self.state.last_update_time = self.state.start_time
        self.state.completed_tasks = 0
        
        logger.info(f"开始 {self.state.current_stage}")
        
        self._log_progress("开始")
    
    def update(
        self,
        task: str,
        completed: Optional[int] = None,
        increment: int = 1
    ):
        """
        更新进度
        
        Args:
            task: 当前任务描述
            completed: 已完成任务数（如果提供，直接设置）
            increment: 增量（如果completed未提供）
        """
        self.state.current_task = task
        self.state.last_update_time = time.time()
        
        if completed is not None:
            self.state.completed_tasks = completed
        else:
            self.state.completed_tasks += increment
        
        # 确保不超过总数
        self.state.completed_tasks = min(self.state.completed_tasks, self.state.total_tasks)
        
        self._log_progress("更新")
    
    def add_error(self, error: str):
        """添加错误"""
        self.state.errors.append(error)
        logger.error(f"[{self.state.current_stage}] {error}")
    
    def add_warning(self, warning: str):
        """添加警告"""
        self.state.warnings.append(warning)
        logger.warning(f"[{self.state.current_stage}] {warning}")
    
    def finish(self):
        """完成跟踪"""
        self.state.completed_tasks = self.state.total_tasks
        self._log_progress("完成")
        
        logger.info(f"完成 {self.state.current_stage} - 耗时 {self.get_elapsed_time()}")
    
    def get_progress(self) -> float:
        """获取进度百分比"""
        if self.state.total_tasks == 0:
            return 0.0
        return (self.state.completed_tasks / self.state.total_tasks) * 100
    
    def get_elapsed_time(self) -> str:
        """获取已用时间"""
        if self.state.start_time == 0:
            return "未开始"
        
        elapsed = time.time() - self.state.start_time
        return TimeEstimator._format_time(elapsed)
    
    def get_estimated_remaining(self) -> str:
        """获取预估剩余时间"""
        if self.state.start_time == 0 or self.state.completed_tasks == 0:
            return "计算中..."
        
        elapsed = time.time() - self.state.start_time
        avg_time_per_task = elapsed / self.state.completed_tasks
        remaining_tasks = self.state.total_tasks - self.state.completed_tasks
        remaining_seconds = avg_time_per_task * remaining_tasks
        
        return TimeEstimator._format_time(remaining_seconds)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取摘要"""
        return {
            "stage": self.state.current_stage,
            "current_task": self.state.current_task,
            "progress": f"{self.get_progress():.1f}%",
            "completed": f"{self.state.completed_tasks}/{self.state.total_tasks}",
            "elapsed_time": self.get_elapsed_time(),
            "estimated_remaining": self.get_estimated_remaining(),
            "errors_count": len(self.state.errors),
            "warnings_count": len(self.state.warnings)
        }
    
    def get_report(self) -> str:
        """获取可读报告"""
        summary = self.get_summary()
        
        report = f"""
【{summary['stage']} - 进度报告】
当前任务: {summary['current_task']}
总进度: {summary['progress']} ({summary['completed']})
已用时间: {summary['elapsed_time']}
预估剩余: {summary['estimated_remaining']}
        """.strip()
        
        if summary['errors_count'] > 0:
            report += f"\n错误: {summary['errors_count']}个"
        
        if summary['warnings_count'] > 0:
            report += f"\n警告: {summary['warnings_count']}个"
        
        return report
    
    def _log_progress(self, action: str):
        """记录进度"""
        progress_info = {
            "action": action,
            "stage": self.state.current_stage,
            "task": self.state.current_task,
            "progress": self.get_progress(),
            "completed": self.state.completed_tasks,
            "total": self.state.total_tasks,
            "elapsed": self.get_elapsed_time(),
            "estimated_remaining": self.get_estimated_remaining(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.history.append(progress_info)
        
        # 每10%进度输出一次日志
        if self.state.completed_tasks > 0:
            progress_pct = self.get_progress()
            if int(progress_pct) % 10 == 0 and progress_pct > 0:
                logger.info(self.get_report())


class MultiStageProgressTracker:
    """
    多阶段进度跟踪器
    
    跟踪包含多个阶段的工作流
    """
    
    def __init__(self, stages: List[str]):
        """
        初始化
        
        Args:
            stages: 阶段列表
        """
        self.stages = stages
        self.current_stage_index = 0
        self.stage_trackers: Dict[str, ProgressTracker] = {}
        self.start_time = 0.0
        self.history: List[Dict] = []
    
    def start_workflow(self):
        """开始工作流"""
        self.start_time = time.time()
        logger.info(f"开始工作流，共 {len(self.stages)} 个阶段")
    
    def start_stage(self, stage_name: str, total_tasks: int):
        """开始阶段"""
        tracker = ProgressTracker(total_tasks=total_tasks, stage_name=stage_name)
        tracker.start(stage_name)
        self.stage_trackers[stage_name] = tracker
    
    def update_stage(self, stage_name: str, task: str, completed: Optional[int] = None):
        """更新阶段进度"""
        if stage_name in self.stage_trackers:
            self.stage_trackers[stage_name].update(task, completed)
    
    def finish_stage(self, stage_name: str):
        """完成阶段"""
        if stage_name in self.stage_trackers:
            self.stage_trackers[stage_name].finish()
            self.current_stage_index += 1
    
    def get_overall_progress(self) -> float:
        """获取总体进度"""
        if not self.stage_trackers:
            return 0.0
        
        total_progress = sum(
            tracker.get_progress()
            for tracker in self.stage_trackers.values()
        )
        
        return total_progress / len(self.stages)
    
    def get_overall_summary(self) -> Dict[str, Any]:
        """获取总体摘要"""
        stage_summaries = {
            name: tracker.get_summary()
            for name, tracker in self.stage_trackers.items()
        }
        
        elapsed = time.time() - self.start_time if self.start_time > 0 else 0
        
        return {
            "total_stages": len(self.stages),
            "completed_stages": self.current_stage_index,
            "current_stage": self.stages[self.current_stage_index] if self.current_stage_index < len(self.stages) else "完成",
            "overall_progress": f"{self.get_overall_progress():.1f}%",
            "elapsed_time": TimeEstimator._format_time(elapsed),
            "stage_summaries": stage_summaries
        }
    
    def get_overall_report(self) -> str:
        """获取总体报告"""
        summary = self.get_overall_summary()
        
        report = f"""
【工作流总体报告】
总阶段数: {summary['total_stages']}
已完成: {summary['completed_stages']}
当前阶段: {summary['current_stage']}
总体进度: {summary['overall_progress']}
已用时间: {summary['elapsed_time']}
        """.strip()
        
        # 添加各阶段进度
        for stage_name, stage_summary in summary['stage_summaries'].items():
            report += f"\n  - {stage_name}: {stage_summary['progress']}"
        
        return report


# 便捷函数
def estimate_time(scenes: List[Dict], config: Dict[str, str]) -> str:
    """快速预估时间（返回可读字符串）"""
    result = TimeEstimator.estimate_workflow_time(scenes, config)
    return result["readable"]
