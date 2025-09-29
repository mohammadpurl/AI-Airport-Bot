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

        # Configure proxy if available (supports HTTP/HTTPS/SOCKS via PROXY_URL)
        proxy_url = (
            os.getenv("PROXY_URL")
            or os.getenv("HTTP_PROXY")
            or os.getenv("HTTPS_PROXY")
        )
        if proxy_url:
            self.session.proxies = {"http": proxy_url, "https": proxy_url}
            logger.info(f"Using proxy: {proxy_url}")

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(
            max_retries=retries,
            pool_connections=5,  # کاهش از 20 به 5
            pool_maxsize=10,  # کاهش از 50 به 10
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

    def cleanup_session(self):
        """Clean up session connections"""
        try:
            self.session.close()
            logger.info("Session cleaned up successfully")
        except Exception as e:
            logger.warning(f"Session cleanup failed: {e}")

    def __del__(self):
        """Destructor to ensure session cleanup"""
        self.cleanup_session()

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
            os.getenv("USE_DIRECT_CONNECTION", "false").lower()
            == "true"  # Default to false on server
        )

        if use_direct_connection:
            try:
                import requests as direct_requests

                # Configure proxy for direct requests (supports PROXY_URL)
                proxies = {}
                proxy_url = (
                    os.getenv("PROXY_URL")
                    or os.getenv("HTTP_PROXY")
                    or os.getenv("HTTPS_PROXY")
                )
                if proxy_url:
                    proxies = {"http": proxy_url, "https": proxy_url}

                response = direct_requests.post(
                    self.url,
                    json=payload,
                    timeout=30,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "User-Agent": "curl/7.68.0",
                    },
                    proxies=proxies,
                    verify=False,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("messages", result)
            except Exception as direct_error:
                logger.warning(f"Direct connection failed: {direct_error}")

        # Fallback: استفاده از endpoint محلی یا mock response
        fallback_response = {
            "messages": [
                {
                    "text": "متأسفانه در حال حاضر سرویس خارجی در دسترس نیست. لطفاً بعداً تلاش کنید.",
                    "facialExpression": "sad",
                    "animation": "Idle",
                }
            ],
            "session_id": session_id,
        }
        return fallback_response["messages"]
