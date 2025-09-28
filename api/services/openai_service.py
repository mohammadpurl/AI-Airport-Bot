import os
import requests  # type: ignore[import]
import logging
from requests.adapters import HTTPAdapter  # type: ignore[import]
from urllib3.util.retry import Retry  # type: ignore[import]

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.url = os.getenv("EXTERNAL_CHAT_SERVICE_URL")
        # Create a session for connection pooling with robust retry strategy
        self.session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(
            max_retries=retries,
            pool_connections=20,  # افزایش از 10 به 20
            pool_maxsize=50,  # افزایش از 20 به 50
            pool_block=False,
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Set default headers with keep-alive hints
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "curl/7.68.0",  # استفاده از curl user-agent
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

        # تست مستقیم بدون connection pooling
        use_direct_connection = (
            os.getenv("USE_DIRECT_CONNECTION", "true").lower() == "true"
        )
        logger.info(f"USE_DIRECT_CONNECTION: {use_direct_connection}")

        if use_direct_connection:
            logger.info(f"Testing direct connection to: {self.url}")
            try:
                import requests as direct_requests

                response = direct_requests.post(
                    self.url,
                    json=payload,
                    timeout=30,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "User-Agent": "curl/7.68.0",
                    },
                    verify=False,
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Direct connection successful: {result}")
                return result["messages"] if "messages" in result else result
            except Exception as direct_error:
                logger.warning(f"Direct connection failed: {direct_error}")
                logger.info("Falling back to session-based connection")

        # Optimized retry with tuned timeouts per attempt
        for attempt in range(3):
            try:
                timeout = 15 if attempt == 0 else (30 if attempt == 1 else 45)
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
