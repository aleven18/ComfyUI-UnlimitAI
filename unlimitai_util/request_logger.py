import datetime
import hashlib
import json
import logging
import os
import re
from typing import Any

import folder_paths

logger = logging.getLogger(__name__)


def get_log_directory():
    base_temp_dir = folder_paths.get_temp_directory()
    log_dir = os.path.join(base_temp_dir, "unlimitai_api_logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        logger.error("Error creating API log directory %s: %s", log_dir, str(e))
        return base_temp_dir
    return log_dir


def _sanitize_filename_component(name: str) -> str:
    if not name:
        return "log"
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    sanitized = sanitized.strip(" ._")
    if not sanitized:
        sanitized = "log"
    return sanitized


def _short_hash(*parts: str, length: int = 10) -> str:
    return hashlib.sha1(("|".join(parts)).encode("utf-8")).hexdigest()[:length]


def _build_log_filepath(log_dir: str, operation_id: str, request_url: str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    slug = _sanitize_filename_component(operation_id)
    h = _short_hash(operation_id or "", request_url or "")
    max_total_path = 240
    prefix = f"{timestamp}_"
    suffix = f"_{h}.log"
    if not slug:
        slug = "op"
    max_filename_len = max(60, max_total_path - len(log_dir) - 1)
    max_slug_len = max(8, max_filename_len - len(prefix) - len(suffix))
    if len(slug) > max_slug_len:
        slug = slug[:max_slug_len].rstrip(" ._-")
    return os.path.join(log_dir, f"{prefix}{slug}{suffix}")


def _format_data_for_logging(data: Any) -> str:
    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return f"[Binary data of length {len(data)} bytes]"
    elif isinstance(data, (dict, list)):
        try:
            return json.dumps(data, indent=2, ensure_ascii=False)
        except TypeError:
            return str(data)
    return str(data)


def log_request_response(
    operation_id: str,
    request_method: str,
    request_url: str,
    request_headers: dict | None = None,
    request_params: dict | None = None,
    request_data: Any = None,
    response_status_code: int | None = None,
    response_headers: dict | None = None,
    response_content: Any = None,
    error_message: str | None = None,
):
    try:
        log_dir = get_log_directory()
        filepath = _build_log_filepath(log_dir, operation_id, request_url)

        log_content: list[str] = []
        log_content.append(f"Timestamp: {datetime.datetime.now().isoformat()}")
        log_content.append(f"Operation ID: {operation_id}")
        log_content.append("-" * 30 + " REQUEST " + "-" * 30)
        log_content.append(f"Method: {request_method}")
        log_content.append(f"URL: {request_url}")
        if request_headers:
            sanitized_headers = {k: v for k, v in request_headers.items() if k.lower() != "authorization"}
            log_content.append(f"Headers:\n{_format_data_for_logging(sanitized_headers)}")
        if request_params:
            log_content.append(f"Params:\n{_format_data_for_logging(request_params)}")
        if request_data is not None:
            log_content.append(f"Data/Body:\n{_format_data_for_logging(request_data)}")

        log_content.append("\n" + "-" * 30 + " RESPONSE " + "-" * 30)
        if response_status_code is not None:
            log_content.append(f"Status Code: {response_status_code}")
        if response_headers:
            log_content.append(f"Headers:\n{_format_data_for_logging(response_headers)}")
        if response_content is not None:
            log_content.append(f"Content:\n{_format_data_for_logging(response_content)}")
        if error_message:
            log_content.append(f"Error:\n{error_message}")

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(log_content))
        except Exception as e:
            logger.error("Error writing API log to %s: %s", filepath, str(e))
    except Exception as _log_e:
        logging.debug("log_request_response failed: %s", _log_e)
