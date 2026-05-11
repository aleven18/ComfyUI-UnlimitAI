"""
Novel to Drama workflow nodes for ComfyUI-UnlimitAI.
Specialized nodes for converting Chinese novels to English drama videos.

Optimized with:
- Smart delay (replaces hardcoded time.sleep)
- Smart skip (skip unnecessary API calls)
- Content deduplication
- Progress tracking
- Robust error handling
"""
import logging
logger = logging.getLogger(__name__)

import json
import time
from typing import Dict, Any, Tuple, Optional
from ..utils.helpers import make_request, poll_status
from ..utils.json_utils import parse_json_safe
from ..utils.smart_skip import SmartSkipper
from ..utils.content_dedup import ContentDeduplicator
from ..utils.progress_tracker import ProgressTracker
from ..utils.delay import SmartDelay


class WorkflowContext:
    """Per-instance context holding all optimization components.
    
    Avoids module-level singletons so concurrent workflows don't share state.
    Each node instance creates its own context on first access.
    """
    
    def __init__(
        self,
        enable_smart_skip: bool = True,
        enable_dedup: bool = True,
        enable_progress: bool = True,
        base_delay: float = 1.0,
    ):
        self.enable_smart_skip = enable_smart_skip
        self.enable_dedup = enable_dedup
        self.enable_progress = enable_progress
        
        self.smart_skip = SmartSkipper() if enable_smart_skip else None
        self.content_dedup = ContentDeduplicator() if enable_dedup else None
        self.smart_delay = SmartDelay(initial_delay=base_delay)
        self.progress_trackers: Dict[str, ProgressTracker] = {}
    
    def should_skip_generation(self, task_type: str, scene: Dict[str, Any]) -> Optional[str]:
        if not self.smart_skip:
            return None
        
        should_gen = True
        reason = ""
        
        if task_type == "image":
            should_gen, reason = self.smart_skip.should_generate_image(scene)
        elif task_type == "video":
            should_gen, reason = self.smart_skip.should_generate_video(scene)
        elif task_type == "audio":
            should_gen, reason = self.smart_skip.should_generate_audio(scene)
        elif task_type == "music":
            should_gen, reason = self.smart_skip.should_generate_music(scene)
        
        if not should_gen:
            logger.info("Smart skip: %s", reason)
            return reason
        return None
    
    def check_content_duplicate(self, task_type: str, content_key: str) -> Optional[str]:
        if not self.content_dedup:
            return None
        
        try:
            cached = self.content_dedup.check_exists(content_key, content_type=task_type)
            if cached:
                url = cached.get(f"{task_type}_url") or cached.get("url") or cached.get("image_url") or cached.get("video_url")
                if url:
                    logger.info("Found duplicate content for %s", task_type)
                    return url
        except Exception as e:
            logger.debug("Dedup check failed: %s", e)
        
        return None
    
    def store_content_duplicate(self, task_type: str, content_key: str, url: str):
        if not self.content_dedup or not url:
            return
        
        try:
            self.content_dedup.store(content_key, result={f"{task_type}_url": url}, content_type=task_type)
        except Exception as e:
            logger.debug("Dedup store failed: %s", e)
    
    def apply_smart_delay(self, task_type: str = "default", is_last: bool = False):
        if is_last:
            return
        
        self.smart_delay.wait(operation=task_type)
    
    def record_result(self, success: bool, is_rate_limit: bool = False):
        if success:
            self.smart_delay.on_success()
        elif is_rate_limit:
            self.smart_delay.on_failure(is_rate_limit=True)
        else:
            self.smart_delay.on_failure()
    
    def start_progress(self, batch_key: str, total: int, label: str):
        if not self.enable_progress:
            return
        tracker = ProgressTracker(total_tasks=total, stage_name=label)
        tracker.start(f"{label} generation")
        self.progress_trackers[batch_key] = tracker
    
    def update_progress(self, batch_key: str, task_name: str, completed: int):
        tracker = self.progress_trackers.get(batch_key)
        if tracker:
            tracker.update(task_name, completed=completed)
    
    def finish_progress(self, batch_key: str):
        tracker = self.progress_trackers.get(batch_key)
        if tracker:
            tracker.finish()
            del self.progress_trackers[batch_key]



