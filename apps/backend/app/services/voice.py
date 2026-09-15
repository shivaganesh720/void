import base64


class VoiceService:
    """Abstraction for Voice capabilities (STT/TTS)."""

    def __init__(self, provider: str = "local"):
        self.provider = provider

    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe speech to text.

        The local provider intentionally keeps the behavior deterministic and
        human-readable so the runtime can use it in mission creation without a
        second fake orchestration layer.
        """
        if self.provider == "local":
            text = audio_data.decode("utf-8", errors="replace").strip()
            if text.startswith("VOICE:"):
                return text.split("VOICE:", 1)[1].strip()
            if text:
                return text
            return "Voice command recognized but no transcript was supplied."
        raise NotImplementedError("External provider not configured.")

    def transcribe_base64(self, audio_base64: str) -> str:
        """Decode a base64-encoded audio payload into plain text."""
        if not audio_base64:
            raise ValueError("VOICE_AUDIO_EMPTY")
        payload = audio_base64.strip()
        if len(payload) % 4:
            payload += "=" * (-len(payload) % 4)
        try:
            audio_data = base64.b64decode(payload, validate=True)
        except ValueError as exc:
            raise ValueError("VOICE_AUDIO_INVALID_BASE64") from exc
        return self.transcribe(audio_data)

    def synthesize(self, text: str) -> bytes:
        """Convert text to speech."""
        if self.provider == "local":
            return text.encode("utf-8")
        raise NotImplementedError("External provider not configured.")
