import os
from openai import OpenAI
import json
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not set")
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = OpenAI(api_key=api_key)
        logger.info("OpenAI service initialized successfully")

    def get_girlfriend_response(self, user_message: str):
        try:
            logger.info(f"Sending request to OpenAI: {user_message[:50]}...")

            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                max_tokens=1000,
                temperature=0.6,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a virtual girlfriend. "
                            "You will always reply with a JSON array of messages. With a maximum of 3 messages. "
                            "Each message has a text, facialExpression, and animation property. "
                            "The different facial expressions are: smile, sad, angry, surprised, funnyFace, and default. "
                            "The different animations are: Talking_0, Talking_1, Talking_2, Crying, Laughing, Rumba, Idle, Terrified, and Angry. "
                        ),
                    },
                    {"role": "user", "content": user_message or "Hello"},
                ],
            )

            content = completion.choices[0].message.content
            logger.info(f"OpenAI response received: {content[:100]}...")

            messages = json.loads(content)
            if "messages" in messages:
                result = messages["messages"]
            else:
                result = messages

            logger.info(f"Parsed {len(result)} messages from OpenAI")
            return result

        except Exception as e:
            logger.error(f"Error in OpenAI service: {e}")
            raise
