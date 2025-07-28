import os
import requests


class ElevenLabsService:
    def __init__(self):
        self.api_key = os.getenv("ELEVEN_LABS_API_KEY")
        self.voice_id = "508da0af14044417a916cba1d00f632a"
        self.base_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    def text_to_speech(self, text: str, file_name: str):
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        with open(file_name, "wb") as f:
            f.write(response.content)
