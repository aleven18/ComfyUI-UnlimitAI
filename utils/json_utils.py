import json
import logging

logger = logging.getLogger(__name__)


def parse_json_safe(text: str, key: str = "") -> dict:
    if not text or not text.strip():
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON%s: %s", f" for {key}" if key else "", e)
        return {}
