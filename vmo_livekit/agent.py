"""VoicePipelineAgent — LiveKit-native voice AI pipeline.

STT → LLM → TTS with built-in VAD and interruption handling.
No custom transport, metrics processors, or lifecycle management needed.
"""

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent

from .config import SYSTEM_PROMPT, GREETING, LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
from .providers import create_stt, create_llm, create_tts
from .sip_handler import SessionContext
from .metrics import get_tracer, get_logger, _calls_total, _calls_active

logger = get_logger(__name__)


async def entrypoint(ctx: JobContext):
    """LiveKit worker entrypoint — one per SIP/WebRTC call."""
    logger.info("VMO job received", room=ctx.room.name)

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    if participant is None:
        logger.error("No participant joined")
        return

    headers = participant.attributes or {}
    session = SessionContext.from_sip_headers(headers)

    logger.info("Session started", **session.asdict())

    if _calls_total:
        _calls_total.add(1, {"tenant_id": session.tenant_id})
    if _calls_active:
        _calls_active.add(1, {"tenant_id": session.tenant_id})

    tracer = get_tracer()

    with tracer.start_as_current_span("vmo.call") as span:
        span.set_attributes(session.asdict())

        agent = VoicePipelineAgent(
            vad=None,
            stt=create_stt(),
            llm=create_llm(),
            tts=create_tts(),
            chat_ctx=llm.ChatContext().append(
                role="system",
                text=SYSTEM_PROMPT,
            ),
        )

        agent.start(room=ctx.room)

        await agent.say(GREETING, allow_interruptions=False)

    if _calls_active:
        _calls_active.add(-1, {"tenant_id": session.tenant_id})
    logger.info("VMO session ended", vmo_call_id=session.vmo_call_id)


def create_worker() -> WorkerOptions:
    """Create LiveKit worker options."""
    return WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="vmo-livekit",
        ws_url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )
