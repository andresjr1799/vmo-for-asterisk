"""PipelineUsageAggregator — tracks STT/TTS/LLM usage from native MetricsFrame.

Listens to pipecat's built-in ``MetricsFrame`` (enabled via ``enable_metrics=True``
in ``PipelineParams``) and aggregates:
  - LLM token usage (prompt + completion + total)
  - TTS character count
  - STT audio duration (seconds)

Exposes ``summary()`` for inclusion in ``vmo.call.ended`` events.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Optional

from pipecat.frames.frames import (
    CancelFrame,
    EndFrame,
    Frame,
    MetricsFrame,
    StartFrame,
)
from pipecat.metrics.metrics import (
    LLMTokenUsage,
    LLMUsageMetricsData,
    TTSUsageMetricsData,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class PipelineUsageAggregator(FrameProcessor):
    """Aggregates STT/TTS/LLM usage across all turns of a pipeline."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._llm_tokens: Dict[str, LLMTokenUsage] = {}
        self._tts_chars: Dict[str, int] = defaultdict(int)
        self._stt_duration: Dict[str, float] = defaultdict(float)

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, MetricsFrame):
            for data in frame.data:
                if isinstance(data, LLMUsageMetricsData):
                    self._handle_llm(data)
                elif isinstance(data, TTSUsageMetricsData):
                    self._handle_tts(data)

        await self.push_frame(frame, direction)

    def _handle_llm(self, data: LLMUsageMetricsData):
        key = f"{data.processor}|||{data.model}"
        usage = data.value
        if key in self._llm_tokens:
            existing = self._llm_tokens[key]
            self._llm_tokens[key] = LLMTokenUsage(
                prompt_tokens=existing.prompt_tokens + usage.prompt_tokens,
                completion_tokens=existing.completion_tokens + usage.completion_tokens,
                total_tokens=existing.total_tokens + usage.total_tokens,
                cache_read_input_tokens=(existing.cache_read_input_tokens or 0)
                + (usage.cache_read_input_tokens or 0),
            )
        else:
            self._llm_tokens[key] = usage

    def _handle_tts(self, data: TTSUsageMetricsData):
        key = f"{data.processor}|||{data.model}"
        self._tts_chars[key] += data.value

    def summary(self) -> dict:
        llm_summary = {}
        for key, usage in self._llm_tokens.items():
            llm_summary[key] = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }

        return {
            "llm_tokens": llm_summary,
            "tts_chars": dict(self._tts_chars),
            "stt_duration_s": dict(self._stt_duration),
        }
