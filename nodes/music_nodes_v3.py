from typing_extensions import override

from comfy_api.latest import IO, ComfyExtension

from ..unlimitai_util import (
    ApiEndpoint,
    download_url_as_bytesio,
    poll_op,
    sync_op,
    sync_op_raw,
    validate_api_key,
    validate_string,
)
from ..unlimitai_util.conversions import audio_bytes_to_audio_input
from ..apis.suno import (
    SunoInspirationRequest, SunoCustomModeRequest, SunoLyricsRequest,
    SunoExtendRequest, SunoSubmitResponse, SunoPollResponse,
    suno_status_extractor,
)


class SunoInspirationV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="SunoInspirationV3Node",
            display_name="Suno Inspiration [V3]",
            category="api node/music/Suno",
            description="Suno inspiration mode music generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Music description."),
                IO.String.Input("tags", default="", multiline=False, tooltip="Genre/style tags."),
                IO.String.Input("title", default="", multiline=False, tooltip="Song title."),
                IO.Boolean.Input("make_instrumental", default=False, tooltip="Instrumental only."),
                IO.Combo.Input("model", options=["chirp-v3-5", "chirp-v4-5", "chirp-v5"], default="chirp-v3-5"),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("audio_url"), IO.String.Output("title"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", tags: str = "", title: str = "", make_instrumental: bool = False, model: str = "chirp-v3-5"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        version = model.replace("chirp-", "")
        endpoint_path = f"/suno/{version}/generate" if version != "v3-5" else "/suno/v3/generate"
        request = SunoInspirationRequest(prompt=prompt, tags=tags, title=title, make_instrumental=make_instrumental, model=model, mv=model)
        submit: SunoSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path=endpoint_path, method="POST"), data=request, response_model=SunoSubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        task_id = submit.clips[0].id if submit.clips else ""
        if not task_id:
            raise Exception(f"Suno submit failed: no clip id. Response: {submit}")
        result: SunoPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=f"{endpoint_path}/{task_id}", method="GET"), response_model=SunoPollResponse, status_extractor=suno_status_extractor, api_key=key, completed_statuses=["complete", "completed", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "submitted", "generating"], poll_interval=10.0, max_poll_attempts=120, estimated_duration=60)
        clip = result.clips[0] if result.clips else None
        audio_url = clip.audio_url if clip else ""
        clip_title = clip.title if clip else ""
        image_url = clip.image_url if clip else ""
        if not audio_url:
            raise Exception("Suno task completed but no audio URL found.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
        return IO.NodeOutput(audio_input, audio_url, clip_title, image_url)


class SunoCustomModeV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="SunoCustomModeV3Node",
            display_name="Suno Custom [V3]",
            category="api node/music/Suno",
            description="Suno custom mode music generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Music description."),
                IO.String.Input("lyrics", multiline=True, default="", tooltip="Custom lyrics."),
                IO.String.Input("tags", default="", multiline=False, tooltip="Genre/style tags."),
                IO.String.Input("title", default="", multiline=False, tooltip="Song title."),
                IO.Boolean.Input("make_instrumental", default=False),
                IO.Combo.Input("model", options=["chirp-v3-5", "chirp-v4-5", "chirp-v5"], default="chirp-v3-5"),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("audio_url"), IO.String.Output("title"), IO.String.Output("image_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", lyrics: str = "", tags: str = "", title: str = "", make_instrumental: bool = False, model: str = "chirp-v3-5"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        version = model.replace("chirp-", "")
        endpoint_path = f"/suno/{version}/generate" if version != "v3-5" else "/suno/v3/generate"
        request = SunoCustomModeRequest(prompt=prompt, lyrics=lyrics, tags=tags, title=title, make_instrumental=make_instrumental, model=model, mv=model)
        submit: SunoSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path=endpoint_path, method="POST"), data=request, response_model=SunoSubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        task_id = submit.clips[0].id if submit.clips else ""
        if not task_id:
            raise Exception(f"Suno submit failed: no clip id. Response: {submit}")
        result: SunoPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=f"{endpoint_path}/{task_id}", method="GET"), response_model=SunoPollResponse, status_extractor=suno_status_extractor, api_key=key, completed_statuses=["complete", "completed", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "submitted", "generating"], poll_interval=10.0, max_poll_attempts=120, estimated_duration=60)
        clip = result.clips[0] if result.clips else None
        audio_url = clip.audio_url if clip else ""
        clip_title = clip.title if clip else ""
        image_url = clip.image_url if clip else ""
        if not audio_url:
            raise Exception("Suno task completed but no audio URL found.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
        return IO.NodeOutput(audio_input, audio_url, clip_title, image_url)


class SunoLyricsGeneratorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="SunoLyricsGeneratorV3Node",
            display_name="Suno Lyrics Generator [V3]",
            category="api node/music/Suno",
            description="Generate lyrics via Suno.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Lyrics prompt / theme."),
            ],
            outputs=[IO.String.Output("lyrics"), IO.String.Output("title")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = ""):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = SunoLyricsRequest(prompt=prompt)
        response = await sync_op_raw(cls, endpoint=ApiEndpoint(path="/suno/v3/generate/lyrics", method="POST"), data=request, api_key=key, wait_label="Generating lyrics", estimated_duration=10)
        if isinstance(response, dict):
            lyrics = response.get("lyrics", "") or response.get("text", "")
            title = response.get("title", "")
        else:
            lyrics = str(response)
            title = ""
        return IO.NodeOutput(lyrics, title)


