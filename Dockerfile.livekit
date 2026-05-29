FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    livekit-agents \
    livekit-plugins-deepgram \
    livekit-plugins-elevenlabs \
    livekit-plugins-openai \
    opentelemetry-api opentelemetry-sdk \
    opentelemetry-exporter-otlp-proto-grpc \
    structlog

COPY vmo_livekit/ /app/vmo_livekit/

ENV PYTHONPATH=/app
EXPOSE 8080 5060

CMD ["python", "-m", "vmo_livekit"]
