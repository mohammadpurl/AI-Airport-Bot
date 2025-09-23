import os
import requests
import logging

logger = logging.getLogger(__name__)


class ElevenLabsService:
    def __init__(self):
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.base_url = os.getenv("EXTERNAL_ELEVENLABS_SERVICE_URL")

        if not self.base_url:
            logger.warning(
                "EXTERNAL_ELEVENLABS_SERVICE_URL is not set; ElevenLabs TTS will fail"
            )
        else:
            logger.info(
                f"ElevenLabs service initialized (url set, voice_id={'set' if self.voice_id else 'not set'})"
            )

    def text_to_speech(self, text: str, file_name: str):
        try:
            logger.info(f"Converting text to speech: {text[:50]}...")
            logger.info(f"Output file: {file_name}")
            if not self.base_url:
                raise RuntimeError(
                    "EXTERNAL_ELEVENLABS_SERVICE_URL is not configured in environment"
                )

            # Ensure destination directory exists
            try:
                os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not ensure output directory exists: {e}")

            payload = {
                "text": text,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
            }
            if self.voice_id:
                payload["voice_id"] = self.voice_id

            response = requests.post(self.base_url, json=payload, timeout=60)
            logger.info(
                f"ElevenLabs TTS response status={response.status_code} length={len(response.content)}"
            )
            try:
                response.raise_for_status()
            except Exception:
                # Log server response body to ease debugging
                logger.error(
                    f"ElevenLabs TTS error body: {getattr(response, 'text', '')[:500]}"
                )
                raise

            if not response.content:
                raise ValueError("TTS service returned empty audio content")

            with open(file_name, "wb") as f:
                f.write(response.content)

            logger.info(f"Audio file created successfully: {file_name}")

        except Exception as e:
            logger.error(f"Error in ElevenLabs text-to-speech: {e}")
            raise
