"""
ComfyUI-UnlimitAI
Custom nodes for ComfyUI to use UnlimitAI API services.

Features:
- Text generation (GPT-4, Claude, DeepSeek, GPT-5)
- Image generation (FLUX, Ideogram, Kling, DALL-E, Imagen, Recraft)
- Video generation (VEO, Kling, Minimax, VIDU, Luma, Runway)
- Audio/Speech (Minimax TTS, OpenAI TTS, Whisper, Voice Cloning)
- Music generation (Suno)
- Novel to Drama workflow
- Advanced optimization features (preview, retry, parallel, etc.)
- Character management (image loading, voice definition, consistency)

Author: AI Assistant
Version: 1.2.0
"""

from .nodes.text_nodes import NODE_CLASS_MAPPINGS as TEXT_NODES
from .nodes.text_nodes import NODE_DISPLAY_NAME_MAPPINGS as TEXT_NAMES

from .nodes.image_nodes import NODE_CLASS_MAPPINGS as IMAGE_NODES
from .nodes.image_nodes import NODE_DISPLAY_NAME_MAPPINGS as IMAGE_NAMES

from .nodes.video_nodes import NODE_CLASS_MAPPINGS as VIDEO_NODES
from .nodes.video_nodes import NODE_DISPLAY_NAME_MAPPINGS as VIDEO_NAMES

from .nodes.audio_nodes import NODE_CLASS_MAPPINGS as AUDIO_NODES
from .nodes.audio_nodes import NODE_DISPLAY_NAME_MAPPINGS as AUDIO_NAMES

from .nodes.music_nodes import NODE_CLASS_MAPPINGS as MUSIC_NODES
from .nodes.music_nodes import NODE_DISPLAY_NAME_MAPPINGS as MUSIC_NAMES

from .nodes.workflow_nodes import NODE_CLASS_MAPPINGS as WORKFLOW_NODES
from .nodes.workflow_nodes import NODE_DISPLAY_NAME_MAPPINGS as WORKFLOW_NAMES

from .nodes.config_nodes import NODE_CLASS_MAPPINGS as CONFIG_NODES
from .nodes.config_nodes import NODE_DISPLAY_NAME_MAPPINGS as CONFIG_NAMES

from .nodes.optimized_nodes import NODE_CLASS_MAPPINGS as OPTIMIZED_NODES
from .nodes.optimized_nodes import NODE_DISPLAY_NAME_MAPPINGS as OPTIMIZED_NAMES

from .nodes.advanced_nodes import NODE_CLASS_MAPPINGS as ADVANCED_NODES
from .nodes.advanced_nodes import NODE_DISPLAY_NAME_MAPPINGS as ADVANCED_NAMES

from .nodes.character_nodes import NODE_CLASS_MAPPINGS as CHARACTER_NODES
from .nodes.character_nodes import NODE_DISPLAY_NAME_MAPPINGS as CHARACTER_NAMES

from .nodes.video_enhanced_nodes import NODE_CLASS_MAPPINGS as VIDEO_ENHANCED_NODES
from .nodes.video_enhanced_nodes import NODE_DISPLAY_NAME_MAPPINGS as VIDEO_ENHANCED_NAMES


NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(TEXT_NODES)
NODE_CLASS_MAPPINGS.update(IMAGE_NODES)
NODE_CLASS_MAPPINGS.update(VIDEO_NODES)
NODE_CLASS_MAPPINGS.update(AUDIO_NODES)
NODE_CLASS_MAPPINGS.update(MUSIC_NODES)
NODE_CLASS_MAPPINGS.update(WORKFLOW_NODES)
NODE_CLASS_MAPPINGS.update(CONFIG_NODES)
NODE_CLASS_MAPPINGS.update(OPTIMIZED_NODES)
NODE_CLASS_MAPPINGS.update(ADVANCED_NODES)
NODE_CLASS_MAPPINGS.update(CHARACTER_NODES)
NODE_CLASS_MAPPINGS.update(VIDEO_ENHANCED_NODES)


NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(TEXT_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(IMAGE_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(VIDEO_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(AUDIO_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(MUSIC_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(WORKFLOW_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(CONFIG_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(OPTIMIZED_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(ADVANCED_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(CHARACTER_NAMES)
NODE_DISPLAY_NAME_MAPPINGS.update(VIDEO_ENHANCED_NAMES)


# V3 nodes (IO.ComfyNode) are compatible with NODE_CLASS_MAPPINGS registration.
# ComfyNode provides V1-compatible INPUT_TYPES, RETURN_TYPES, FUNCTION, CATEGORY etc.
# We register them by their schema node_id so they appear in the frontend alongside V1/V2 nodes.
def _register_v3_nodes():
    import logging
    _logger = logging.getLogger(__name__)
    v3_nodes = []

    try:
        from .nodes.workflow_nodes_v3 import (
            StoryboardComposerV3Node,
            NovelToDramaV3Node,
            SceneImageGeneratorV3Node,
            SceneVideoGeneratorV3Node,
            SceneAudioGeneratorV3Node,
            DramaManifestV3Node,
            StoryboardVideoV3Node,
            StoryboardProV3Node,
        )
        v3_nodes.extend([
            StoryboardComposerV3Node,
            NovelToDramaV3Node,
            SceneImageGeneratorV3Node,
            SceneVideoGeneratorV3Node,
            SceneAudioGeneratorV3Node,
            DramaManifestV3Node,
            StoryboardVideoV3Node,
            StoryboardProV3Node,
        ])
    except Exception:
        _logger.exception("Failed to register workflow_nodes_v3")

    try:
        from .nodes.optimized_nodes_v3 import (
            OptimizedNovelAnalyzerV3Node,
            OptimizedImageGeneratorV3Node,
            OptimizedVideoGeneratorV3Node,
            OptimizedAudioGeneratorV3Node,
        )
        v3_nodes.extend([
            OptimizedNovelAnalyzerV3Node,
            OptimizedImageGeneratorV3Node,
            OptimizedVideoGeneratorV3Node,
            OptimizedAudioGeneratorV3Node,
        ])
    except Exception:
        _logger.exception("Failed to register optimized_nodes_v3")

    try:
        from .nodes.image_nodes_v3 import (
            FluxProV3Node,
            FluxProKontextV3Node,
            IdeogramV3V3Node,
            KlingImageGenV3Node,
            KlingMultiImage2ImageV3Node,
            KlingOmniImageV3Node,
            KlingImageExpandV3Node,
            KlingVirtualTryOnV3Node,
            GPTImageV3Node,
            Imagen4V3Node,
            RecraftV3V3Node,
        )
        v3_nodes.extend([
            FluxProV3Node,
            FluxProKontextV3Node,
            IdeogramV3V3Node,
            KlingImageGenV3Node,
            KlingMultiImage2ImageV3Node,
            KlingOmniImageV3Node,
            KlingImageExpandV3Node,
            KlingVirtualTryOnV3Node,
            GPTImageV3Node,
            Imagen4V3Node,
            RecraftV3V3Node,
        ])
    except Exception:
        _logger.exception("Failed to register image_nodes_v3")

    try:
        from .nodes.video_nodes_v3 import (
            KlingVideoV3Node,
            KlingImageToVideoV3Node,
            KlingDigitalHumanV3Node,
            KlingMultiImage2VideoV3Node,
            KlingOmniVideoV3Node,
            KlingMultiElementsV3Node,
            KlingVideoExtendV3Node,
            KlingEffectsV3Node,
            KlingMotionControlV3Node,
            KlingCameraControlV3Node,
            KlingLipSyncV3Node,
            VEOV3Node,
            VEOFalAIV3Node,
            MinimaxHailuoV3Node,
            VIDUVideoV3Node,
            VIDUImageToVideoV3Node,
            LumaVideoV3Node,
            RunwayGen4V3Node,
        )
        v3_nodes.extend([
            KlingVideoV3Node,
            KlingImageToVideoV3Node,
            KlingDigitalHumanV3Node,
            KlingMultiImage2VideoV3Node,
            KlingOmniVideoV3Node,
            KlingMultiElementsV3Node,
            KlingVideoExtendV3Node,
            KlingEffectsV3Node,
            KlingMotionControlV3Node,
            KlingCameraControlV3Node,
            KlingLipSyncV3Node,
            VEOV3Node,
            VEOFalAIV3Node,
            MinimaxHailuoV3Node,
            VIDUVideoV3Node,
            VIDUImageToVideoV3Node,
            LumaVideoV3Node,
            RunwayGen4V3Node,
        ])
    except Exception:
        _logger.exception("Failed to register video_nodes_v3")

    try:
        from .nodes.audio_nodes_v3 import (
            MinimaxTTSV3Node,
            MinimaxTTSAsyncV3Node,
            MinimaxVoiceCloneV3Node,
            OpenAITTSV3Node,
            OpenAIWhisperV3Node,
            KlingAudioGenV3Node,
            KlingVideoToAudioV3Node,
            KlingTTSV3Node,
            KlingCustomVoiceV3Node,
            KlingPresetVoicesV3Node,
            DialogueGeneratorV3Node,
        )
        v3_nodes.extend([
            MinimaxTTSV3Node,
            MinimaxTTSAsyncV3Node,
            MinimaxVoiceCloneV3Node,
            OpenAITTSV3Node,
            OpenAIWhisperV3Node,
            KlingAudioGenV3Node,
            KlingVideoToAudioV3Node,
            KlingTTSV3Node,
            KlingCustomVoiceV3Node,
            KlingPresetVoicesV3Node,
            DialogueGeneratorV3Node,
        ])
    except Exception:
        _logger.exception("Failed to register audio_nodes_v3")

    try:
        from .nodes.music_nodes_v3 import (
            SunoInspirationV3Node,
            SunoCustomModeV3Node,
            SunoLyricsGeneratorV3Node,
            SunoExtendV3Node,
            BackgroundMusicV3Node,
            SoundtrackComposerV3Node,
        )
        v3_nodes.extend([
            SunoInspirationV3Node,
            SunoCustomModeV3Node,
            SunoLyricsGeneratorV3Node,
            SunoExtendV3Node,
            BackgroundMusicV3Node,
            SoundtrackComposerV3Node,
        ])
    except Exception:
        _logger.exception("Failed to register music_nodes_v3")

    try:
        from .nodes.text_nodes_v3 import (
            UnlimitAITextV3Node,
            GPT5ReasoningV3Node,
            DeepSeekThinkingV3Node,
            StructuredOutputV3Node,
            NovelAnalyzerV3Node,
            SceneTranslatorV3Node,
            VisionChatV3Node,
        )
        v3_nodes.extend([
            UnlimitAITextV3Node,
            GPT5ReasoningV3Node,
            DeepSeekThinkingV3Node,
            StructuredOutputV3Node,
            NovelAnalyzerV3Node,
            SceneTranslatorV3Node,
            VisionChatV3Node,
        ])
    except Exception:
        _logger.exception("Failed to register text_nodes_v3")

    try:
        from .nodes.config_nodes_v3 import (
            DramaConfigV3Node,
            ModelComparisonV3Node,
            CostEstimatorV3Node,
        )
        v3_nodes.extend([
            DramaConfigV3Node,
            ModelComparisonV3Node,
            CostEstimatorV3Node,
        ])
    except Exception:
        _logger.exception("Failed to register config_nodes_v3")

    for node_cls in v3_nodes:
        try:
            schema = node_cls.GET_SCHEMA()
            node_id = schema.node_id
            if node_id not in NODE_CLASS_MAPPINGS:
                NODE_CLASS_MAPPINGS[node_id] = node_cls
            if schema.display_name is not None:
                NODE_DISPLAY_NAME_MAPPINGS[node_id] = schema.display_name
        except Exception:
            _logger.exception(f"Failed to register V3 node: {node_cls.__name__}")


_register_v3_nodes()


WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
