import os
import requests
import logging

logger = logging.getLogger(__name__)


class ElevenLabsService:
    def __init__(self):

        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.base_url = os.getenv("EXTERNAL_ELEVENLABS_SERVICE_URL")
        logger.info("ElevenLabs service initialized successfully")

    def text_to_speech(self, text: str, file_name: str):
        try:
            logger.info(f"Converting text to speech: {text[:50]}...")
            logger.info(f"Output file: {file_name}")
            payload = {
                "text": text,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
            }

            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()

            with open(file_name, "wb") as f:
                f.write(response.content)

            logger.info(f"Audio file created successfully: {file_name}")

        except Exception as e:
            logger.error(f"Error in ElevenLabs text-to-speech: {e}")
            raise
