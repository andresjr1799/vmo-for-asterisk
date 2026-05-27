"""Provider wrapper: ElevenLabs TTS — WebSocket (PipeCat 1.1.0+)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..config.models import ElevenLabsProviderCfg, AudioProfileCfg

try:
    from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
    _PIPECAT = True
except ImportError:
    _PIPECAT = False

    class ElevenLabsTTSService:  # type: ignore[no-redef]
        def __init__(self, **kw): self._kw = kw
        def link(self, n): pass


class _PatchedElevenLabsTTSService(ElevenLabsTTSService):
    """Sends voice_settings only on first context per WebSocket connection."""

    async def run_tts(self, text, context_id):
        try:
            async for frame in super().run_tts(text, context_id):
                yield frame
        finally:
            self._voice_settings = None

    async def _connect(self):
        self._voice_settings = self._set_voice_settings()
        await super()._connect()


def build_service(resolved: "ElevenLabsProviderCfg", audio_profile: "AudioProfileCfg") -> Any:
    params = dict(resolved.params)
    voice_id = params.pop("voice_id", "")
    model = params.pop("model_id", None) or params.pop("model", "eleven_multilingual_v2")
    speed = params.pop("speed", 1.0)
    stability = params.pop("stability", 0.5)
    similarity_boost = params.pop("similarity_boost", 0.75)

    settings_kwargs: dict[str, Any] = {
        "voice": voice_id,
        "model": model,
        "stability": float(stability),
        "similarity_boost": float(similarity_boost),
    }
    if speed is not None:
        settings_kwargs["speed"] = float(speed)

    return _PatchedElevenLabsTTSService(
        api_key=resolved.api_key,
        sample_rate=audio_profile.out_rate,
        reconnect_on_error=False,
        settings=ElevenLabsTTSService.Settings(**settings_kwargs),
    )
