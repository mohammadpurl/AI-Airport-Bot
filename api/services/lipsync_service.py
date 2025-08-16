import subprocess
import logging
import os

logger = logging.getLogger(__name__)


class LipSyncService:
    @staticmethod
    def mp3_to_wav(mp3_path: str, wav_path: str):
        try:
            logger.info(f"Converting {mp3_path} to {wav_path}")
            subprocess.run(["ffmpeg", "-y", "-i", mp3_path, wav_path], check=True)
            logger.info(f"MP3 to WAV conversion completed: {wav_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e}")
            raise
        except FileNotFoundError:
            logger.error("FFmpeg not found. Please install FFmpeg.")
            raise

    @staticmethod
    def wav_to_lipsync_json(wav_path: str, json_path: str):
        try:
            logger.info(f"Generating lipsync for {wav_path}")
            # Pick correct Rhubarb executable across OSes
            if os.name == "nt":
                rhubarb_exec = os.path.join("bin", "rhubarb.exe")
            else:
                rhubarb_exec = os.path.join("./bin", "rhubarb")
            subprocess.run(
                [
                    rhubarb_exec,
                    "-f",
                    "json",
                    "-o",
                    json_path,
                    wav_path,
                    "-r",
                    "phonetic",
                ],
                check=True,
            )
            logger.info(f"Lipsync JSON created: {json_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Rhubarb error: {e}")
            raise
        except FileNotFoundError:
            logger.error("Rhubarb not found. Please install Rhubarb.")
            raise
