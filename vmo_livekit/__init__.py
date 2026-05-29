"""
VMO LiveKit — Voice Media Orchestrator on LiveKit Agents.

Simplified architecture:
  Asterisk → SIP Trunk → LiveKit SIP → VoicePipelineAgent (STT+LLM+TTS)

Requirements:
  pip install livekit-agents livekit-plugins-deepgram livekit-plugins-elevenlabs
  pip install livekit-plugins-openai livekit-agents[sip]
  pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
"""
