import json

from typing_extensions import override

from comfy_api.latest import IO, ComfyExtension


PRICING = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-5": {"input": 0.03, "output": 0.06},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
    "deepseek-chat": {"input": 0.00014, "output": 0.00028},
    "deepseek-reasoner": {"input": 0.00055, "output": 0.00219},
}


class DramaConfigV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="DramaConfigV3Node",
            display_name="Drama Config [V3]",
            category="api node/config",
            description="Configuration node for drama workflow — select models and parameters in one place.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.Int.Input("num_scenes", default=10, min=1, max=50, step=1),
                IO.String.Input("drama_title", default="My Drama", multiline=False),
                IO.Combo.Input("text_model", options=["deepseek-chat", "gpt-4o", "claude-3-5-sonnet-20241022"], default="deepseek-chat"),
                IO.Combo.Input("target_language", options=["english", "chinese"], default="english"),
                IO.Combo.Input("art_style", options=["cinematic", "anime", "realistic", "artistic"], default="cinematic"),
                IO.Combo.Input("image_model", options=["flux-pro", "ideogram-v3", "kling-v2", "dall-e-3"], default="flux-pro"),
                IO.Combo.Input("image_aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Combo.Input("video_model", options=["kling-v2", "veo-3.1", "vidu2", "hailuo"], default="kling-v2"),
                IO.Combo.Input("video_duration", options=["5", "10"], default="5"),
                IO.Combo.Input("video_aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Combo.Input("voice_id", options=["male-qn-qingse", "male-qn-jingying", "female-shaonv", "female-yujie", "presenter_male", "presenter_female"], default="male-qn-jingying"),
                IO.Boolean.Input("generate_music", default=True),
            ],
            outputs=[
                IO.String.Output("api_key"),
                IO.String.Output("config_json"),
                IO.String.Output("text_config"),
                IO.String.Output("image_config"),
                IO.String.Output("video_config"),
                IO.String.Output("audio_config"),
                IO.String.Output("num_scenes_str"),
                IO.String.Output("drama_title"),
            ],
            hidden=[IO.Hidden.unique_id],
            is_api_node=False,
        )

    @classmethod
    async def execute(cls, api_key: str = "", num_scenes: int = 10, drama_title: str = "My Drama", text_model: str = "deepseek-chat", target_language: str = "english", art_style: str = "cinematic", image_model: str = "flux-pro", image_aspect_ratio: str = "16:9", video_model: str = "kling-v2", video_duration: str = "5", video_aspect_ratio: str = "16:9", voice_id: str = "male-qn-jingying", generate_music: bool = True):
        config = {
            "api_key": api_key,
            "num_scenes": num_scenes,
            "drama_title": drama_title,
            "text": {"model": text_model, "target_language": target_language, "art_style": art_style},
            "image": {"model": image_model, "aspect_ratio": image_aspect_ratio},
            "video": {"model": video_model, "duration": video_duration, "aspect_ratio": video_aspect_ratio},
            "audio": {"voice_id": voice_id, "generate_music": generate_music},
        }
        config_json = json.dumps(config, ensure_ascii=False, indent=2)
        text_config = json.dumps(config["text"], ensure_ascii=False)
        image_config = json.dumps(config["image"], ensure_ascii=False)
        video_config = json.dumps(config["video"], ensure_ascii=False)
        audio_config = json.dumps(config["audio"], ensure_ascii=False)
        return IO.NodeOutput(api_key, config_json, text_config, image_config, video_config, audio_config, str(num_scenes), drama_title)