class SunoExtendV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="SunoExtendV3Node",
            display_name="Suno Extend [V3]",
            category="api node/music/Suno",
            description="Extend an existing Suno track via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("audio_url", default="", multiline=False, tooltip="URL of the audio to extend."),
                IO.String.Input("prompt", default="", multiline=True, tooltip="Continuation prompt."),
                IO.String.Input("tags", default="", multiline=False, tooltip="Genre/style tags."),
                IO.Float.Input("continue_at", default=0.0, min=0.0, max=300.0, step=1.0, tooltip="Timestamp in seconds to continue from."),
                IO.Combo.Input("model", options=["chirp-v3-5", "chirp-v4-5", "chirp-v5"], default="chirp-v3-5"),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("audio_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", audio_url: str = "", prompt: str = "", tags: str = "", continue_at: float = 0.0, model: str = "chirp-v3-5"):
        validate_string(audio_url, field_name="audio_url")
        key = validate_api_key(api_key)
        version = model.replace("chirp-", "")
        endpoint_path = f"/suno/{version}/extend" if version != "v3-5" else "/suno/v3/extend"
        request = SunoExtendRequest(audio_url=audio_url, prompt=prompt, tags=tags, continue_at=continue_at, model=model, mv=model)
        submit: SunoSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path=endpoint_path, method="POST"), data=request, response_model=SunoSubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        task_id = submit.clips[0].id if submit.clips else ""
        if not task_id:
            raise Exception(f"Suno extend submit failed: {submit}")
        gen_path = f"/suno/{version}/generate" if version != "v3-5" else "/suno/v3/generate"
        result: SunoPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=f"{gen_path}/{task_id}", method="GET"), response_model=SunoPollResponse, status_extractor=suno_status_extractor, api_key=key, completed_statuses=["complete", "completed", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "submitted", "generating"], poll_interval=10.0, max_poll_attempts=120, estimated_duration=60)
        clip = result.clips[0] if result.clips else None
        result_audio_url = clip.audio_url if clip else ""
        if not result_audio_url:
            raise Exception("Suno extend completed but no audio URL found.")
        audio_bytesio = await download_url_as_bytesio(result_audio_url, cls=cls)
        audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
        return IO.NodeOutput(audio_input, result_audio_url)


class BackgroundMusicV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="BackgroundMusicV3Node",
            display_name="Background Music [V3]",
            category="api node/music/Drama",
            description="Generate background music via Suno.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Music description / mood."),
                IO.String.Input("tags", default="", multiline=False, tooltip="Genre/style tags."),
                IO.String.Input("title", default="", multiline=False, tooltip="Title."),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("audio_url"), IO.String.Output("title")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", tags: str = "", title: str = ""):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = SunoInspirationRequest(prompt=prompt, tags=tags, title=title, make_instrumental=True, model="chirp-v3-5", mv="chirp-v3-5")
        submit: SunoSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/suno/v3/generate", method="POST"), data=request, response_model=SunoSubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        task_id = submit.clips[0].id if submit.clips else ""
        if not task_id:
            raise Exception(f"BGM submit failed: {submit}")
        result: SunoPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=f"/suno/v3/generate/{task_id}", method="GET"), response_model=SunoPollResponse, status_extractor=suno_status_extractor, api_key=key, completed_statuses=["complete", "completed", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "generating"], poll_interval=10.0, max_poll_attempts=120, estimated_duration=60)
        clip = result.clips[0] if result.clips else None
        audio_url = clip.audio_url if clip else ""
        clip_title = clip.title if clip else ""
        if not audio_url:
            raise Exception("BGM task completed but no audio URL found.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
        return IO.NodeOutput(audio_input, audio_url, clip_title)


class SoundtrackComposerV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="SoundtrackComposerV3Node",
            display_name="Soundtrack Composer [V3]",
            category="api node/music/Drama",
            description="Compose a soundtrack for a scene description via Suno.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("scene_description", multiline=True, default="", tooltip="Scene description to compose for."),
                IO.String.Input("mood", default="", multiline=False, tooltip="Mood / genre tags."),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("audio_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", scene_description: str = "", mood: str = ""):
        validate_string(scene_description, field_name="scene_description")
        key = validate_api_key(api_key)
        prompt = f"Soundtrack for: {scene_description}"
        if mood:
            prompt += f" Mood: {mood}"
        request = SunoInspirationRequest(prompt=prompt, tags=mood, make_instrumental=True, model="chirp-v3-5", mv="chirp-v3-5")
        submit: SunoSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/suno/v3/generate", method="POST"), data=request, response_model=SunoSubmitResponse, api_key=key, wait_label="Composing soundtrack", estimated_duration=5)
        task_id = submit.clips[0].id if submit.clips else ""
        if not task_id:
            raise Exception(f"Soundtrack submit failed: {submit}")
        result: SunoPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=f"/suno/v3/generate/{task_id}", method="GET"), response_model=SunoPollResponse, status_extractor=suno_status_extractor, api_key=key, completed_statuses=["complete", "completed", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "generating"], poll_interval=10.0, max_poll_attempts=120, estimated_duration=60)
        clip = result.clips[0] if result.clips else None
        audio_url = clip.audio_url if clip else ""
        if not audio_url:
            raise Exception("Soundtrack task completed but no audio URL found.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
        return IO.NodeOutput(audio_input, audio_url)


class UnlimitAIMusicV3Extension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        return [
            SunoInspirationV3Node, SunoCustomModeV3Node, SunoLyricsGeneratorV3Node,
            SunoExtendV3Node, BackgroundMusicV3Node, SoundtrackComposerV3Node,
        ]


async def comfy_entrypoint() -> UnlimitAIMusicV3Extension:
    return UnlimitAIMusicV3Extension()
