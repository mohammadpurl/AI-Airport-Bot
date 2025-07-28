import base64
import json


class FileService:
    @staticmethod
    def audio_file_to_base64(file_path: str) -> str:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    @staticmethod
    def read_json_transcript(file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
