#!/usr/bin/env python3
"""
Test script to verify proxy configuration
"""
import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_proxy():
    """Test proxy configuration"""

    # Get proxy from environment
    proxy_url = "http://185.128.153.75:33333"

    if not proxy_url:
        logger.warning(
            "No proxy configured. Set HTTP_PROXY or HTTPS_PROXY environment variable."
        )
        return False

    logger.info(f"Testing proxy: {proxy_url}")

    # Configure proxies
    proxies = {"http": proxy_url, "https": proxy_url}

    # Test URLs
    test_urls = [
        "https://elevenlab-test.vercel.app/assistant/chat",
    ]

    for url in test_urls:
        try:
            logger.info(f"Testing: {url}")
            response = requests.get(url, proxies=proxies, timeout=10)
            logger.info(f"Success: {response.status_code}")
            if "ipify" in url:
                logger.info(f"Your IP: {response.json()}")
        except Exception as e:
            logger.error(f"Failed: {e}")

    return True


if __name__ == "__main__":
    test_proxy()
