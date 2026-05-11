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
from ..apis.minimax import MinimaxTTSRequest, MinimaxTTSResponse, MinimaxTTSAsyncSubmitResponse, MinimaxTTSAsyncPollResponse, minimax_tts_status_extractor, MinimaxVoiceCloneRequest, MinimaxVoiceCloneResponse
from ..apis.openai import OpenAITTSRequest, OpenAIWhisperResponse
from ..apis.kling import (
    KLING_TEXT_TO_AUDIO,
    KLING_TEXT_TO_AUDIO_POLL,
    KLING_VIDEO_TO_AUDIO,
    KLING_VIDEO_TO_AUDIO_POLL,
    KLING_TTS,
    KLING_CUSTOM_VOICES,
    KLING_CUSTOM_VOICES_POLL,
    KLING_PRESETS_VOICES,
    KlingTextToAudioRequest,
    KlingVideoToAudioRequest,
    KlingTTSRequest,
    KlingCustomVoiceRequest,
    KlingSubmitResponse,
    KlingPollResponse,
    kling_status_extractor,
)


async def _kling_submit_poll_audio(cls, submit_path: str, poll_path: str,
                                    request, api_key: str,
                                    wait_label: str = "Submitting",
                                    poll_interval: float = 3.0,
                                    max_poll_attempts: int = 60,
                                    estimated_duration: int = 30) -> tuple:
    submit: KlingSubmitResponse = await sync_op(
        cls, endpoint=ApiEndpoint(path=submit_path, method="POST"),
        data=request, response_model=KlingSubmitResponse, api_key=api_key,
        wait_label=wait_label, estimated_duration=5,
    )
    task_id = submit.data.task_id
    if not task_id:
        raise Exception(f"Kling audio submit failed: {submit}")
    poll_response: KlingPollResponse = await poll_op(
        cls, poll_endpoint=ApiEndpoint(path=poll_path.format(task_id), method="GET"),
        response_model=KlingPollResponse, status_extractor=kling_status_extractor,
        api_key=api_key, completed_statuses=["succeed"], failed_statuses=["failed"],
        queued_statuses=["submitted", "processing"], poll_interval=poll_interval,
        max_poll_attempts=max_poll_attempts, estimated_duration=estimated_duration,
    )
    audio_url = ""
    if poll_response.data and poll_response.data.task_result and poll_response.data.task_result.audio:
        first = poll_response.data.task_result.audio[0]
        if first is not None:
            audio_url = first.get("url", "") if isinstance(first, dict) else getattr(first, "url", "")
    if not audio_url:
        raise Exception("Kling audio task completed but no audio URL found.")
    audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
    audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
    return audio_input, task_id