class NovelToDramaWorkflowNode:
    """
    Complete workflow: Chinese novel -> English drama scenes with audio.
    """
    
    def __init__(self):
        self.ctx = WorkflowContext()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "novel_text": ("STRING", {"default": "", "multiline": True}),
                "num_scenes": ("INT", {"default": 10, "min": 1, "max": 50}),
            },
            "optional": {
                "text_model": (["deepseek-chat", "gpt-4o", "claude-3-5-sonnet-20241022"], {"default": "deepseek-chat"}),
                "target_language": (["english", "chinese"], {"default": "english"}),
                "art_style": (["cinematic", "anime", "realistic", "artistic"], {"default": "cinematic"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("scenes_json", "summary", "total_cost")
    FUNCTION = "process"
    CATEGORY = "UnlimitAI/Workflow/Drama"
    
    def process(
        self,
        api_key: str,
        novel_text: str,
        num_scenes: int,
        text_model: str = "deepseek-chat",
        target_language: str = "english",
        art_style: str = "cinematic"
    ) -> Tuple[str, str, str]:
        lang_instruction = "使用中文" if target_language == "chinese" else "Use English"
        
        prompt = f"""{lang_instruction}分析以下小说文本，提取{num_scenes}个关键场景用于制作漫剧视频。

对于每个场景，提供：
1. scene_number: 场景编号
2. title: 场景标题
3. description: 场景描述（人物、动作、环境）
4. characters: 出场人物列表
5. mood: 场景氛围（emotional/suspenseful/romantic/action/peaceful/dramatic/melancholic/upbeat/tense）
6. dialogue: 关键对话或独白（用于配音，包含情感标签如 (laughs), (sighs)）
7. visual_prompt: 用于生成图像的详细英文提示词，{art_style} style
8. camera_movement: 镜头运动建议

小说文本：
{novel_text}"""
        
        schema = {
            "type": "object",
            "properties": {
                "scenes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "scene_number": {"type": "integer"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "characters": {"type": "array", "items": {"type": "string"}},
                            "mood": {"type": "string"},
                            "dialogue": {"type": "string"},
                            "visual_prompt": {"type": "string"},
                            "camera_movement": {"type": "string"}
                        }
                    }
                },
                "summary": {"type": "string"}
            }
        }
        
        payload = {
            "model": text_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "novel_scenes",
                    "schema": schema
                }
            }
        }
        
        response = make_request("/v1/chat/completions", api_key, payload)
        
        choices = response.get("choices", [])
        if not choices:
            return ("", "No response from API", "$0.00")
        
        text = choices[0].get("message", {}).get("content", "")
        if not text:
            return ("", "Empty response from API", "$0.00")
        
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return (text, "Failed to parse scene JSON", "$0.00")
        
        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        pricing = {
            "deepseek-chat": {"input": 0.00014, "output": 0.00028},
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015}
        }
        
        rates = pricing.get(text_model, pricing["deepseek-chat"])
        cost = (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])
        
        summary = data.get("summary", "")
        
        return (text, summary, f"${cost:.6f}")