class ModelComparisonV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="ModelComparisonV3Node",
            display_name="Model Comparison [V3]",
            category="api node/config",
            description="Compare models and pricing across providers.",
            inputs=[
                IO.Combo.Input("category", options=["text", "image", "video", "audio", "music"], default="text"),
            ],
            outputs=[IO.String.Output("comparison_json"), IO.String.Output("recommendation")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=False,
        )

    @classmethod
    async def execute(cls, category: str = "text"):
        models = {
            "text": [
                {"model": "gpt-4o", "provider": "OpenAI", "input_per_1k": 0.0025, "output_per_1k": 0.01, "strengths": "Best overall quality, fast"},
                {"model": "deepseek-chat", "provider": "DeepSeek", "input_per_1k": 0.00014, "output_per_1k": 0.00028, "strengths": "Cheapest, good quality"},
                {"model": "claude-3-5-sonnet-20241022", "provider": "Anthropic", "input_per_1k": 0.003, "output_per_1k": 0.015, "strengths": "Best for long context"},
            ],
            "image": [
                {"model": "flux-pro", "provider": "fal.ai", "price_per_image": 0.03, "strengths": "Fast, high quality"},
                {"model": "ideogram-v3", "provider": "Ideogram", "price_per_image": 0.02, "strengths": "Good at text rendering"},
                {"model": "kling-v2", "provider": "Kling", "price_per_image": 0.01, "strengths": "Cheapest option"},
            ],
            "video": [
                {"model": "veo-3.1", "provider": "Google", "price_per_video": 0.50, "strengths": "Highest quality, with audio"},
                {"model": "kling-v2", "provider": "Kling", "price_per_video": 0.10, "strengths": "Good quality, affordable"},
                {"model": "vidu2", "provider": "VIDU", "price_per_video": 0.08, "strengths": "Fast, affordable"},
            ],
            "audio": [
                {"model": "speech-01-turbo", "provider": "Minimax", "price_per_1k_chars": 0.001, "strengths": "Best for Chinese TTS"},
                {"model": "tts-1", "provider": "OpenAI", "price_per_1k_chars": 0.015, "strengths": "Natural English voices"},
            ],
            "music": [
                {"model": "chirp-v3-5", "provider": "Suno", "price_per_song": 0.05, "strengths": "Good quality, fast"},
                {"model": "chirp-v5", "provider": "Suno", "price_per_song": 0.08, "strengths": "Latest, best quality"},
            ],
        }
        category_models = models.get(category, [])
        comparison = json.dumps({"category": category, "models": category_models}, ensure_ascii=False, indent=2)
        recommendation = ""
        if category_models:
            recommendation = f"Best value: {category_models[0]['model']} — {category_models[0]['strengths']}"
        return IO.NodeOutput(comparison, recommendation)


class CostEstimatorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="CostEstimatorV3Node",
            display_name="Cost Estimator [V3]",
            category="api node/config",
            description="Estimate API cost based on model and usage.",
            inputs=[
                IO.Combo.Input("model", options=list(PRICING.keys()), default="gpt-4o"),
                IO.Int.Input("input_tokens", default=1000, min=1, max=10000000, step=1),
                IO.Int.Input("output_tokens", default=500, min=1, max=10000000, step=1),
            ],
            outputs=[IO.Float.Output("estimated_cost"), IO.String.Output("breakdown")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=False,
        )

    @classmethod
    async def execute(cls, model: str = "gpt-4o", input_tokens: int = 1000, output_tokens: int = 500):
        rates = PRICING.get(model, {"input": 0.0, "output": 0.0})
        cost = (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])
        breakdown = f"Model: {model}\nInput: {input_tokens} tokens × ${rates['input']:.6f}/1k = ${input_tokens / 1000 * rates['input']:.6f}\nOutput: {output_tokens} tokens × ${rates['output']:.6f}/1k = ${output_tokens / 1000 * rates['output']:.6f}\nTotal: ${cost:.6f}"
        return IO.NodeOutput(cost, breakdown)


class UnlimitAIConfigV3Extension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        return [DramaConfigV3Node, ModelComparisonV3Node, CostEstimatorV3Node]


async def comfy_entrypoint() -> UnlimitAIConfigV3Extension:
    return UnlimitAIConfigV3Extension()
