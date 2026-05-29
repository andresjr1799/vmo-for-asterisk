"""Provider factory — creates LiveKit-compatible STT, LLM, TTS services.

LiveKit Agents expects services implementing their protocol interfaces.
"""

from livekit.agents import stt, llm, tts
from livekit.plugins import deepgram, elevenlabs, openai

from .config import (
    STT_API_KEY, STT_MODEL, STT_LANGUAGE,
    LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_TEMPERATURE,
    TTS_API_KEY, TTS_VOICE_ID, TTS_MODEL,
    ASAP_BACKEND_URL, ASAP_BACKEND_TIMEOUT,
)


def create_stt() -> stt.STT:
    """Deepgram STT — Nova-3, Spanish, 8000Hz."""
    return deepgram.STT(
        api_key=STT_API_KEY,
        model=STT_MODEL,
        language=STT_LANGUAGE,
        sample_rate=8000,
        endpointing=100,
    )


def create_llm() -> llm.LLM:
    """LLM provider — OpenAI or ASAP backend."""
    if LLM_PROVIDER == "asap_backend" and ASAP_BACKEND_URL:
        from livekit.agents.llm import LLM
        from .asap_llm import ASAPBackendLLM
        return ASAPBackendLLM(
            base_url=ASAP_BACKEND_URL,
            timeout=ASAP_BACKEND_TIMEOUT,
        )

    return openai.LLM(
        api_key=LLM_API_KEY,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
    )


def create_tts() -> tts.TTS:
    """ElevenLabs TTS — multilingual v2, custom voice."""
    return elevenlabs.TTS(
        api_key=TTS_API_KEY,
        voice_id=TTS_VOICE_ID,
        model=TTS_MODEL,
        stability=0.5,
        similarity_boost=0.75,
    )
