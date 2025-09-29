import base64
import json
import logging

logger = logging.getLogger(__name__)


class FileService:
    @staticmethod
    def audio_file_to_base64(file_path: str) -> str:
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            result = base64.b64encode(data).decode()
            return result
        except FileNotFoundError:
            logger.error(f"Audio file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading audio file {file_path}: {e}")
            raise

    @staticmethod
    def read_json_transcript(file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            logger.error(f"JSON transcript file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading JSON transcript {file_path}: {e}")
            raise
