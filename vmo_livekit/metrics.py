"""OpenTelemetry — traces, metrics, structured logs.

All observability in one file. No CallMetrics, MetricsFrameProcessor,
or EventBus needed — LiveKit handles the pipeline lifecycle natively.
"""

import logging
import os
import structlog

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from .config import OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME, LOG_LEVEL

_tracer: trace.Tracer | None = None
_meter: metrics.Meter | None = None

# ── Metrics ────────────────────────────────────────────────────────────────────

_stt_latency: metrics.Histogram | None = None
_llm_ttfb: metrics.Histogram | None = None
_tts_first_audio: metrics.Histogram | None = None
_turn_response: metrics.Histogram | None = None
_calls_total: metrics.Counter | None = None
_calls_active: metrics.UpDownCounter | None = None


def init_otel() -> None:
    """Initialize OpenTelemetry SDK — traces, metrics, logs."""
    global _tracer, _meter, _stt_latency, _llm_ttfb, _tts_first_audio
    global _turn_response, _calls_total, _calls_active

    resource = Resource(attributes={"service.name": OTEL_SERVICE_NAME})

    # Traces
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT))
    )
    trace.set_tracer_provider(tracer_provider)
    _tracer = trace.get_tracer(__name__)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    _meter = metrics.get_meter(__name__)

    _stt_latency = _meter.create_histogram(
        "vmo.stt.latency", unit="ms", description="STT transcription latency"
    )
    _llm_ttfb = _meter.create_histogram(
        "vmo.llm.ttfb", unit="ms", description="LLM time-to-first-token"
    )
    _tts_first_audio = _meter.create_histogram(
        "vmo.tts.first_audio", unit="ms", description="TTS time-to-first-audio"
    )
    _turn_response = _meter.create_histogram(
        "vmo.turn.response", unit="ms", description="Full turn response time"
    )
    _calls_total = _meter.create_counter(
        "vmo.calls.total", description="Total calls"
    )
    _calls_active = _meter.create_up_down_counter(
        "vmo.calls.active", description="Active calls"
    )


def get_tracer() -> trace.Tracer:
    if _tracer is None:
        init_otel()
    return _tracer  # type: ignore[return-value]


# ── Structured logging ─────────────────────────────────────────────────────────

def setup_logging() -> None:
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=level, format="%(message)s")


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
