from typing_extensions import override

from comfy_api.latest import IO, ComfyExtension

from ..unlimitai_util import (
    ApiEndpoint,
    sync_op,
    validate_api_key,
    validate_string,
)
from ..apis.text import TextGenerationRequest, TextGenerationResponse, ChatMessage, extract_text_content

from .workflow_nodes_v3 import (
    SceneImageGeneratorV3Node,
    SceneVideoGeneratorV3Node,
    SceneAudioGeneratorV3Node,
)
from ..utils.json_utils import parse_json_safe


class OptimizedNovelAnalyzerV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OptimizedNovelAnalyzerV3Node",
            display_name="Optimized Novel Analyzer [V3]",
            category="api node/workflow/Optimized",
            description="Optimized novel analyzer with api_key input support.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key (connectable)."),
                IO.String.Input("novel_text", multiline=True, default="", tooltip="Novel text to analyze."),
                IO.Int.Input("num_scenes", default=10, min=1, max=50, step=1),
                IO.Combo.Input("model", options=["deepseek-chat", "gpt-4o", "claude-3-5-sonnet-20241022"], default="deepseek-chat"),
                IO.Combo.Input("target_language", options=["english", "chinese"], default="english"),
                IO.Combo.Input("art_style", options=["cinematic", "anime", "realistic", "artistic"], default="cinematic"),
            ],
            outputs=[IO.String.Output("scenes_json"), IO.String.Output("summary"), IO.Float.Output("total_cost")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", novel_text: str = "", num_scenes: int = 10, model: str = "deepseek-chat", target_language: str = "english", art_style: str = "cinematic"):
        validate_string(novel_text, field_name="novel_text")
        key = validate_api_key(api_key)
        lang_instruction = "使用中文" if target_language == "chinese" else "Use English"
        prompt = f"""{lang_instruction}分析以下小说文本，提取{num_scenes}个关键场景用于制作漫剧视频。

对于每个场景，提供以下信息：
1. scene_number: 场景编号
2. title: 场景标题
3. description: 场景描述（包含人物、动作、环境、情感）
4. characters: 出场人物列表
5. mood: 场景氛围
6. dialogue: 关键对话或内心独白
7. visual_prompt: 用于生成图像的详细英文提示词，{art_style} style
8. camera_movement: 建议的镜头运动

小说文本：
{novel_text}

请以JSON数组格式返回场景列表。"""
        schema = {"type": "object", "properties": {"scenes": {"type": "array", "items": {"type": "object", "properties": {"scene_number": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}, "characters": {"type": "array", "items": {"type": "string"}}, "mood": {"type": "string"}, "dialogue": {"type": "string"}, "visual_prompt": {"type": "string"}, "camera_movement": {"type": "string"}}}}, "summary": {"type": "string"}}}
        request = TextGenerationRequest(model=model, messages=[ChatMessage(role="user", content=prompt)], temperature=0.7, response_format={"type": "json_schema", "json_schema": {"name": "novel_scenes", "schema": schema}})
        response: TextGenerationResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"), data=request, response_model=TextGenerationResponse, api_key=key, wait_label="Analyzing novel", estimated_duration=20)
        text = extract_text_content(response.choices[0].message.content) if response.choices else ""
        pricing = {"deepseek-chat": {"input": 0.00014, "output": 0.00028}, "gpt-4o": {"input": 0.0025, "output": 0.01}, "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015}}
        rates = pricing.get(model, pricing["deepseek-chat"])
        pt = response.usage.prompt_tokens
        ct = response.usage.completion_tokens
        cost = (pt / 1000 * rates["input"]) + (ct / 1000 * rates["output"])
        data = parse_json_safe(text, "scenes")
        summary = data.get("summary", "")
        return IO.NodeOutput(text, summary, cost)


class OptimizedImageGeneratorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OptimizedImageGeneratorV3Node",
            display_name="Optimized Image Generator [V3]",
            category="api node/workflow/Optimized",
            description="Optimized image generator with api_key input support.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key (connectable)."),
                IO.String.Input("scenes_json", multiline=True, default="", tooltip="Scenes JSON."),
                IO.Combo.Input("image_model", options=["flux-pro", "ideogram-v3", "kling-v2", "dall-e-3"], default="flux-pro"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Int.Input("max_scenes", default=10, min=1, max=50, step=1),
                IO.Image.Input("ref_image", optional=True, tooltip="Reference image for character consistency (Kling only)."),
                IO.String.Input("ref_image_url", default="", multiline=False, optional=True, tooltip="Or provide a reference image URL (Kling only)."),
                IO.Combo.Input("image_reference", options=["none", "subject", "face"], default="none", tooltip="Subject: keep character appearance. Face: keep facial features only. Kling only."),
                IO.Float.Input("image_fidelity", default=0.5, min=0.0, max=1.0, step=0.01, tooltip="Reference image intensity. Kling only."),
                IO.Float.Input("human_fidelity", default=0.45, min=0.0, max=1.0, step=0.01, tooltip="Subject similarity strength. Kling only."),
            ],
            outputs=[IO.String.Output("images_json"), IO.String.Output("summary")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", scenes_json: str = "", image_model: str = "flux-pro", aspect_ratio: str = "16:9", max_scenes: int = 10, ref_image=None, ref_image_url: str = "", image_reference: str = "none", image_fidelity: float = 0.5, human_fidelity: float = 0.45):
        return await SceneImageGeneratorV3Node.execute(api_key=api_key, scenes_json=scenes_json, image_model=image_model, aspect_ratio=aspect_ratio, max_scenes=max_scenes, ref_image=ref_image, ref_image_url=ref_image_url, image_reference=image_reference, image_fidelity=image_fidelity, human_fidelity=human_fidelity)


class OptimizedVideoGeneratorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OptimizedVideoGeneratorV3Node",
            display_name="Optimized Video Generator [V3]",
            category="api node/workflow/Optimized",
            description="Optimized video generator with api_key input support.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key (connectable)."),
                IO.String.Input("images_json", multiline=True, default="", tooltip="Images JSON."),
                IO.Combo.Input("video_model", options=["kling-v2", "veo-3.1", "vidu2", "hailuo"], default="kling-v2"),
                IO.Combo.Input("duration", options=["5", "10"], default="5"),
                IO.Combo.Input("aspect_ratio", options=["16:9", "9:16", "1:1"], default="16:9"),
                IO.Combo.Input("storyboard_mode", options=["disabled", "combine_scenes"], default="disabled", tooltip="combine_scenes: merge all scenes into one Kling storyboard video."),
            ],
            outputs=[IO.String.Output("videos_json"), IO.String.Output("summary")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", images_json: str = "", video_model: str = "kling-v2", duration: str = "5", aspect_ratio: str = "16:9", storyboard_mode: str = "disabled"):
        return await SceneVideoGeneratorV3Node.execute(api_key=api_key, images_json=images_json, video_model=video_model, duration=duration, aspect_ratio=aspect_ratio, storyboard_mode=storyboard_mode)


class OptimizedAudioGeneratorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OptimizedAudioGeneratorV3Node",
            display_name="Optimized Audio Generator [V3]",
            category="api node/workflow/Optimized",
            description="Optimized audio generator with api_key input support.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key (connectable)."),
                IO.String.Input("scenes_json", multiline=True, default="", tooltip="Scenes JSON."),
                IO.Combo.Input("voice_id", options=["male-qn-qingse", "male-qn-jingying", "female-shaonv", "female-yujie", "presenter_male", "presenter_female"], default="male-qn-jingying"),
                IO.Boolean.Input("generate_music", default=True),
                IO.Int.Input("max_scenes", default=10, min=1, max=50, step=1),
            ],
            outputs=[IO.String.Output("audio_json"), IO.String.Output("summary")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", scenes_json: str = "", voice_id: str = "male-qn-jingying", generate_music: bool = True, max_scenes: int = 10):
        return await SceneAudioGeneratorV3Node.execute(api_key=api_key, scenes_json=scenes_json, voice_id=voice_id, generate_music=generate_music, max_scenes=max_scenes)


class UnlimitAIOptimizedV3Extension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        return [OptimizedNovelAnalyzerV3Node, OptimizedImageGeneratorV3Node, OptimizedVideoGeneratorV3Node, OptimizedAudioGeneratorV3Node]


async def comfy_entrypoint() -> UnlimitAIOptimizedV3Extension:
    return UnlimitAIOptimizedV3Extension()
