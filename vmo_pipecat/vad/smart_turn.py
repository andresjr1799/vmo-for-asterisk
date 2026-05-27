"""SmartTurn VAD — ML-based turn detection via LocalSmartTurnAnalyzerV3.

Integrates pipecat-ai's SmartTurn analyzer as a drop-in replacement for
SileroVAD. Activated in tenants.yaml with ``vad: smart_turn``.

Usage::

    from .vad.smart_turn import build_smart_turn_analyzer

    analyzer = build_smart_turn_analyzer(stop_secs=2.0)
    # UserTurnStrategies with TurnAnalyzerUserTurnStopStrategy
"""

from __future__ import annotations

from typing import Optional

from ..observability.log_setup import get_logger

logger = get_logger(__name__)

try:
    from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
    from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import (
        LocalSmartTurnAnalyzerV3,
    )

    _PIPECAT = True
except ImportError:
    _PIPECAT = False

    class SmartTurnParams:  # type: ignore[no-redef]
        def __init__(self, **kw): pass

    class LocalSmartTurnAnalyzerV3:  # type: ignore[no-redef]
        def __init__(self, **kw): pass


def build_smart_turn_analyzer(stop_secs: float = 1.0) -> Optional[LocalSmartTurnAnalyzerV3]:
    if not _PIPECAT:
        logger.warning("pipecat-ai not installed — SmartTurn disabled, falling back to SileroVAD")
        return None

    params = SmartTurnParams(stop_secs=stop_secs)
    analyzer = LocalSmartTurnAnalyzerV3(params=params)
    logger.info("SmartTurn analyzer initialized", stop_secs=stop_secs)
    return analyzer
