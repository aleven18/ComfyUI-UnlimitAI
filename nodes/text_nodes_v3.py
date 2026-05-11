from typing_extensions import override

from comfy_api.latest import IO, ComfyExtension

from ..unlimitai_util import (
    ApiEndpoint,
    sync_op,
    validate_api_key,
    validate_string,
)
from ..apis.text import TextGenerationRequest, TextGenerationResponse, ChatMessage, extract_text_content
from .config_nodes_v3 import PRICING


def _calc_cost(model: str, pt: int, ct: int) -> float:
    rates = PRICING.get(model, {'input': 0.0, 'output': 0.0})
    return (pt / 1000 * rates['input']) + (ct / 1000 * rates['output'])



class UnlimitAITextV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="UnlimitAITextV3Node",
            display_name="Text Generation [V3]",
            category="api node/text",
            description="LLM text generation via UnlimitAI (GPT-4, Claude, DeepSeek, etc.).",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt."),
                IO.Combo.Input("model", options=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "claude-3-5-sonnet-20241022", "deepseek-chat", "deepseek-reasoner"], default="gpt-4o"),
                IO.Float.Input("temperature", default=0.7, min=0.0, max=2.0, step=0.1),
                IO.Int.Input("max_tokens", default=4096, min=1, max=128000, step=1),
            ],
            outputs=[IO.String.Output("text"), IO.Int.Output("prompt_tokens"), IO.Int.Output("completion_tokens"), IO.Float.Output("cost")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", model: str = "gpt-4o", temperature: float = 0.7, max_tokens: int = 4096):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = TextGenerationRequest(model=model, messages=[ChatMessage(role="user", content=prompt)], temperature=temperature, max_tokens=max_tokens)
        response: TextGenerationResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"), data=request, response_model=TextGenerationResponse, api_key=key, wait_label="Generating text", estimated_duration=10)
        text = extract_text_content(response.choices[0].message.content) if response.choices else ""
        pt = response.usage.prompt_tokens
        ct = response.usage.completion_tokens
        return IO.NodeOutput(text, pt, ct, _calc_cost(model, pt, ct))


class GPT5ReasoningV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="GPT5ReasoningV3Node",
            display_name="GPT-5 Reasoning [V3]",
            category="api node/text",
            description="GPT-5 reasoning via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Reasoning prompt."),
                IO.Float.Input("temperature", default=0.7, min=0.0, max=2.0, step=0.1),
                IO.Int.Input("max_tokens", default=4096, min=1, max=128000, step=1),
            ],
            outputs=[IO.String.Output("text"), IO.String.Output("reasoning"), IO.Int.Output("prompt_tokens"), IO.Int.Output("completion_tokens"), IO.Float.Output("cost")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", temperature: float = 0.7, max_tokens: int = 4096):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = TextGenerationRequest(model="gpt-5", messages=[ChatMessage(role="user", content=prompt)], temperature=temperature, max_tokens=max_tokens)
        response: TextGenerationResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"), data=request, response_model=TextGenerationResponse, api_key=key, wait_label="Reasoning", estimated_duration=30)
        text = extract_text_content(response.choices[0].message.content) if response.choices else ""
        reasoning = ""
        if response.choices and response.choices[0].message:
            msg = response.choices[0].message
            reasoning = msg.reasoning_content or ""
            if not reasoning:
                raw = msg.model_dump() if hasattr(msg, "model_dump") else {}
                reasoning = raw.get("reasoning_content", "") or ""
        pt = response.usage.prompt_tokens
        ct = response.usage.completion_tokens
        return IO.NodeOutput(text, reasoning, pt, ct, _calc_cost("gpt-5", pt, ct))


class DeepSeekThinkingV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="DeepSeekThinkingV3Node",
            display_name="DeepSeek Thinking [V3]",
            category="api node/text",
            description="DeepSeek reasoner thinking via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Reasoning prompt."),
                IO.Float.Input("temperature", default=0.7, min=0.0, max=2.0, step=0.1),
                IO.Int.Input("max_tokens", default=4096, min=1, max=128000, step=1),
            ],
            outputs=[IO.String.Output("text"), IO.String.Output("reasoning"), IO.Int.Output("prompt_tokens"), IO.Int.Output("completion_tokens"), IO.Float.Output("cost")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", temperature: float = 0.7, max_tokens: int = 4096):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = TextGenerationRequest(model="deepseek-reasoner", messages=[ChatMessage(role="user", content=prompt)], temperature=temperature, max_tokens=max_tokens)
        response: TextGenerationResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"), data=request, response_model=TextGenerationResponse, api_key=key, wait_label="Thinking", estimated_duration=30)
        text = extract_text_content(response.choices[0].message.content) if response.choices else ""
        reasoning = ""
        if response.choices:
            msg = response.choices[0].message
            reasoning = msg.reasoning_content or ""
            if not reasoning:
                raw = msg.model_dump() if hasattr(msg, "model_dump") else {}
                reasoning = raw.get("reasoning_content", "") or ""
        pt = response.usage.prompt_tokens
        ct = response.usage.completion_tokens
        return IO.NodeOutput(text, reasoning, pt, ct, _calc_cost("deepseek-reasoner", pt, ct))


class StructuredOutputV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="StructuredOutputV3Node",
            display_name="Structured Output [V3]",
            category="api node/text",
            description="LLM structured JSON output via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Prompt."),
                IO.String.Input("json_schema", multiline=True, default="", tooltip="JSON schema for structured output."),
                IO.Combo.Input("model", options=["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022"], default="gpt-4o"),
                IO.Float.Input("temperature", default=0.3, min=0.0, max=2.0, step=0.1),
            ],
            outputs=[IO.String.Output("text"), IO.String.Output("json_output"), IO.Int.Output("prompt_tokens"), IO.Int.Output("completion_tokens"), IO.Float.Output("cost")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", json_schema: str = "", model: str = "gpt-4o", temperature: float = 0.3):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        import json
        schema_dict = None
        if json_schema.strip():
            try:
                schema_dict = json.loads(json_schema)
            except json.JSONDecodeError:
                schema_dict = None
        response_format = {"type": "json_schema", "json_schema": {"name": "structured_output", "schema": schema_dict}} if schema_dict else {"type": "json_object"}
        request = TextGenerationRequest(model=model, messages=[ChatMessage(role="user", content=prompt)], temperature=temperature, response_format=response_format)
        response: TextGenerationResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"), data=request, response_model=TextGenerationResponse, api_key=key, wait_label="Generating structured output", estimated_duration=10)
        text = extract_text_content(response.choices[0].message.content) if response.choices else ""
        json_output = text
        pt = response.usage.prompt_tokens
        ct = response.usage.completion_tokens
        return IO.NodeOutput(text, json_output, pt, ct, _calc_cost(model, pt, ct))


class NovelAnalyzerV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="NovelAnalyzerV3Node",
            display_name="Novel Analyzer [V3]",
            category="api node/text/Novel",
            description="Analyze novel text and extract scenes via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("novel_text", multiline=True, default="", tooltip="Novel text to analyze."),
                IO.Combo.Input("model", options=["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022", "deepseek-chat"], default="gpt-4o"),
            ],
            outputs=[IO.String.Output("analysis"), IO.String.Output("scenes_json"), IO.Int.Output("prompt_tokens"), IO.Int.Output("completion_tokens"), IO.Float.Output("cost")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", novel_text: str = "", model: str = "gpt-4o"):
        validate_string(novel_text, field_name="novel_text")
        key = validate_api_key(api_key)
        prompt = f"Analyze the following novel text and extract scenes as structured JSON:\n\n{novel_text}"
        request = TextGenerationRequest(model=model, messages=[ChatMessage(role="user", content=prompt)], temperature=0.3, response_format={"type": "json_object"})
        response: TextGenerationResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"), data=request, response_model=TextGenerationResponse, api_key=key, wait_label="Analyzing novel", estimated_duration=20)
        text = extract_text_content(response.choices[0].message.content) if response.choices else ""
        pt = response.usage.prompt_tokens
        ct = response.usage.completion_tokens
        return IO.NodeOutput(text, text, pt, ct, _calc_cost(model, pt, ct))


class SceneTranslatorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="SceneTranslatorV3Node",
            display_name="Scene Translator [V3]",
            category="api node/text/Novel",
            description="Translate scene text to a target language via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("text", multiline=True, default="", tooltip="Text to translate."),
                IO.String.Input("target_language", default="English", multiline=False, tooltip="Target language."),
                IO.Combo.Input("model", options=["gpt-4o", "gpt-4o-mini", "deepseek-chat"], default="gpt-4o"),
            ],
            outputs=[IO.String.Output("translation"), IO.Int.Output("prompt_tokens"), IO.Int.Output("completion_tokens"), IO.Float.Output("cost")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", text: str = "", target_language: str = "English", model: str = "gpt-4o"):
        validate_string(text, field_name="text")
        key = validate_api_key(api_key)
        prompt = f"Translate the following text to {target_language}:\n\n{text}"
        request = TextGenerationRequest(model=model, messages=[ChatMessage(role="user", content=prompt)], temperature=0.3)
        response: TextGenerationResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"), data=request, response_model=TextGenerationResponse, api_key=key, wait_label="Translating", estimated_duration=10)
        translation = extract_text_content(response.choices[0].message.content) if response.choices else ""
        pt = response.usage.prompt_tokens
        ct = response.usage.completion_tokens
        return IO.NodeOutput(translation, pt, ct, _calc_cost(model, pt, ct))


class VisionChatV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="VisionChatV3Node",
            display_name="Vision Chat [V3]",
            category="api node/text",
            description="Multimodal LLM chat with image understanding (GPT-4o, Claude). Send images for visual analysis.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt / question about the images."),
                IO.String.Input("image_urls", multiline=True, default="", tooltip="Image URLs, one per line. Sent alongside the text prompt for visual analysis."),
                IO.Combo.Input("model", options=["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022"], default="gpt-4o", tooltip="Vision-capable model required."),
                IO.Float.Input("temperature", default=0.7, min=0.0, max=2.0, step=0.1),
                IO.Int.Input("max_tokens", default=4096, min=1, max=128000, step=1),
            ],
            outputs=[IO.String.Output("text"), IO.Int.Output("prompt_tokens"), IO.Int.Output("completion_tokens"), IO.Float.Output("cost")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", image_urls: str = "", model: str = "gpt-4o", temperature: float = 0.7, max_tokens: int = 4096):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        urls = [u.strip() for u in image_urls.strip().split("\n") if u.strip()]
        if urls:
            content_parts: list[dict] = [{"type": "text", "text": prompt}]
            for url in urls:
                content_parts.append({"type": "image_url", "image_url": {"url": url}})
            messages = [ChatMessage(role="user", content=content_parts)]
        else:
            messages = [ChatMessage(role="user", content=prompt)]
        request = TextGenerationRequest(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
        response: TextGenerationResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/chat/completions", method="POST"), data=request, response_model=TextGenerationResponse, api_key=key, wait_label="Analyzing images", estimated_duration=15)
        text = extract_text_content(response.choices[0].message.content) if response.choices else ""
        if isinstance(text, list):
            text = " ".join(part.get("text", "") for part in text if isinstance(part, dict) and part.get("type") == "text")
        pt = response.usage.prompt_tokens
        ct = response.usage.completion_tokens
        return IO.NodeOutput(text, pt, ct, _calc_cost(model, pt, ct))


class UnlimitAITextV3Extension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        return [
            UnlimitAITextV3Node, GPT5ReasoningV3Node, DeepSeekThinkingV3Node,
            StructuredOutputV3Node, NovelAnalyzerV3Node, SceneTranslatorV3Node,
            VisionChatV3Node,
        ]


async def comfy_entrypoint() -> UnlimitAITextV3Extension:
    return UnlimitAITextV3Extension()
