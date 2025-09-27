import os
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.url = os.getenv("EXTERNAL_CHAT_SERVICE_URL")
        # Create a session for connection pooling
        self.session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
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

    def get_assistant_response(
        self, user_message: str, session_id: str, language: str = "fa"
    ):
        payload = {
            "message": user_message,
            "session_id": session_id,
            "language": language,
        }

        # Try multiple times with different timeouts for Vercel cold start
        for attempt in range(3):
            try:
                timeout = 60 if attempt == 0 else 120  # Increase timeouts
                logger.info(
                    f"Calling external chat service (attempt {attempt + 1}): {self.url}"
                )
                response = self.session.post(
                    self.url, json=payload, timeout=timeout, verify=False
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"External chat service response: {result}")
                return result["messages"] if "messages" in result else result
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    logger.error(f"All attempts failed. Last error: {e}")
                    raise
