import subprocess


class LipSyncService:
    @staticmethod
    def mp3_to_wav(mp3_path: str, wav_path: str):
        subprocess.run(["ffmpeg", "-y", "-i", mp3_path, wav_path], check=True)

    @staticmethod
    def wav_to_lipsync_json(wav_path: str, json_path: str):
        subprocess.run(
            [
                "./bin/rhubarb",
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
