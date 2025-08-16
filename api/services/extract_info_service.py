import os
import requests
import logging
from api.schemas.extract_info_schema import ExtractInfoRequest

logger = logging.getLogger(__name__)


class ExtractInfoService:
    def __init__(self):
        self.url = os.getenv("EXTERNAL_EXTRACTINFO_SERVICE_URL")
        if not self.url:
            raise ValueError(
                "EXTERNAL_EXTRACTINFO_SERVICE_URL environment variable is not set"
            )

    def get_extractInfo_response(self, messages: ExtractInfoRequest):
        # Convert messages to the format expected by external service
        payload = {
            "messages": [
                {"id": msg.id, "text": msg.text, "sender": msg.sender}
                for msg in messages.messages
            ]
        }

        try:
            logger.info(f"Calling external extractInfo service: {self.url}")
            logger.info(f"Payload: {payload}")

            response = requests.post(self.url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            logger.info(f"External extractInfo service response: {result}")

            # Validate and return the result
            # The external service should return the same format as before
            expected_fields = [
                "airportName",
                "travelDate",
                "flightNumber",
                "passengers",
            ]

            # Check if all required fields are present
            for field in expected_fields:
                if field not in result:
                    logger.warning(
                        f"Missing field '{field}' in external service response"
                    )
                    if field == "passengers":
                        result[field] = []
                    else:
                        result[field] = ""

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling external extractInfo service: {e}")
            raise ValueError(f"External service error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in extractInfo service: {e}")
            raise ValueError(f"Service error: {str(e)}")


# Create a global instance for backward compatibility
extract_info_service = ExtractInfoService()


async def call_openai(messages: ExtractInfoRequest):
    """
    Backward compatibility function that uses the external service
    """
    return extract_info_service.get_extractInfo_response(messages)
