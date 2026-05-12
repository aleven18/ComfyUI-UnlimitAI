"""
统一API客户端模块

提供所有UnlimitAI API的统一调用接口
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path


from .exceptions import APIError


class UnlimitAIClient:
    """UnlimitAI API 客户端"""
    
    BASE_URL = "https://api.unlimitai.org"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = 30
        self.max_retries = 3
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict:
        """发起API请求"""
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
            elif method == "POST":
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            # 检查响应状态
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # 速率限制，等待后重试
                if retry_count < self.max_retries:
                    time.sleep(2 ** retry_count)
                    return self._make_request(method, endpoint, payload, retry_count + 1)
                else:
                    raise APIError(f"请求频率超限: {response.text}")
            else:
                raise APIError(f"API错误 ({response.status_code}): {response.text}")
                
        except requests.exceptions.Timeout:
            if retry_count < self.max_retries:
                time.sleep(2 ** retry_count)
                return self._make_request(method, endpoint, payload, retry_count + 1)
            else:
                raise APIError("请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise APIError("网络连接失败，请检查网络或API Key")
        except json.JSONDecodeError:
            raise APIError("响应格式错误，请联系技术支持")
    
    # ==================== 文本生成 ====================
    
    def generate_text(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict:
        """生成文本"""
        endpoint = "/v1/chat/completions"
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        return self._make_request("POST", endpoint, payload)
    
    # ==================== 图像生成 ====================
    
    def generate_image_flux(
        self,
        prompt: str,
        model: str = "flux-pro",
        aspect_ratio: str = "16:9",
        **kwargs
    ) -> Dict:
        """使用FLUX生成图像"""
        endpoint = "/api/v1/flux/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            **kwargs
        }
        
        return self._make_request("POST", endpoint, payload)
    
    def generate_image_imagen(
        self,
        prompt: str,
        model: str = "imagen-4.0-generate-preview-05-20",
        aspect_ratio: str = "16:9",
        **kwargs
    ) -> Dict:
        """使用Imagen生成图像"""
        endpoint = "/api/v1/imagen/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            **kwargs
        }
        
        return self._make_request("POST", endpoint, payload)
    
    # ==================== 视频生成 ====================
    
    def generate_video_kling(
        self,
        image_url: str,
        prompt: str,
        model: str = "kling-v2",
        duration: str = "10s",
        **kwargs
    ) -> Dict:
        """使用Kling生成视频"""
        endpoint = f"/v1/videos/{model}/image-to-video"
        
        payload = {
            "image": image_url,
            "prompt": prompt,
            "duration": duration,
            **kwargs
        }
        
        return self._make_request("POST", endpoint, payload)
    
    def generate_video_vidu(
        self,
        image_url: str,
        prompt: str,
        duration: int = 4,
        **kwargs
    ) -> Dict:
        """使用VIDU生成视频"""
        endpoint = "/v1/videos/vidu/image-to-video"
        
        payload = {
            "image": image_url,
            "prompt": prompt,
            "duration": duration,
            **kwargs
        }
        
        return self._make_request("POST", endpoint, payload)
    
    # ==================== 音频生成 ====================
    
    def generate_audio_minimax(
        self,
        text: str,
        voice: str = "female-shaonv",
        model: str = "speech-02-turbo",
        **kwargs
    ) -> Dict:
        """使用Minimax生成音频"""
        endpoint = "/v1/audio/speech"
        
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            **kwargs
        }
        
        return self._make_request("POST", endpoint, payload)
    
    def generate_audio_openai(
        self,
        text: str,
        voice: str = "nova",
        model: str = "tts-1",
        **kwargs
    ) -> Dict:
        """使用OpenAI生成音频"""
        endpoint = "/v1/audio/speech"
        
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            **kwargs
        }
        
        return self._make_request("POST", endpoint, payload)
    
    # ==================== 音乐生成 ====================
    
    def generate_music_suno(
        self,
        prompt: str,
        mode: str = "custom",
        **kwargs
    ) -> Dict:
        """使用Suno生成音乐"""
        if mode == "custom":
            endpoint = "/api/v1/suno/custom"
        else:
            endpoint = "/api/v1/suno/inspiration"
        
        payload = {
            "prompt": prompt,
            **kwargs
        }
        
        return self._make_request("POST", endpoint, payload)
    
    # ==================== 批量操作 ====================
    
    def batch_generate_images(
        self,
        requests_data: List[Dict],
        delay: float = 1.0
    ) -> List[Dict]:
        """批量生成图像"""
        results = []
        
        for i, req in enumerate(requests_data):
            try:
                result = self.generate_image_flux(**req)
                results.append({
                    "index": i,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "status": "failed",
                    "error": str(e)
                })
            
            # 避免速率限制
            if i < len(requests_data) - 1:
                time.sleep(delay)
        
        return results


class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        if not url:
            return False
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """验证API Key格式"""
        if not api_key:
            return False
        return len(api_key) >= 20
    
    @staticmethod
    def validate_prompt(prompt: str, max_length: int = 2000) -> bool:
        """验证提示词"""
        if not prompt:
            return False
        if len(prompt) > max_length:
            return False
        return True
    
    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """清理提示词"""
        # 移除可能导致问题的字符
        dangerous_chars = ['<', '>', '{', '}', '|', '\\']
        for char in dangerous_chars:
            prompt = prompt.replace(char, '')
        return prompt.strip()
    
    @staticmethod
    def validate_positive_int(value: int, min_val: int = 1, max_val: int = 100) -> bool:
        """验证正整数"""
        try:
            val = int(value)
            return min_val <= val <= max_val
        except (ValueError, TypeError):
            return False


class ErrorHandler:
    """统一错误处理"""
    
    @staticmethod
    def format_error(error: Exception, context: str = "") -> tuple:
        """格式化错误输出"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # 生成用户友好的错误消息
        user_msg = f"❌ 错误: {error_msg}\n\n"
        
        if "JSONDecodeError" in error_type:
            user_msg += "💡 提示: JSON格式错误，请检查输入数据格式\n"
            user_msg += "   - 确保所有引号配对\n"
            user_msg += "   - 确保没有多余的逗号"
        elif "ConnectionError" in error_type or "连接" in error_msg:
            user_msg += "💡 提示: 网络连接失败\n"
            user_msg += "   - 检查网络连接\n"
            user_msg += "   - 确认API Key正确\n"
            user_msg += "   - 检查防火墙设置"
        elif "timeout" in error_msg.lower() or "超时" in error_msg:
            user_msg += "💡 提示: 请求超时\n"
            user_msg += "   - 检查网络速度\n"
            user_msg += "   - 稍后重试"
        elif "401" in error_msg or "403" in error_msg:
            user_msg += "💡 提示: 认证失败\n"
            user_msg += "   - 检查API Key是否正确\n"
            user_msg += "   - 确认账户余额充足"
        elif "429" in error_msg:
            user_msg += "💡 提示: 请求频率超限\n"
            user_msg += "   - 等待几分钟后重试\n"
            user_msg += "   - 减少并发请求数"
        else:
            if context:
                user_msg += f"💡 提示: {context}"
        
        return (
            {
                "error": error_msg,
                "error_type": error_type,
                "context": context
            },
            user_msg,
            {}
        )
    
    @staticmethod
    def safe_execute(func, *args, **kwargs):
        """安全执行函数"""
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            return ErrorHandler.format_error(e, f"执行 {func.__name__} 时出错")


# 创建全局客户端实例
_client_instance = None

def get_client(api_key: str = None) -> UnlimitAIClient:
    """获取API客户端实例"""
    global _client_instance
    
    if api_key:
        _client_instance = UnlimitAIClient(api_key)
    
    if not _client_instance:
        raise ValueError("未初始化API客户端，请提供API Key")
    
    return _client_instance
