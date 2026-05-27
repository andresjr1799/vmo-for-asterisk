"""ASAP Backend Agentic LLM — REST SSE streaming LLM provider."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional, TYPE_CHECKING

from ..observability.log_setup import get_logger

logger = get_logger(__name__)

try:
    import httpx
except ImportError:
    httpx = None

try:
    from pipecat.frames.frames import (
        TextFrame,
        LLMContextFrame,
        LLMFullResponseStartFrame,
        LLMFullResponseEndFrame,
    )
    from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
    _PIPECAT = True
except ImportError:
    _PIPECAT = False

    class FrameProcessor:
        def __init__(self, **kw): pass

    class TextFrame:
        def __init__(self, text): self.text = text

    class LLMContextFrame:
        def __init__(self, context=None): self.context = context

    class LLMFullResponseStartFrame:
        pass

    class LLMFullResponseEndFrame:
        pass

    class FrameDirection:
        DOWNSTREAM = 0

if TYPE_CHECKING:
    from ..config.models import AudioProfileCfg


def build_service(resolved: Any, audio_profile: "AudioProfileCfg", **kwargs: Any) -> "ASAPBackendAgenticLLM":
    params = dict(resolved.params or {})
    url = params.pop("url", "http://localhost:9094/api/v1/agentic/inference/stream")
    timeout = int(params.pop("timeout", 45))

    identity = kwargs.get("identity")
    tenant_id = identity.tenant_id if identity else ""

    return ASAPBackendAgenticLLM(
        url=url,
        api_key=resolved.api_key or "",
        timeout=timeout,
        tenant_id=tenant_id,
    )


class ASAPBackendAgenticLLM(FrameProcessor):

    def __init__(
        self, *, url: str = "", api_key: str = "", timeout: int = 45,
        tenant_id: str = "", **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._url = url
        self._api_key = api_key
        self._timeout = timeout
        self._tenant_id = tenant_id
        self._functions: Dict[str, Any] = {}

    def register_function(self, name: str, cb: Any) -> None:
        self._functions[name] = cb

    async def process_frame(self, frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, LLMContextFrame):
            await self._handle_llm_context(frame)
        else:
            await self.push_frame(frame, direction)

    async def _handle_llm_context(self, frame: LLMContextFrame) -> None:
        messages = getattr(frame.context, "messages", []) if frame.context else []
        user_input = self._extract_user_input(messages)
        if not user_input:
            logger.warning("ASAP LLM: no user input, skipping")
            return

        await self.push_frame(LLMFullResponseStartFrame())
        start_time = time.monotonic()

        try:
            await self._stream_response(user_input)
        except Exception as exc:
            logger.error("ASAP LLM streaming failed", error=str(exc), exc_info=True)
            await self.push_frame(TextFrame("Lo siento, no puedo procesar tu solicitud en este momento."))
        finally:
            elapsed = int((time.monotonic() - start_time) * 1000)
            logger.debug("ASAP LLM turn complete", elapsed_ms=elapsed)
            await self.push_frame(LLMFullResponseEndFrame())

    def _extract_user_input(self, messages: list) -> str:
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                return str(msg.get("content", ""))
        return ""

    async def _stream_response(self, user_input: str) -> None:
        if not httpx:
            raise RuntimeError("httpx not installed")

        payload = {"user_input": user_input, "sentiment": {}}
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-Tenant-Id": self._tenant_id,
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        logger.debug("ASAP LLM sending request", url=self._url, input_len=len(user_input))

        async with httpx.AsyncClient(timeout=float(self._timeout)) as client:
            async with client.stream("POST", self._url, json=payload, headers=headers) as response:
                logger.debug("ASAP LLM response status", status=response.status_code)
                line_count = 0
                async for line in response.aiter_lines():
                    line_count += 1
                    if not line or not line.startswith("data: "):
                        if line:
                            logger.debug("ASAP LLM non-SSE line", line=line[:200])
                        continue
                    try:
                        data = json.loads(line.removeprefix("data: "))
                    except json.JSONDecodeError:
                        logger.debug("ASAP LLM JSON decode failed", raw=line[:200])
                        continue
                    event_type = data.get("type", "")
                    logger.debug("ASAP LLM event", type=event_type, keys=list(data.keys()))
                    if event_type == "delta":
                        content = data.get("content", "")
                        if content:
                            await self.push_frame(TextFrame(content))
                    elif event_type == "done":
                        logger.debug("ASAP LLM stream done")
                        return
                logger.debug("ASAP LLM stream ended", lines_received=line_count)
