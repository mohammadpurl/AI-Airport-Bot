import os
import requests
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.url = os.getenv("EXTERNAL_CHAT_SERVICE_URL")

    def get_assistant_response(
        self, user_message: str, session_id: str, language: str = "fa"
    ):
        payload = {
            "message": user_message,
            "session_id": session_id,
            "language": language,
        }
        try:
            logger.info(f"Calling external chat service: {self.url}")
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"External chat service response: {result}")
            return result["messages"] if "messages" in result else result
        except Exception as e:
            logger.error(f"Error calling external chat service: {e}")
            raise
