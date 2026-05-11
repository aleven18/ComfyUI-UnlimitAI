"""
Utility functions for ComfyUI-UnlimitAI nodes.
"""
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, Tuple
import hashlib
import os

from .exceptions import APIError, APIRateLimitError, APIConnectionError, APITimeoutError


UNLIMITAI_BASE_URL = "https://api.unlimitai.org"


def make_request(
    endpoint: str,
    api_key: str,
    payload: Dict[str, Any],
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Make HTTP request to UnlimitAI API.
    
    Args:
        endpoint: API endpoint (e.g., "/v1/chat/completions")
        api_key: UnlimitAI API key
        payload: Request payload
        method: HTTP method (POST, GET)
        headers: Additional headers
        timeout: Request timeout in seconds
    
    Returns:
        Response data as dictionary
    """
    url = f"{UNLIMITAI_BASE_URL}{endpoint}"
    
    default_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    if headers:
        default_headers.update(headers)
    
    req_data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=req_data if method == "POST" else None,
        headers=default_headers,
        method=method
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        if e.code == 429:
            retry_after = None
            try:
                err_json = json.loads(error_body)
                retry_after = err_json.get("retry_after") or err_json.get("retry-after")
            except (json.JSONDecodeError, TypeError):
                pass
            raise APIRateLimitError(retry_after=retry_after)
        elif e.code in (401, 403):
            from .exceptions import APIAuthError
            raise APIAuthError(message=f"Auth error {e.code}: {error_body}")
        elif e.code >= 500:
            from .exceptions import APIServerError
            raise APIServerError(status_code=e.code, message=f"Server error: {error_body}")
        else:
            raise APIError(
                message=f"API Error {e.code}: {error_body}",
                status_code=e.code,
                url=url
            )
    except urllib.error.URLError as e:
        raise APIConnectionError(url=url, cause=e)
    except json.JSONDecodeError as e:
        from .exceptions import APIResponseError
        raise APIResponseError(message=f"JSON Decode Error: {e}", response=None)
    except TimeoutError as e:
        raise APITimeoutError(timeout=timeout, url=url)


def make_multipart_request(
    endpoint: str,
    api_key: str,
    data: Dict[str, Any],
    files: Optional[Dict[str, Tuple[str, bytes]]] = None,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Make multipart/form-data request for file uploads.
    
    Args:
        endpoint: API endpoint
        api_key: UnlimitAI API key
        data: Form fields
        files: Dictionary of {field_name: (filename, file_bytes)}
        timeout: Request timeout in seconds
    
    Returns:
        Response data as dictionary
    """
    url = f"{UNLIMITAI_BASE_URL}{endpoint}"
    
    boundary = hashlib.md5(str(time.time()).encode()).hexdigest()
    
    body_parts = []
    
    for key, value in data.items():
        body_parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
            f'{value}\r\n'
        )
    
    if files:
        for field_name, (filename, file_bytes) in files.items():
            body_parts.append(
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
                f'Content-Type: application/octet-stream\r\n\r\n'
            )
            body_parts.append(file_bytes)
            body_parts.append(b'\r\n')
    
    body_parts.append(f'--{boundary}--\r\n')
    
    body = b''.join(
        part.encode('utf-8') if isinstance(part, str) else part
        for part in body_parts
    )
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "application/json"
    }
    
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        if e.code == 429:
            raise APIRateLimitError()
        else:
            raise APIError(
                message=f"API Error {e.code}: {error_body}",
                status_code=e.code,
                url=url
            )
    except urllib.error.URLError as e:
        raise APIConnectionError(url=url, cause=e)


def poll_status(
    status_url: str,
    api_key: str,
    interval: int = 5,
    max_attempts: int = 120,
    success_status: str = "succeeded"
) -> Dict[str, Any]:
    """
    Poll async job status until completion.
    
    Args:
        status_url: Status check URL
        api_key: UnlimitAI API key
        interval: Polling interval in seconds
        max_attempts: Maximum number of polling attempts
        success_status: Status indicating success
    
    Returns:
        Final response data
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    req = urllib.request.Request(status_url, headers=headers, method="GET")
    
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                result = json.loads(response_data)
                
                status = result.get("status")
                
                if status == success_status:
                    return result
                elif status in ["failed", "error", "canceled"]:
                    from .exceptions import APIResponseError
                    raise APIResponseError(
                        message=f"Job failed with status: {status}. Error: {result.get('error', 'Unknown error')}",
                        response=result
                    )
                
                time.sleep(interval)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            if e.code == 429:
                raise APIRateLimitError()
            else:
                raise APIError(
                    message=f"Status check error {e.code}: {error_body}",
                    status_code=e.code,
                    url=status_url
                )
        except urllib.error.URLError as e:
            raise APIConnectionError(url=status_url, cause=e)
    
    raise APITimeoutError(timeout=max_attempts * interval, url=status_url)


def download_file(url: str, save_path: str, timeout: int = 60) -> str:
    """
    Download file from URL to local path.
    
    Args:
        url: File URL
        save_path: Local save path
        timeout: Download timeout in seconds
    
    Returns:
        Absolute path to saved file
    """
    abs_path = os.path.abspath(save_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    req = urllib.request.Request(url)
    
    with urllib.request.urlopen(req, timeout=timeout) as response:
        with open(abs_path, 'wb') as f:
            f.write(response.read())
    
    return abs_path


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode image file to base64 string.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Base64 encoded string
    """
    import base64
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    return base64.b64encode(image_data).decode('utf-8')


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
    
    Returns:
        True if valid format
    """
    if not api_key:
        return False
    if not api_key.startswith("sk-"):
        return False
    if len(api_key) < 20:
        return False
    return True


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Estimate API cost based on token usage.
    
    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    
    Returns:
        Estimated cost in USD
    """
    pricing = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-5": {"input": 0.03, "output": 0.06},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "deepseek-chat": {"input": 0.00014, "output": 0.00028},
        "deepseek-reasoner": {"input": 0.00055, "output": 0.00219},
    }
    
    if model not in pricing:
        return 0.0
    
    rates = pricing[model]
    cost = (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])
    return cost
