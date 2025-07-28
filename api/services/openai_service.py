import os
from openai import OpenAI
import json


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_girlfriend_response(self, user_message: str):
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
        messages = json.loads(content)
        if "messages" in messages:
            return messages["messages"]
        return messages
