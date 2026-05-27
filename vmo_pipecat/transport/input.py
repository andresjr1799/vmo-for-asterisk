"""
AsteriskAudioSocketInputTransport — PipeCat 1.2.1 compatible.

Recibe PCM16 del AudioSocket y lo inyecta al pipeline de pipecat.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

try:
    from pipecat.transports.base_input import BaseInputTransport
    from pipecat.transports.base_transport import TransportParams
    from pipecat.frames.frames import InputAudioRawFrame
    _PIPECAT = True
except ImportError:
    _PIPECAT = False

    class TransportParams:  # type: ignore[no-redef]
        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)

    class BaseInputTransport:  # type: ignore[no-redef]
        def __init__(self, params=None, **kw):
            self._params = params

    class InputAudioRawFrame:  # type: ignore[no-redef]
        def __init__(self, audio, sample_rate, num_channels):
            self.audio = audio
            self.sample_rate = sample_rate
            self.num_channels = num_channels

if TYPE_CHECKING:
    from ..audio.audiosocket_server import AudioSocketServer


class AsteriskAudioSocketInputTransport(BaseInputTransport):

    def __init__(
        self,
        params: TransportParams,
        *,
        in_sample_rate: int = 16000,
        channels: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(params, **kwargs)
        self._in_sample_rate = in_sample_rate
        self._channels = channels
        self._conn_id: Optional[str] = None
        self._resample_state = None

    def bind(self, conn_id: str) -> None:
        self._conn_id = conn_id

    @property
    def conn_id(self) -> Optional[str]:
        return self._conn_id

    async def push_audio(self, audio_bytes: bytes) -> None:
        if not audio_bytes:
            return

        from ..observability.log_setup import get_logger
        _log = get_logger(__name__)

        self._push_audio_count = getattr(self, '_push_audio_count', 0) + 1

        frame = InputAudioRawFrame(
            audio=audio_bytes,
            sample_rate=self._in_sample_rate,
            num_channels=self._channels,
        )
        await self.push_frame(frame)

        if self._push_audio_count % 100 == 1:
            _log.debug(
                "Transport input push_audio",
                count=self._push_audio_count,
                pcm_bytes=len(audio_bytes),
                in_rate=self._in_sample_rate,
            )

    async def start(self, frame=None) -> None:
        self._resample_state = None
        await super().start(frame)
        await self.set_transport_ready(frame)

    async def stop(self, frame=None) -> None:
        self._conn_id = None
        await super().stop(frame)

    async def cancel(self, frame=None) -> None:
        self._conn_id = None
        await super().cancel(frame)
