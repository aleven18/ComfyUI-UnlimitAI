import json
import pytest
from unittest.mock import MagicMock, patch

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestStoryboardComposerV3:
    def test_schema_defined(self):
        from nodes.workflow_nodes_v3 import StoryboardComposerV3Node
        schema = StoryboardComposerV3Node.define_schema()
        assert schema is not None

    def test_output_storyboard_json(self):
        from nodes.workflow_nodes_v3 import StoryboardComposerV3Node
        from comfy_api.latest import IO
        result = StoryboardComposerV3Node.execute(total_duration="5", storyboards=None)
        assert result.outputs[0].value == ""

    @pytest.mark.asyncio
    async def test_valid_segments(self):
        from nodes.workflow_nodes_v3 import StoryboardComposerV3Node
        sb = {
            "storyboards": "2 segments",
            "storyboard_1_prompt": "A fox walks through forest",
            "storyboard_1_duration": 3,
            "storyboard_2_prompt": "The fox finds a glowing flower",
            "storyboard_2_duration": 2,
        }
        result = await StoryboardComposerV3Node.execute(total_duration="5", storyboards=sb)
        parsed = json.loads(result.outputs[0].value)
        assert parsed["total_duration"] == 5
        assert len(parsed["segments"]) == 2

    @pytest.mark.asyncio
    async def test_duration_mismatch_raises(self):
        from nodes.workflow_nodes_v3 import StoryboardComposerV3Node
        from unlimitai_util.common_exceptions import ValidationError
        sb = {
            "storyboards": "2 segments",
            "storyboard_1_prompt": "Scene one",
            "storyboard_1_duration": 3,
            "storyboard_2_prompt": "Scene two",
            "storyboard_2_duration": 3,
        }
        with pytest.raises(ValidationError, match="must equal total_duration"):
            await StoryboardComposerV3Node.execute(total_duration="5", storyboards=sb)

    @pytest.mark.asyncio
    async def test_empty_prompt_raises(self):
        from nodes.workflow_nodes_v3 import StoryboardComposerV3Node
        from unlimitai_util.common_exceptions import ValidationError
        sb = {
            "storyboards": "2 segments",
            "storyboard_1_prompt": "   ",
            "storyboard_1_duration": 3,
            "storyboard_2_prompt": "Scene two",
            "storyboard_2_duration": 2,
        }
        with pytest.raises(ValidationError, match="prompt is empty"):
            await StoryboardComposerV3Node.execute(total_duration="5", storyboards=sb)


class TestCameraPresets:
    def test_dolly_in(self):
        from nodes.workflow_nodes_v3 import CAMERA_PRESETS
        assert "dolly-in" in CAMERA_PRESETS
        assert CAMERA_PRESETS["dolly-in"].zoom is not None

    def test_static_default(self):
        from nodes.workflow_nodes_v3 import CAMERA_PRESETS
        static = CAMERA_PRESETS["static"]
        assert static.horizontal == 0.0
        assert static.vertical == 0.0

    def test_all_presets_have_keys(self):
        from nodes.workflow_nodes_v3 import CAMERA_PRESETS
        expected = {"dolly-in", "dolly-out", "pan-left", "pan-right", "tilt-up",
                    "tilt-down", "static", "orbit", "tracking", "handheld",
                    "crane-up", "crane-down", "zoom-in", "zoom-out", "slow-push", "reveal"}
        assert set(CAMERA_PRESETS.keys()) == expected


class TestMapCameraTextToPreset:
    def test_known_preset(self):
        from nodes.workflow_nodes_v3 import _map_camera_text_to_preset, CAMERA_PRESETS
        result = _map_camera_text_to_preset("dolly-in")
        assert result is not None
        assert result.zoom == CAMERA_PRESETS["dolly-in"].zoom

    def test_fuzzy_match(self):
        from nodes.workflow_nodes_v3 import _map_camera_text_to_preset
        result = _map_camera_text_to_preset("slow push in")
        assert result is not None

    def test_empty_returns_none(self):
        from nodes.workflow_nodes_v3 import _map_camera_text_to_preset
        assert _map_camera_text_to_preset("") is None
        assert _map_camera_text_to_preset(None) is None

    def test_unknown_returns_none(self):
        from nodes.workflow_nodes_v3 import _map_camera_text_to_preset
        assert _map_camera_text_to_preset("teleport to mars") is None


class TestParseCameraValuesFromSegment:
    def test_valid_values(self):
        from nodes.workflow_nodes_v3 import _parse_camera_values_from_segment
        seg = {"camera_values": {"horizontal": 0.5, "vertical": -0.3, "pan": 0.1,
                                  "tilt": 0.0, "roll": 0.0, "zoom": -0.2}}
        result = _parse_camera_values_from_segment(seg)
        assert result is not None
        assert result.horizontal == 0.5
        assert result.vertical == -0.3

    def test_clamping(self):
        from nodes.workflow_nodes_v3 import _parse_camera_values_from_segment
        seg = {"camera_values": {"horizontal": 5.0, "zoom": 100.0}}
        result = _parse_camera_values_from_segment(seg)
        assert result.horizontal == 1.0
        assert result.zoom == 10.0

    def test_missing_camera_values(self):
        from nodes.workflow_nodes_v3 import _parse_camera_values_from_segment
        assert _parse_camera_values_from_segment({}) is None
        assert _parse_camera_values_from_segment({"camera_values": None}) is None


