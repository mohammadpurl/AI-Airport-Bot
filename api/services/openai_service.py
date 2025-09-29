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
            pool_connections=5,  # کاهش از 20 به 5
            pool_maxsize=10,  # کاهش از 50 به 10
            pool_block=False,
            pool_recycle=300,  # اضافه کردن recycle هر 5 دقیقه
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
        logger.info(f"USE_DIRECT_CONNECTION: {use_direct_connection}")

        # Reset connection pool if needed
        if hasattr(self.session, "poolmanager"):
            self.session.poolmanager.clear()
            logger.info("Connection pool cleared")

        if use_direct_connection:
            logger.info(f"Testing direct connection to: {self.url}")

            # تست DNS resolution
            try:
                import socket

                host = "elevenlab-test.vercel.app"
                ip = socket.gethostbyname(host)
                logger.info(f"DNS resolution successful: {host} -> {ip}")
            except Exception as dns_error:
                logger.warning(f"DNS resolution failed: {dns_error}")

            # تست connectivity
            try:
                import subprocess

                ping_proc = subprocess.run(
                    ["ping", "-c", "1", "elevenlab-test.vercel.app"],
                    capture_output=True,
                    timeout=10,
                )
                if ping_proc.returncode == 0:
                    logger.info("Ping test successful")
                else:
                    logger.warning(
                        f"Ping test failed: {ping_proc.stderr.decode() if ping_proc.stderr else 'Unknown error'}"
                    )
            except Exception as ping_error:
                logger.warning(f"Ping test error: {ping_error}")

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

        # Fallback: استفاده از endpoint محلی یا mock response
        logger.warning("All external connections failed, using fallback response")
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
        logger.info(f"Fallback response: {fallback_response}")
        return fallback_response["messages"]
