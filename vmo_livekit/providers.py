"""Provider factory — creates LiveKit-compatible STT, LLM, TTS services.

LiveKit Agents expects services implementing their protocol interfaces.
We wrap pipecat-style providers.
"""

from livekit.agents import stt, llm, tts
from livekit.plugins import deepgram, elevenlabs, openai

from .config import (
    STT_API_KEY, STT_MODEL, STT_LANGUAGE,
    LLM_API_KEY, LLM_MODEL, LLM_TEMPERATURE,
    TTS_API_KEY, TTS_VOICE_ID, TTS_MODEL,
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
    """OpenAI LLM — GPT-4o-mini, Spanish."""
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