class TestValidateCharacterUrls:
    def test_valid_urls(self):
        from nodes.workflow_nodes_v3 import _validate_character_urls
        urls = _validate_character_urls("https://example.com/img1.jpg\nhttps://example.com/img2.jpg")
        assert len(urls) == 2

    def test_invalid_url_raises(self):
        from nodes.workflow_nodes_v3 import _validate_character_urls
        from unlimitai_util.common_exceptions import ValidationError
        with pytest.raises(ValidationError, match="not a valid URL"):
            _validate_character_urls("not-a-url")

    def test_empty_input(self):
        from nodes.workflow_nodes_v3 import _validate_character_urls
        assert _validate_character_urls("") == []
        assert _validate_character_urls("  \n  ") == []


class TestSanitizeForPrompt:
    def test_strips_html(self):
        from nodes.workflow_nodes_v3 import _sanitize_for_prompt
        assert "<script>" not in _sanitize_for_prompt("hello <script>alert(1)</script> world")

    def test_strips_code_blocks(self):
        from nodes.workflow_nodes_v3 import _sanitize_for_prompt
        assert "```" not in _sanitize_for_prompt("text ```system prompt``` end")

    def test_max_length(self):
        from nodes.workflow_nodes_v3 import _sanitize_for_prompt
        long_text = "x" * 5000
        assert len(_sanitize_for_prompt(long_text, max_len=100)) <= 100


class TestAspectRatiMaps:
    def test_all_providers_present(self):
        from nodes.workflow_nodes_v3 import ASPECT_RATIO_MAPS
        assert "flux" in ASPECT_RATIO_MAPS
        assert "ideogram" in ASPECT_RATIO_MAPS
        assert "gpt_image" in ASPECT_RATIO_MAPS
        assert "dalle" in ASPECT_RATIO_MAPS

    def test_all_ratios_covered(self):
        from nodes.workflow_nodes_v3 import ASPECT_RATIO_MAPS
        for provider, mapping in ASPECT_RATIO_MAPS.items():
            assert "16:9" in mapping, f"{provider} missing 16:9"
            assert "9:16" in mapping, f"{provider} missing 9:16"
            assert "1:1" in mapping, f"{provider} missing 1:1"


class TestPricingConstants:
    def test_llm_pricing(self):
        from nodes.workflow_nodes_v3 import LLM_PRICING
        assert "deepseek-chat" in LLM_PRICING
        assert "gpt-4o" in LLM_PRICING
        assert "input" in LLM_PRICING["deepseek-chat"]
        assert "output" in LLM_PRICING["deepseek-chat"]

    def test_image_pricing(self):
        from nodes.workflow_nodes_v3 import IMAGE_PRICING
        assert "kling-v2" in IMAGE_PRICING
        assert "flux-pro" in IMAGE_PRICING

    def test_video_pricing(self):
        from nodes.workflow_nodes_v3 import VIDEO_PRICING
        assert "kling-v2-master" in VIDEO_PRICING
        assert "kling-v3" in VIDEO_PRICING


class TestKlingPydanticModels:
    def test_kling_image_gen_request(self):
        from apis.kling import KlingImageGenRequest
        req = KlingImageGenRequest(model_name="kling-v2", prompt="test", aspect_ratio="16:9", n=1)
        assert req.model_name == "kling-v2"

    def test_kling_t2v_request(self):
        from apis.kling import KlingText2VideoRequest
        req = KlingText2VideoRequest(model_name="kling-v2-master", prompt="test", duration="5", aspect_ratio="16:9")
        assert req.model_name == "kling-v2-master"

    def test_kling_multi_prompt_item(self):
        from apis.kling import KlingMultiPromptItem
        item = KlingMultiPromptItem(index=1, prompt="test", duration="5")
        assert item.index == 1

    def test_kling_camera_config(self):
        from apis.kling import KlingCameraConfig
        cfg = KlingCameraConfig(horizontal=0.5, zoom=-0.3)
        assert cfg.horizontal == 0.5
        assert cfg.zoom == -0.3


class TestStoryboardVideoV3Node:
    def test_schema_defined(self):
        from nodes.workflow_nodes_v3 import StoryboardVideoV3Node
        schema = StoryboardVideoV3Node.define_schema()
        assert schema is not None

    @pytest.mark.asyncio
    async def test_invalid_json_raises(self):
        from nodes.workflow_nodes_v3 import StoryboardVideoV3Node
        from unlimitai_util.common_exceptions import ValidationError
        with pytest.raises(ValidationError, match="Invalid segments_json"):
            await StoryboardVideoV3Node.execute(
                api_key="sk-test-key-12345678",
                segments_json="not json{{{",
            )


class TestExtractSettingFromMaster:
    def test_extracts_setting(self):
        from nodes.workflow_nodes_v3 import _extract_setting_from_master
        master = """1. CHARACTERS
A young girl with red hair.

2. SETTING
A dark forest at midnight with glowing mushrooms.

3. VISUAL STYLE
Cinematic and moody."""
        result = _extract_setting_from_master(master)
        assert "dark forest" in result

    def test_no_setting_returns_empty(self):
        from nodes.workflow_nodes_v3 import _extract_setting_from_master
        result = _extract_setting_from_master("Just some random text without sections")
        assert result == ""
