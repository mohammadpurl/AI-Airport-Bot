import os
import requests  # type: ignore[import]
import logging
from requests.adapters import HTTPAdapter  # type: ignore[import]
from urllib3.util.retry import Retry  # type: ignore[import]

logger = logging.getLogger(__name__)


class ElevenLabsService:
    def __init__(self):
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.base_url = os.getenv("EXTERNAL_ELEVENLABS_SERVICE_URL")
        self.api_key = os.getenv(
            "ELEVENLABS_API_KEY"
        )  # optional, if calling ElevenLabs directly

        if not self.base_url:
            logger.warning(
                "EXTERNAL_ELEVENLABS_SERVICE_URL is not set; ElevenLabs TTS will fail"
            )
        else:
            logger.info(
                f"ElevenLabs service initialized (url set, voice_id={'set' if self.voice_id else 'not set'})"
            )

        # Create a session for connection pooling
        self.session = requests.Session()
        retries = Retry(
            total=1, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        # Set default headers
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
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

            # Set headers for this request
            headers = {}
            if self.api_key:
                headers["xi-api-key"] = self.api_key

            # Optimized retry with shorter timeouts
            for attempt in range(2):
                try:
                    timeout = 20 if attempt == 0 else 40  # Reduced timeouts
                    logger.info(
                        f"ElevenLabs TTS attempt {attempt + 1} with timeout {timeout}s"
                    )

                    response = self.session.post(
                        self.base_url,
                        json=payload,
                        headers=headers,
                        timeout=timeout,
                        verify=False,
                    )

                    logger.info(
                        f"ElevenLabs TTS response status={response.status_code} length={len(response.content)}"
                    )
                    response.raise_for_status()

                    content_type = response.headers.get("Content-Type", "")
                    if content_type and not content_type.lower().startswith("audio"):
                        logger.error(
                            f"Unexpected content-type from TTS: {content_type}"
                        )
                        logger.error(
                            f"Response body (first 500 chars): {getattr(response, 'text', '')[:500]}"
                        )
                        raise ValueError(
                            f"TTS returned non-audio content-type: {content_type}"
                        )

                    if not response.content:
                        raise ValueError("TTS service returned empty audio content")

                    with open(file_name, "wb") as f:
                        f.write(response.content)

                    logger.info(f"Audio file created successfully: {file_name}")
                    return  # Success, exit the retry loop

                except Exception as e:
                    logger.warning(f"ElevenLabs TTS attempt {attempt + 1} failed: {e}")
                    if attempt == 1:  # Last attempt
                        logger.error(
                            f"All ElevenLabs TTS attempts failed. Last error: {e}"
                        )
                        raise
                    continue

        except Exception as e:
            logger.error(f"Error in ElevenLabs text-to-speech: {e}")
            raise