class SceneImageGeneratorNode:
    """
    Generate images for all scenes in batch.
    """
    
    def __init__(self):
        self.ctx = WorkflowContext()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "scenes_json": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "image_model": (["flux-pro", "ideogram-v3", "kling-v2", "dall-e-3"], {"default": "flux-pro"}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
                "max_scenes": ("INT", {"default": 10, "min": 1, "max": 50}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("images_json", "summary")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Workflow/Drama"
    
    def generate(
        self,
        api_key: str,
        scenes_json: str,
        image_model: str = "flux-pro",
        aspect_ratio: str = "16:9",
        max_scenes: int = 10
    ) -> Tuple[str, str]:
        scenes_data = parse_json_safe(scenes_json, "scenes_json")
        scenes = scenes_data.get("scenes", [])[:max_scenes]
        
        if not scenes:
            return (json.dumps({"images": []}), "No scenes to process")
        
        results = []
        total = len(scenes)
        
        self.ctx.start_progress("image_batch", total, "image")
        
        for idx, scene in enumerate(scenes):
            scene_number = scene.get("scene_number", 0)
            prompt = scene.get("visual_prompt", "")
            is_last = (idx == total - 1)
            
            if not prompt:
                results.append({
                    "scene_number": scene_number,
                    "image_url": "",
                    "status": "skipped",
                    "reason": "no_prompt"
                })
                continue
            
            skip_scene = {
                "scene_number": scene_number,
                "visual_prompt": prompt,
                "image_url": scene.get("image_url", ""),
                "scene_type": scene.get("scene_type", ""),
                "skip_image": scene.get("skip_image", False),
            }
            skip_reason = self.ctx.should_skip_generation("image", skip_scene)
            if skip_reason:
                results.append({
                    "scene_number": scene_number,
                    "image_url": "",
                    "status": "skipped",
                    "reason": skip_reason
                })
                continue
            
            content_key = f"image:{prompt}:{image_model}:{aspect_ratio}"
            cached_url = self.ctx.check_content_duplicate("image", content_key)
            if cached_url:
                results.append({
                    "scene_number": scene_number,
                    "image_url": cached_url,
                    "status": "success",
                    "reason": "deduplicated"
                })
                continue
            
            payload = {
                "prompt": prompt,
                "num_images": 1,
                "enable_safety_checker": True,
                "output_format": "jpeg",
                "sync": True
            }
            
            try:
                if image_model == "flux-pro":
                    endpoint = "/fal-ai/flux-pro"
                    payload["image_size"] = "landscape_16_9" if aspect_ratio == "16:9" else "portrait_9_16" if aspect_ratio == "9:16" else "square"
                elif image_model == "ideogram-v3":
                    endpoint = "/v1/ideogram/generate"
                    payload["aspect_ratio"] = aspect_ratio
                    payload["model"] = "V_3"
                elif image_model == "kling-v2":
                    endpoint = "/v1/images/kling"
                    payload["model"] = "kling-v2"
                    payload["aspect_ratio"] = aspect_ratio
                else:
                    endpoint = "/v1/images/generations"
                    payload["model"] = "dall-e-3"
                    payload["size"] = "1792x1024" if aspect_ratio == "16:9" else "1024x1792" if aspect_ratio == "9:16" else "1024x1024"
                
                response = make_request(endpoint, api_key, payload)
                
                if image_model == "flux-pro":
                    image_url = response.get("images", [{}])[0].get("url", "")
                elif image_model in ["ideogram-v3", "dall-e-3"]:
                    image_url = response.get("data", [{}])[0].get("url", "")
                else:
                    task_id_resp = response.get("data", {})
                    if isinstance(task_id_resp, dict):
                        task_id_val = task_id_resp.get("task_id", "")
                    else:
                        task_id_val = ""
                    if task_id_val:
                        status_url = f"https://api.unlimitai.org/v1/images/kling/{task_id_val}"
                        result = poll_status(status_url, api_key, interval=3, max_attempts=60, success_status="succeed")
                        image_url = result.get("data", {}).get("task_result", {}).get("images", [{}])[0].get("url", "")
                    else:
                        image_url = ""
                
                results.append({
                    "scene_number": scene_number,
                    "image_url": image_url,
                    "status": "success"
                })
                
                self.ctx.store_content_duplicate("image", content_key, image_url)
                self.ctx.record_result(True)
                self.ctx.apply_smart_delay("image", is_last=is_last)
                
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = "rate" in error_str or "limit" in error_str or "429" in error_str
                self.ctx.record_result(False, is_rate_limit)
                
                results.append({
                    "scene_number": scene_number,
                    "image_url": "",
                    "status": f"error: {str(e)}"
                })
            
            self.ctx.update_progress("image_batch", f"Scene {scene_number}", completed=idx + 1)
        
        self.ctx.finish_progress("image_batch")
        
        output = {"images": results}
        output_json = json.dumps(output, ensure_ascii=False, indent=2)
        
        successful = sum(1 for r in results if r["status"] == "success" and r.get("reason") != "deduplicated")
        deduplicated = sum(1 for r in results if r.get("reason") == "deduplicated")
        skipped = sum(1 for r in results if "skipped" in r["status"])
        summary = f"Generated {successful}/{len(results)} images (dedup: {deduplicated}, skipped: {skipped})"
        
        return (output_json, summary)


class SceneVideoGeneratorNode:
    """
    Generate videos for all scenes in batch.
    """
    
    def __init__(self):
        self.ctx = WorkflowContext()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "images_json": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "video_model": (["veo-3.1", "kling-v2", "vidu2", "hailuo"], {"default": "kling-v2"}),
                "duration": (["5", "10"], {"default": "5"}),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("videos_json", "summary")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Workflow/Drama"
    
    def generate(
        self,
        api_key: str,
        images_json: str,
        video_model: str = "kling-v2",
        duration: str = "5",
        aspect_ratio: str = "16:9"
    ) -> Tuple[str, str]:
        images_data = parse_json_safe(images_json, "images_json")
        images = images_data.get("images", [])
        
        if not images:
            return (json.dumps({"videos": []}), "No images to process")
        
        results = []
        total = len(images)
        
        self.ctx.start_progress("video_batch", total, "video")
        
        for idx, img in enumerate(images):
            scene_number = img.get("scene_number", 0)
            image_url = img.get("image_url", "")
            is_last = (idx == total - 1)
            
            if not image_url:
                results.append({
                    "scene_number": scene_number,
                    "video_url": "",
                    "status": "skipped",
                    "reason": "no_image"
                })
                continue
            
            skip_scene = {
                "scene_number": scene_number,
                "image_url": image_url,
                "video_url": img.get("video_url", ""),
                "scene_type": img.get("scene_type", ""),
                "skip_video": img.get("skip_video", False),
            }
            skip_reason = self.ctx.should_skip_generation("video", skip_scene)
            if skip_reason:
                results.append({
                    "scene_number": scene_number,
                    "video_url": "",
                    "status": "skipped",
                    "reason": skip_reason
                })
                continue
            
            content_key = f"video:{image_url}:{video_model}:{duration}"
            cached_url = self.ctx.check_content_duplicate("video", content_key)
            if cached_url:
                results.append({
                    "scene_number": scene_number,
                    "video_url": cached_url,
                    "status": "success",
                    "reason": "deduplicated"
                })
                continue
            
            payload = {
                "prompt": "Animate this scene with natural movement and atmosphere",
                "image": image_url,
                "duration": duration,
                "aspect_ratio": aspect_ratio
            }
            
            try:
                if video_model == "kling-v2":
                    endpoint = "/v1/videos/kling/image-to-video"
                    payload["model"] = "kling-v2"
                    payload["cfg_scale"] = 0.5
                    success_status = "succeed"
                elif video_model == "vidu2":
                    endpoint = "/v1/videos/vidu/image-to-video"
                    payload["model"] = "vidu2"
                    payload["duration"] = int(duration)
                    success_status = "success"
                elif video_model == "hailuo":
                    endpoint = "/v1/video/generation"
                    payload["model"] = "T2V-01-Director"
                    payload["first_frame_image"] = image_url
                    del payload["image"]
                    del payload["duration"]
                    del payload["aspect_ratio"]
                    success_status = "success"
                else:
                    endpoint = f"/veo/{video_model}/generate"
                    payload["aspectRatio"] = aspect_ratio
                    del payload["aspect_ratio"]
                    del payload["duration"]
                    success_status = "COMPLETED"
                
                response = make_request(endpoint, api_key, payload)
                
                task_data = response.get("data", {})
                if isinstance(task_data, dict):
                    task_id = task_data.get("task_id", "") or response.get("request_id", "")
                else:
                    task_id = response.get("request_id", "")
                
                if task_id:
                    if video_model == "kling-v2":
                        status_url = f"https://api.unlimitai.org/v1/videos/kling/{task_id}"
                    elif video_model == "vidu2":
                        status_url = f"https://api.unlimitai.org/v1/videos/vidu/{task_id}"
                    elif video_model == "hailuo":
                        status_url = f"https://api.unlimitai.org/v1/video/generation/{task_id}"
                    else:
                        status_url = response.get("status_url", "")
                    
                    result = poll_status(status_url, api_key, interval=10, max_attempts=120, success_status=success_status)
                    
                    if video_model == "kling-v2":
                        video_url = result.get("data", {}).get("task_result", {}).get("videos", [{}])[0].get("url", "")
                    elif video_model == "vidu2":
                        video_url = result.get("data", {}).get("video_url", "")
                    elif video_model == "hailuo":
                        video_url = result.get("video_url", "")
                    else:
                        video_url = result.get("video", {}).get("url", "")
                else:
                    video_url = ""
                
                results.append({
                    "scene_number": scene_number,
                    "video_url": video_url,
                    "status": "success"
                })
                
                self.ctx.store_content_duplicate("video", content_key, video_url)
                self.ctx.record_result(True)
                self.ctx.apply_smart_delay("video", is_last=is_last)
                
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = "rate" in error_str or "limit" in error_str or "429" in error_str
                self.ctx.record_result(False, is_rate_limit)
                
                results.append({
                    "scene_number": scene_number,
                    "video_url": "",
                    "status": f"error: {str(e)}"
                })
            
            self.ctx.update_progress("video_batch", f"Scene {scene_number}", completed=idx + 1)
        
        self.ctx.finish_progress("video_batch")
        
        output = {"videos": results}
        output_json = json.dumps(output, ensure_ascii=False, indent=2)
        
        successful = sum(1 for r in results if r["status"] == "success" and r.get("reason") != "deduplicated")
        deduplicated = sum(1 for r in results if r.get("reason") == "deduplicated")
        skipped = sum(1 for r in results if "skipped" in r["status"])
        summary = f"Generated {successful}/{len(results)} videos (dedup: {deduplicated}, skipped: {skipped})"
        
        return (output_json, summary)


class SceneAudioGeneratorNode:
    """
    Generate audio (dialogue + music) for all scenes.
    """
    
    def __init__(self):
        self.ctx = WorkflowContext()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "scenes_json": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "voice_id": ("STRING", {"default": "male-qn-jingying", "multiline": False}),
                "generate_music": ("BOOLEAN", {"default": True}),
                "max_scenes": ("INT", {"default": 10, "min": 1, "max": 50}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("audio_json", "summary")
    FUNCTION = "generate"
    CATEGORY = "UnlimitAI/Workflow/Drama"
    
    def generate(
        self,
        api_key: str,
        scenes_json: str,
        voice_id: str = "male-qn-jingying",
        generate_music: bool = True,
        max_scenes: int = 10
    ) -> Tuple[str, str]:
        scenes_data = parse_json_safe(scenes_json, "scenes_json")
        scenes = scenes_data.get("scenes", [])[:max_scenes]
        
        if not scenes:
            return (json.dumps({"audio": []}), "No scenes to process")
        
        results = []
        total = len(scenes)
        
        self.ctx.start_progress("audio_batch", total, "audio")
        
        mood_prompts = {
            "emotional": "emotional piano, touching",
            "suspenseful": "suspenseful thriller, mysterious",
            "romantic": "romantic love theme, soft",
            "action": "action movie, energetic",
            "peaceful": "peaceful ambient, calm",
            "dramatic": "dramatic orchestral, cinematic",
            "melancholic": "melancholic sad, touching",
            "upbeat": "upbeat energetic, positive",
            "tense": "tense dramatic, building"
        }
        
        for idx, scene in enumerate(scenes):
            scene_number = scene.get("scene_number", 0)
            dialogue = scene.get("dialogue", "")
            mood = scene.get("mood", "emotional")
            is_last = (idx == total - 1)
            
            result = {
                "scene_number": scene_number,
                "dialogue_url": "",
                "music_url": "",
                "status": "pending"
            }
            
            dialogue_outcome = None
            music_outcome = None
            
            if dialogue:
                skip_scene = {
                    "scene_number": scene_number,
                    "dialogue": dialogue,
                    "audio_url": scene.get("audio_url", ""),
                    "scene_type": scene.get("scene_type", ""),
                    "skip_audio": scene.get("skip_audio", False),
                }
                skip_reason = self.ctx.should_skip_generation("audio", skip_scene)
                if skip_reason:
                    dialogue_outcome = "skipped"
                else:
                    content_key = f"audio:{dialogue}:{voice_id}"
                    cached_url = self.ctx.check_content_duplicate("audio", content_key)
                    if cached_url:
                        result["dialogue_url"] = cached_url
                        dialogue_outcome = "dedup"
                    else:
                        try:
                            payload = {
                                "model": "speech-01-turbo",
                                "input": dialogue,
                                "voice": voice_id,
                                "audio_setting": {
                                    "sample_rate": 32000,
                                    "format": "mp3"
                                }
                            }
                            
                            response = make_request("/v1/audio/speech", api_key, payload)
                            result["dialogue_url"] = response.get("audio_url", "")
                            
                            self.ctx.store_content_duplicate("audio", content_key, result["dialogue_url"])
                            self.ctx.record_result(True)
                            self.ctx.apply_smart_delay("audio", is_last=is_last and not generate_music)
                            dialogue_outcome = "generated"
                        except Exception as e:
                            error_str = str(e).lower()
                            is_rate_limit = "rate" in error_str or "limit" in error_str or "429" in error_str
                            self.ctx.record_result(False, is_rate_limit)
                            dialogue_outcome = "error"
            
            if generate_music:
                prompt = mood_prompts.get(mood, mood_prompts["emotional"])
                
                skip_scene = {
                    "scene_number": scene_number,
                    "mood": mood,
                    "music_url": scene.get("music_url", ""),
                    "scene_type": scene.get("scene_type", ""),
                    "use_stock_music": scene.get("use_stock_music", False),
                    "skip_music": scene.get("skip_music", False),
                }
                skip_reason = self.ctx.should_skip_generation("music", skip_scene)
                if skip_reason:
                    music_outcome = "skipped"
                else:
                    content_key = f"music:{prompt}:{mood}"
                    cached_url = self.ctx.check_content_duplicate("music", content_key)
                    if cached_url:
                        result["music_url"] = cached_url
                        music_outcome = "dedup"
                    else:
                        try:
                            payload = {
                                "prompt": prompt + ", instrumental background music",
                                "mv": "chirp-v3-5",
                                "make_instrumental": True
                            }
                            
                            response = make_request("/suno/v3/generate", api_key, payload)
                            suno_data = response.get("data", {})
                            if isinstance(suno_data, dict):
                                task_id = suno_data.get("task_id", "")
                            else:
                                task_id = ""
                            
                            if task_id:
                                status_url = f"https://api.unlimitai.org/suno/v3/generate/{task_id}"
                                music_result = poll_status(status_url, api_key, interval=10, max_attempts=60, success_status="complete")
                                result["music_url"] = music_result.get("data", [{}])[0].get("audio_url", "")
                            
                            self.ctx.store_content_duplicate("music", content_key, result["music_url"])
                            self.ctx.record_result(True)
                            self.ctx.apply_smart_delay("music", is_last=is_last)
                            music_outcome = "generated"
                        except Exception as e:
                            error_str = str(e).lower()
                            is_rate_limit = "rate" in error_str or "limit" in error_str or "429" in error_str
                            self.ctx.record_result(False, is_rate_limit)
                            music_outcome = "error"
            
            has_dialogue = bool(result["dialogue_url"])
            has_music = bool(result["music_url"])
            dialogue_errored = dialogue_outcome == "error"
            music_errored = music_outcome == "error"
            
            if has_dialogue or has_music:
                if dialogue_errored or music_errored:
                    result["status"] = "partial_success"
                else:
                    result["status"] = "success"
            elif dialogue_errored or music_errored:
                result["status"] = "error"
            else:
                result["status"] = "skipped"
            
            results.append(result)
            
            self.ctx.update_progress("audio_batch", f"Scene {scene_number}", completed=idx + 1)
        
        self.ctx.finish_progress("audio_batch")
        
        output = {"audio": results}
        output_json = json.dumps(output, ensure_ascii=False, indent=2)
        
        successful = sum(1 for r in results if r["status"] in ("success", "partial_success"))
        skipped = sum(1 for r in results if r["status"] == "skipped")
        errors = sum(1 for r in results if r["status"] == "error")
        summary = f"Generated audio for {successful}/{len(results)} scenes (skipped: {skipped}, errors: {errors})"
        
        return (output_json, summary)


class DramaManifestNode:
    """
    Create final manifest JSON combining all assets.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scenes_json": ("STRING", {"default": "", "multiline": True}),
                "images_json": ("STRING", {"default": "", "multiline": True}),
                "videos_json": ("STRING", {"default": "", "multiline": True}),
                "audio_json": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "title": ("STRING", {"default": "Drama Video", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("manifest_json", "summary")
    FUNCTION = "create_manifest"
    CATEGORY = "UnlimitAI/Workflow/Drama"
    
    def create_manifest(
        self,
        scenes_json: str,
        images_json: str,
        videos_json: str,
        audio_json: str,
        title: str = "Drama Video"
    ) -> Tuple[str, str]:
        scenes = parse_json_safe(scenes_json, "scenes_json").get("scenes", [])
        images = parse_json_safe(images_json, "images_json").get("images", [])
        videos = parse_json_safe(videos_json, "videos_json").get("videos", [])
        audio = parse_json_safe(audio_json, "audio_json").get("audio", [])
        
        image_dict = {img["scene_number"]: img for img in images if isinstance(img, dict) and "scene_number" in img}
        video_dict = {vid["scene_number"]: vid for vid in videos if isinstance(vid, dict) and "scene_number" in vid}
        audio_dict = {aud["scene_number"]: aud for aud in audio if isinstance(aud, dict) and "scene_number" in aud}
        
        manifest = {
            "title": title,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_scenes": len(scenes),
            "scenes": []
        }
        
        for scene in scenes:
            scene_num = scene.get("scene_number", 0)
            
            manifest["scenes"].append({
                "scene_number": scene_num,
                "title": scene.get("title", ""),
                "description": scene.get("description", ""),
                "characters": scene.get("characters", []),
                "mood": scene.get("mood", ""),
                "dialogue": scene.get("dialogue", ""),
                "visual_prompt": scene.get("visual_prompt", ""),
                "camera_movement": scene.get("camera_movement", ""),
                "image_url": image_dict.get(scene_num, {}).get("image_url", ""),
                "video_url": video_dict.get(scene_num, {}).get("video_url", ""),
                "dialogue_url": audio_dict.get(scene_num, {}).get("dialogue_url", ""),
                "music_url": audio_dict.get(scene_num, {}).get("music_url", "")
            })
        
        manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)
        
        summary = f"Manifest created: {len(scenes)} scenes with complete assets"
        
        return (manifest_json, summary)


NODE_CLASS_MAPPINGS = {
    "NovelToDramaWorkflowNode": NovelToDramaWorkflowNode,
    "SceneImageGeneratorNode": SceneImageGeneratorNode,
    "SceneVideoGeneratorNode": SceneVideoGeneratorNode,
    "SceneAudioGeneratorNode": SceneAudioGeneratorNode,
    "DramaManifestNode": DramaManifestNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NovelToDramaWorkflowNode": "Novel to Drama Workflow",
    "SceneImageGeneratorNode": "Scene Image Generator (Batch)",
    "SceneVideoGeneratorNode": "Scene Video Generator (Batch)",
    "SceneAudioGeneratorNode": "Scene Audio Generator (Batch)",
    "DramaManifestNode": "Drama Manifest Creator",
}
