"""Provider wrapper: Deepgram STT (PipeCat 1.1.0+).

El transport envia PCM16 (linear16) 8kHz directamente desde AudioSocket (/c(slin)).
Deepgram recibe linear16 8kHz nativamente sin conversion μ-law intermedia.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..config.models import DeepgramProviderCfg, AudioProfileCfg

try:
    from pipecat.services.deepgram.stt import DeepgramSTTService
    _PIPECAT = True
except ImportError:
    _PIPECAT = False

    class DeepgramSTTService:  # type: ignore[no-redef]
        def __init__(self, **kw): self._kw = kw
        def link(self, n): pass


def build_service(resolved: "DeepgramProviderCfg", audio_profile: "AudioProfileCfg", *, keyterms: list[str] | None = None) -> Any:
    params = dict(resolved.params)
    model = params.pop("model", None)
    language = params.pop("language", "es")

    settings_kwargs: dict[str, Any] = {"language": language}
    if model:
        settings_kwargs["model"] = model
    if "endpointing" in params:
        settings_kwargs["endpointing"] = params.pop("endpointing")
    else:
        settings_kwargs["endpointing"] = 100
    if keyterms:
        settings_kwargs["keyterm"] = keyterms

    extra: dict[str, Any] = {}
    known = {"model", "language", "endpointing", "keyterm"}
    for key, value in params.items():
        if key not in known:
            extra[key] = value
    if extra:
        settings_kwargs["extra"] = extra

    return DeepgramSTTService(
        api_key=resolved.api_key,
        should_interrupt=False,
        sample_rate=audio_profile.in_rate,
        settings=DeepgramSTTService.Settings(**settings_kwargs),
    )
