"""ASAP Backend Agentic LLM — LiveKit-compatible SSE streaming provider.

Only sends the last user message. Backend manages memory/context.
VMO is a pure text gateway.
"""

import json
import time
import uuid

import aiohttp
from livekit.agents.llm import LLM, ChatChunk, ChatContext, Choice, ChoiceDelta
from livekit.agents import llm

from .config import ASAP_BACKEND_URL, ASAP_BACKEND_TIMEOUT


class ASAPBackendLLM(LLM):
    """LiveKit-compatible LLM that streams from ASAP backend via SSE.

    Only the last user message is sent. System prompt is added as first
    message. Backend handles conversation context.
    """

    def __init__(self, base_url: str, timeout: int = 45):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def achat(
        self,
        chat_ctx: ChatContext,
        *,
        fnc_ctx: llm.FunctionContext | None = None,
        temperature: float | None = None,
        n: int = 1,
        parallel_tool_calls: bool = False,
    ) -> ChatChunk:
        """Stream chat completion from ASAP backend.

        Yields ChatChunk objects with delta text.
        Only first choice, always finish_reason='stop'.
        """
        messages = chat_ctx.messages
        text = messages[-1].content if messages else ""

        correlation_id = str(uuid.uuid4())
        call_id = str(uuid.uuid4())

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "X-Correlation-Id": correlation_id,
            "X-Call-Id": call_id,
        }

        payload = {
            "messages": [{"role": "user", "content": text}],
            "stream": True,
        }

        timeout = aiohttp.ClientTimeout(total=self._timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self._base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
            ) as resp:
                async for line in resp.content:
                    line = line.decode("utf-8").strip()
                    if not line or not line.startswith("data: "):
                        continue

                    data = line.removeprefix("data: ").strip()
                    if data == "[DONE]":
                        break

                    try:
                        chunk_data = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    choices = chunk_data.get("choices", [])
                    if not choices:
                        continue

                    delta = choices[0].get("delta", {})
                    content = delta.get("content", "")
                    finish = choices[0].get("finish_reason")

                    if content:
                        yield ChatChunk(
                            request_id=correlation_id,
                            choices=[
                                Choice(
                                    delta=ChoiceDelta(
                                        content=content,
                                        role="assistant",
                                    ),
                                    index=0,
                                )
                            ],
                        )
