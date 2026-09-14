class VoiceService:
    """Abstraction for Voice capabilities (STT/TTS)."""
    
    def __init__(self, provider: str = "local"):
        self.provider = provider
        
    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe speech to text."""
        if self.provider == "local":
            return "Mock transcribed intent from voice."
        raise NotImplementedError("External provider not configured.")

    def synthesize(self, text: str) -> bytes:
        """Convert text to speech."""
        if self.provider == "local":
            return b"mock-audio-data"
        raise NotImplementedError("External provider not configured.")
