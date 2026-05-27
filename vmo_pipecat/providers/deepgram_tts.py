"""Provider wrapper: Deepgram TTS → pipecat.services.deepgram.tts.DeepgramTTSService."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..config.models import DeepgramProviderCfg, AudioProfileCfg

try:
    from pipecat.services.deepgram.tts import DeepgramTTSService
    _PIPECAT = True
except ImportError:
    _PIPECAT = False

    class DeepgramTTSService:  # type: ignore[no-redef]
        """Stub when pipecat-ai is not installed."""
        def __init__(self, **kw): self._kw = kw

try:
    from pipecat.utils.text.xml_function_tag_filter import XMLFunctionTagFilter
except ImportError:
    XMLFunctionTagFilter = None


def build_service(resolved: "DeepgramProviderCfg", audio_profile: "AudioProfileCfg") -> Any:
    params = dict(resolved.params)
    if "model" in params and "voice" not in params:
        params["voice"] = params.pop("model")
    params.pop("language", None)
    return DeepgramTTSService(
        api_key=resolved.api_key,
        sample_rate=audio_profile.out_rate,
        text_filters=[XMLFunctionTagFilter()] if XMLFunctionTagFilter else [],
        silence_time_s=1.0,
        **params,
    )