class MinimaxTTSV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="MinimaxTTSV3Node",
            display_name="Minimax TTS [V3]",
            category="api node/audio/TTS",
            description="Minimax TTS via UnlimitAI — best for Chinese voice synthesis.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("text", multiline=True, default="", tooltip="Text to synthesize."),
                IO.Combo.Input("model", options=["speech-01-turbo", "speech-01-hd"], default="speech-01-turbo"),
                IO.Combo.Input("voice", options=["male-qn-qingse", "male-qn-jingying", "female-shaonv", "female-yujie", "presenter_male", "presenter_female", "audiobook_male_1", "audiobook_male_2"], default="male-qn-jingying"),
                IO.Combo.Input("emotion", options=["neutral", "happy", "sad", "angry", "fearful", "surprised"], default="neutral"),
                IO.Float.Input("speed", default=1.0, min=0.5, max=2.0, step=0.1),
                IO.Combo.Input("format", options=["mp3", "wav", "pcm"], default="mp3"),
                IO.Combo.Input("sample_rate", options=[16000, 24000, 32000], default=32000),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("audio_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", text: str = "", model: str = "speech-01-turbo", voice: str = "male-qn-jingying", emotion: str = "neutral", speed: float = 1.0, format: str = "mp3", sample_rate: int = 32000):
        validate_string(text, field_name="text")
        key = validate_api_key(api_key)
        request = MinimaxTTSRequest(model=model, text=text, voice=voice, emotion=emotion, speed=speed, format=format, sample_rate=sample_rate)
        response: MinimaxTTSResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/audio/speech", method="POST"), data=request, response_model=MinimaxTTSResponse, api_key=key, wait_label="Synthesizing speech", estimated_duration=10)
        audio_url = response.audio_url
        if not audio_url:
            raise Exception("Minimax TTS returned no audio URL.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
        return IO.NodeOutput(audio_input, audio_url)


class MinimaxTTSAsyncV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="MinimaxTTSAsyncV3Node",
            display_name="Minimax TTS Async [V3]",
            category="api node/audio/TTS",
            description="Minimax async TTS via UnlimitAI — polling based.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("text", multiline=True, default="", tooltip="Text to synthesize."),
                IO.Combo.Input("model", options=["speech-01-turbo", "speech-01-hd"], default="speech-01-turbo"),
                IO.Combo.Input("voice", options=["male-qn-qingse", "male-qn-jingying", "female-shaonv", "female-yujie", "presenter_male", "presenter_female", "audiobook_male_1", "audiobook_male_2"], default="male-qn-jingying"),
                IO.Combo.Input("emotion", options=["neutral", "happy", "sad", "angry", "fearful", "surprised"], default="neutral"),
                IO.Float.Input("speed", default=1.0, min=0.5, max=2.0, step=0.1),
                IO.Combo.Input("audio_format", options=["mp3", "wav", "pcm"], default="mp3"),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("audio_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", text: str = "", model: str = "speech-01-turbo", voice: str = "male-qn-jingying", emotion: str = "neutral", speed: float = 1.0, audio_format: str = "mp3"):
        validate_string(text, field_name="text")
        key = validate_api_key(api_key)
        submit: MinimaxTTSAsyncSubmitResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/audio/speech_async_v2", method="POST"), data={"text": text, "voice": voice, "model": model, "emotion": emotion, "speed": speed, "format": audio_format}, response_model=MinimaxTTSAsyncSubmitResponse, api_key=key, wait_label="Submitting", estimated_duration=5)
        task_id = submit.task_id
        if not task_id:
            raise Exception(f"Minimax async TTS submit failed: {submit}")
        result: MinimaxTTSAsyncPollResponse = await poll_op(cls, poll_endpoint=ApiEndpoint(path=f"/v1/audio/speech_async_v2/{task_id}", method="GET"), response_model=MinimaxTTSAsyncPollResponse, status_extractor=minimax_tts_status_extractor, api_key=key, completed_statuses=["completed", "Completed", "succeeded"], failed_statuses=["failed", "error"], queued_statuses=["queued", "processing", "created"], poll_interval=3.0, max_poll_attempts=60, estimated_duration=30)
        audio_url = result.audio_url or ""
        if not audio_url:
            raise Exception("Minimax async TTS completed but no audio URL found.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
        return IO.NodeOutput(audio_input, audio_url)


class MinimaxVoiceCloneV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="MinimaxVoiceCloneV3Node",
            display_name="Minimax Voice Clone [V3]",
            category="api node/audio/VoiceClone",
            description="Minimax voice cloning via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("voice_name", default="", multiline=False, tooltip="Name for the cloned voice."),
                IO.String.Input("audio_url", default="", multiline=False, tooltip="URL of the audio sample to clone."),
                IO.String.Input("description", default="", multiline=True, optional=True, tooltip="Optional description of the voice."),
            ],
            outputs=[IO.String.Output("voice_id"), IO.String.Output("voice_name")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", voice_name: str = "", audio_url: str = "", description: str = ""):
        validate_string(voice_name, field_name="voice_name")
        key = validate_api_key(api_key)
        request = MinimaxVoiceCloneRequest(voice_name=voice_name, audio_url=audio_url or None, description=description or None)
        response: MinimaxVoiceCloneResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/voice_clone", method="POST"), data=request, response_model=MinimaxVoiceCloneResponse, api_key=key, wait_label="Cloning voice", estimated_duration=15)
        return IO.NodeOutput(response.voice_id, response.voice_name)


class OpenAITTSV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OpenAITTSV3Node",
            display_name="OpenAI TTS [V3]",
            category="api node/audio/TTS",
            description="OpenAI TTS via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("text", multiline=True, default="", tooltip="Text to synthesize."),
                IO.Combo.Input("model", options=["tts-1", "tts-1-hd"], default="tts-1"),
                IO.Combo.Input("voice", options=["alloy", "echo", "fable", "onyx", "nova", "shimmer"], default="alloy"),
                IO.Float.Input("speed", default=1.0, min=0.25, max=4.0, step=0.25),
                IO.Combo.Input("response_format", options=["mp3", "opus", "aac", "flac", "wav"], default="mp3"),
            ],
            outputs=[IO.Audio.Output("audio")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", text: str = "", model: str = "tts-1", voice: str = "alloy", speed: float = 1.0, response_format: str = "mp3"):
        validate_string(text, field_name="text")
        key = validate_api_key(api_key)
        request = OpenAITTSRequest(model=model, input=text, voice=voice, response_format=response_format, speed=speed)
        audio_bytes = await sync_op_raw(cls, endpoint=ApiEndpoint(path="/v1/audio/speech", method="POST"), data=request, api_key=key, as_binary=True, wait_label="Synthesizing speech", estimated_duration=10)
        if not isinstance(audio_bytes, bytes):
            raise Exception("OpenAI TTS returned non-binary response.")
        audio_input = audio_bytes_to_audio_input(audio_bytes)
        return IO.NodeOutput(audio_input)


class OpenAIWhisperV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OpenAIWhisperV3Node",
            display_name="OpenAI Whisper [V3]",
            category="api node/audio/STT",
            description="OpenAI Whisper speech-to-text via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("audio_url", default="", multiline=False, tooltip="URL of the audio file to transcribe."),
                IO.String.Input("language", default="", multiline=False, optional=True, tooltip="Optional language code (e.g. 'en', 'zh')."),
            ],
            outputs=[IO.String.Output("text"), IO.String.Output("language"), IO.Float.Output("duration")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", audio_url: str = "", language: str = ""):
        validate_string(audio_url, field_name="audio_url")
        key = validate_api_key(api_key)
        response: OpenAIWhisperResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/audio/transcriptions", method="POST"), data={"url": audio_url, "model": "whisper-1", "language": language or None, "response_format": "verbose_json"}, response_model=OpenAIWhisperResponse, api_key=key, wait_label="Transcribing", estimated_duration=15)
        return IO.NodeOutput(response.text, response.language or "", response.duration or 0.0)


class KlingAudioGenV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingAudioGenV3Node",
            display_name="Kling Audio Gen [V3]",
            category="api node/audio/Kling",
            description="Kling text-to-audio generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("prompt", multiline=True, default="", tooltip="Text prompt for audio generation."),
                IO.String.Input("duration", default="5", multiline=False, tooltip="Duration in seconds (3.0-10.0)."),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", prompt: str = "", duration: str = "5"):
        validate_string(prompt, field_name="prompt")
        key = validate_api_key(api_key)
        request = KlingTextToAudioRequest(prompt=prompt, duration=duration)
        audio_input, task_id = await _kling_submit_poll_audio(
            cls, KLING_TEXT_TO_AUDIO, KLING_TEXT_TO_AUDIO_POLL, request, key)
        return IO.NodeOutput(audio_input, task_id)


class KlingVideoToAudioV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingVideoToAudioV3Node",
            display_name="Kling Video to Audio [V3]",
            category="api node/audio/Kling",
            description="Kling video-to-audio generation via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("video_url", default="", multiline=False, tooltip="Video URL (3-20 seconds)."),
                IO.String.Input("sound_effect_prompt", default="", multiline=True, optional=True, tooltip="Sound effect prompt."),
                IO.String.Input("bgm_prompt", default="", multiline=True, optional=True, tooltip="Background music prompt."),
                IO.Boolean.Input("asmr_mode", default=False, tooltip="Enable ASMR mode."),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", video_url: str = "", sound_effect_prompt: str = "", bgm_prompt: str = "", asmr_mode: bool = False):
        validate_string(video_url, field_name="video_url")
        key = validate_api_key(api_key)
        request = KlingVideoToAudioRequest(video_url=video_url, sound_effect_prompt=sound_effect_prompt or None, bgm_prompt=bgm_prompt or None, asmr_mode=asmr_mode)
        audio_input, task_id = await _kling_submit_poll_audio(
            cls, KLING_VIDEO_TO_AUDIO, KLING_VIDEO_TO_AUDIO_POLL, request, key)
        return IO.NodeOutput(audio_input, task_id)


class KlingTTSV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingTTSV3Node",
            display_name="Kling TTS [V3]",
            category="api node/audio/Kling",
            description="Kling text-to-speech via UnlimitAI.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("text", multiline=True, default="", tooltip="Text to synthesize (max 1000 chars)."),
                IO.String.Input("voice_id", default="", multiline=False, tooltip="Voice ID from Kling presets."),
                IO.Combo.Input("voice_language", options=["zh", "en"], default="zh"),
                IO.Float.Input("voice_speed", default=1.0, min=0.8, max=2.0, step=0.1),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("audio_url")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", text: str = "", voice_id: str = "", voice_language: str = "zh", voice_speed: float = 1.0):
        validate_string(text, field_name="text")
        validate_string(voice_id, field_name="voice_id")
        key = validate_api_key(api_key)
        request = KlingTTSRequest(text=text, voice_id=voice_id, voice_language=voice_language, voice_speed=voice_speed)
        response_dict = await sync_op_raw(cls, endpoint=ApiEndpoint(path=KLING_TTS, method="POST"), data=request, api_key=key, wait_label="Synthesizing speech", estimated_duration=10)
        audio_url = ""
        if isinstance(response_dict, dict):
            data = response_dict.get("data", {})
            if isinstance(data, dict):
                audio_url = data.get("url", "")
                if not audio_url:
                    task_result = data.get("task_result", {})
                    if isinstance(task_result, dict):
                        audios = task_result.get("audio", [])
                        if audios and isinstance(audios[0], dict):
                            audio_url = audios[0].get("url", "")
        if not audio_url:
            raise Exception("Kling TTS returned no audio URL.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
        return IO.NodeOutput(audio_input, audio_url)


class KlingCustomVoiceV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingCustomVoiceV3Node",
            display_name="Kling Custom Voice [V3]",
            category="api node/audio/Kling",
            description="Create a custom voice via UnlimitAI Kling. Returns a voice_id for use with Kling TTS or Lip Sync.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("voice_name", default="", multiline=False, tooltip="Name for the custom voice."),
                IO.String.Input("voice_url", default="", multiline=False, tooltip="URL of the audio sample (mp3/wav/m4a/aac, max 5MB, 10-60s)."),
            ],
            outputs=[IO.String.Output("voice_id"), IO.String.Output("task_id")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", voice_name: str = "", voice_url: str = ""):
        validate_string(voice_name, field_name="voice_name")
        validate_string(voice_url, field_name="voice_url")
        key = validate_api_key(api_key)
        request = KlingCustomVoiceRequest(voice_name=voice_name, voice_url=voice_url)
        submit: KlingSubmitResponse = await sync_op(
            cls, endpoint=ApiEndpoint(path=KLING_CUSTOM_VOICES, method="POST"),
            data=request, response_model=KlingSubmitResponse, api_key=key,
            wait_label="Creating voice", estimated_duration=5,
        )
        task_id = submit.data.task_id
        if not task_id:
            raise Exception(f"Kling custom voice submit failed: {submit}")
        poll_response: KlingPollResponse = await poll_op(
            cls, poll_endpoint=ApiEndpoint(path=KLING_CUSTOM_VOICES_POLL.format(task_id), method="GET"),
            response_model=KlingPollResponse, status_extractor=kling_status_extractor,
            api_key=key, completed_statuses=["succeed"], failed_statuses=["failed"],
            queued_statuses=["submitted", "processing"], poll_interval=5.0,
            max_poll_attempts=60, estimated_duration=60,
        )
        voice_id = ""
        if poll_response.data and poll_response.data.task_result:
            audio = poll_response.data.task_result.audio
            if audio and isinstance(audio, list) and len(audio) > 0:
                first = audio[0]
                voice_id = first.get("id", "") if isinstance(first, dict) else getattr(first, "id", "")
        if not voice_id:
            raise Exception("Kling custom voice task completed but no voice ID found.")
        return IO.NodeOutput(voice_id, task_id)


class KlingPresetVoicesV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="KlingPresetVoicesV3Node",
            display_name="Kling Preset Voices [V3]",
            category="api node/audio/Kling",
            description="List all available Kling preset voices. Useful for finding voice_id for TTS or Lip Sync.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
            ],
            outputs=[IO.String.Output("voices_json")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = ""):
        key = validate_api_key(api_key)
        response = await sync_op_raw(
            cls, endpoint=ApiEndpoint(path=KLING_PRESETS_VOICES, method="GET"),
            api_key=key, wait_label="Fetching voices", estimated_duration=5,
        )
        import json
        voices_json = json.dumps(response, ensure_ascii=False, indent=2) if isinstance(response, (dict, list)) else str(response)
        return IO.NodeOutput(voices_json)


class DialogueGeneratorV3Node(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="DialogueGeneratorV3Node",
            display_name="Dialogue Generator [V3]",
            category="api node/audio/Drama",
            description="Generate dialogue audio via Minimax TTS.",
            inputs=[
                IO.String.Input("api_key", default="", multiline=False, tooltip="UnlimitAI API key."),
                IO.String.Input("text", multiline=True, default="", tooltip="Dialogue text."),
                IO.Combo.Input("voice", options=["male-qn-jingying", "female-shaonv", "female-yujie"], default="male-qn-jingying"),
                IO.Combo.Input("emotion", options=["neutral", "happy", "sad", "angry"], default="neutral"),
            ],
            outputs=[IO.Audio.Output("audio"), IO.String.Output("audio_url"), IO.Int.Output("characters")],
            hidden=[IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, api_key: str = "", text: str = "", voice: str = "male-qn-jingying", emotion: str = "neutral"):
        validate_string(text, field_name="text")
        key = validate_api_key(api_key)
        request = MinimaxTTSRequest(model="speech-01-turbo", text=text, voice=voice, emotion=emotion)
        response: MinimaxTTSResponse = await sync_op(cls, endpoint=ApiEndpoint(path="/v1/audio/speech", method="POST"), data=request, response_model=MinimaxTTSResponse, api_key=key, wait_label="Synthesizing dialogue", estimated_duration=10)
        audio_url = response.audio_url
        if not audio_url:
            raise Exception("Dialogue TTS returned no audio URL.")
        audio_bytesio = await download_url_as_bytesio(audio_url, cls=cls)
        audio_input = audio_bytes_to_audio_input(audio_bytesio.getvalue())
        return IO.NodeOutput(audio_input, audio_url, len(text))


class UnlimitAIAudioV3Extension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[IO.ComfyNode]]:
        return [
            MinimaxTTSV3Node, MinimaxTTSAsyncV3Node, MinimaxVoiceCloneV3Node,
            OpenAITTSV3Node, OpenAIWhisperV3Node,
            KlingAudioGenV3Node, KlingVideoToAudioV3Node, KlingTTSV3Node,
            KlingCustomVoiceV3Node, KlingPresetVoicesV3Node,
            DialogueGeneratorV3Node,
        ]


async def comfy_entrypoint() -> UnlimitAIAudioV3Extension:
    return UnlimitAIAudioV3Extension()
