"""Configuration — all settings from environment variables, no YAML."""

import os

# ── LiveKit ────────────────────────────────────────────────────────────────────
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")

# ── Providers ──────────────────────────────────────────────────────────────────
STT_PROVIDER = os.getenv("STT_PROVIDER", "deepgram")
STT_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
STT_MODEL = os.getenv("STT_MODEL", "nova-3")
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "es")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

TTS_PROVIDER = os.getenv("TTS_PROVIDER", "elevenlabs")
TTS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
TTS_VOICE_ID = os.getenv("TTS_VOICE_ID", "")
TTS_MODEL = os.getenv("TTS_MODEL", "eleven_multilingual_v2")

# ── Agent ──────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Eres un asistente virtual amable. Responde en español de forma concisa.")
GREETING = os.getenv("GREETING", "Hola, ¿en qué puedo ayudarte?")
ENABLE_VAD = os.getenv("ENABLE_VAD", "true").lower() == "true"

# ── Observability ──────────────────────────────────────────────────────────────
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "vmo-livekit")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ── SIP ────────────────────────────────────────────────────────────────────────
SIP_PORT = int(os.getenv("SIP_PORT", "5060"))
SIP_LISTEN_ADDR = os.getenv("SIP_LISTEN_ADDR", "0.0.0.0")
SIP_USERNAME = os.getenv("SIP_USERNAME", "vmo")
SIP_PASSWORD = os.getenv("SIP_PASSWORD", "")

# ── ASAP Backend (optional) ────────────────────────────────────────────────────
ASAP_BACKEND_URL = os.getenv("ASAP_BACKEND_URL", "")
ASAP_BACKEND_TIMEOUT = int(os.getenv("ASAP_BACKEND_TIMEOUT", "45"))
