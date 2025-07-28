from fastapi import APIRouter, HTTPException
from api.schemas.girlfriend_schema import ChatRequest, ChatResponse, Message
from api.services.openai_service import OpenAIService
from api.services.elevenlabs_service import ElevenLabsService
from api.services.lipsync_service import LipSyncService
from api.services.file_service import FileService
import os
import logging

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def get_elevenlabs_api_key():
    return os.getenv("ELEVEN_LABS_API_KEY")


@router.get("/")
def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World!"}


@router.get("/test")
def test():
    logger.info("Test endpoint called")
    return {"status": "ok", "message": "Test route is working!"}


@router.get("/voices")
def get_voices():
    logger.info("Voices endpoint called")
    api_key = get_elevenlabs_api_key()
    if not api_key:
        logger.error("ELEVEN_LABS_API_KEY not set")
        raise HTTPException(status_code=400, detail="ELEVEN_LABS_API_KEY not set")
    # اینجا باید درخواست به API اصلی ElevenLabs برای گرفتن لیست صداها ارسال شود
    # برای سادگی، فقط یک پیام تست برمی‌گردانیم
    return {"voices": ["voice1", "voice2", "voice3"]}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger.info(f"Chat endpoint called with message: {request.message}")

    openai_service = OpenAIService()
    elevenlabs_service = ElevenLabsService()
    lipsync_service = LipSyncService()
    file_service = FileService()
    api_key = get_elevenlabs_api_key()

    if not request.message:
        logger.info("No message provided, returning default messages")
        # پیام پیش‌فرض (مانند Node)
        default_messages = []

        # بررسی وجود فایل‌های پیش‌فرض
        intro_files = [
            ("audios/intro_0.wav", "audios/intro_0.json"),
            ("audios/intro_1.wav", "audios/intro_1.json"),
        ]

        for wav_file, json_file in intro_files:
            try:
                if os.path.exists(wav_file) and os.path.exists(json_file):
                    default_messages.append(
                        Message(
                            text=(
                                "Hey dear... How was your day?"
                                if "intro_0" in wav_file
                                else "I missed you so much... Please don't go for so long!"
                            ),
                            audio=file_service.audio_file_to_base64(wav_file),
                            lipsync=file_service.read_json_transcript(json_file),
                            facialExpression=(
                                "smile" if "intro_0" in wav_file else "sad"
                            ),
                            animation=(
                                "Talking_1" if "intro_0" in wav_file else "Crying"
                            ),
                        )
                    )
                else:
                    logger.warning(
                        f"Default audio files not found: {wav_file} or {json_file}"
                    )
            except Exception as e:
                logger.error(f"Error reading default files: {e}")

        if not default_messages:
            # اگر فایل‌های پیش‌فرض وجود ندارند، پیام ساده برگردان
            default_messages = [
                Message(
                    text="Hey dear... How was your day?",
                    audio=None,
                    lipsync=None,
                    facialExpression="smile",
                    animation="Talking_1",
                ),
                Message(
                    text="I missed you so much... Please don't go for so long!",
                    audio=None,
                    lipsync=None,
                    facialExpression="sad",
                    animation="Crying",
                ),
            ]

        return ChatResponse(messages=default_messages)

    if not api_key or not os.getenv("OPENAI_API_KEY"):
        logger.warning("API keys not set")
        api_messages = []

        # بررسی وجود فایل‌های API warning
        api_files = [
            ("audios/api_0.wav", "audios/api_0.json"),
            ("audios/api_1.wav", "audios/api_1.json"),
        ]

        for wav_file, json_file in api_files:
            try:
                if os.path.exists(wav_file) and os.path.exists(json_file):
                    api_messages.append(
                        Message(
                            text=(
                                "Please my dear, don't forget to add your API keys!"
                                if "api_0" in wav_file
                                else "You don't want to ruin Wawa Sensei with a crazy ChatGPT and ElevenLabs bill, right?"
                            ),
                            audio=file_service.audio_file_to_base64(wav_file),
                            lipsync=file_service.read_json_transcript(json_file),
                            facialExpression=(
                                "angry" if "api_0" in wav_file else "smile"
                            ),
                            animation="Angry" if "api_0" in wav_file else "Laughing",
                        )
                    )
                else:
                    logger.warning(
                        f"API warning audio files not found: {wav_file} or {json_file}"
                    )
            except Exception as e:
                logger.error(f"Error reading API warning files: {e}")

        if not api_messages:
            # اگر فایل‌های API warning وجود ندارند، پیام ساده برگردان
            api_messages = [
                Message(
                    text="Please my dear, don't forget to add your API keys!",
                    audio=None,
                    lipsync=None,
                    facialExpression="angry",
                    animation="Angry",
                ),
                Message(
                    text="You don't want to ruin Wawa Sensei with a crazy ChatGPT and ElevenLabs bill, right?",
                    audio=None,
                    lipsync=None,
                    facialExpression="smile",
                    animation="Laughing",
                ),
            ]

        return ChatResponse(messages=api_messages)

    try:
        # گرفتن پیام‌ها از OpenAI
        logger.info("Getting response from OpenAI")
        openai_messages: list = openai_service.get_girlfriend_response(request.message)
        logger.info(f"OpenAI returned {len(openai_messages)} messages")

        result_messages = []

        # ایجاد پوشه audios اگر وجود ندارد
        os.makedirs("audios", exist_ok=True)

        for i, message in enumerate(openai_messages):
            logger.info(f"Processing message {i}: {message.get('text', 'No text')}")

            file_name = f"audios/message_{i}.mp3"
            text_input = message["text"]

            try:
                # تبدیل متن به گفتار
                logger.info(f"Converting text to speech: {text_input[:50]}...")
                elevenlabs_service.text_to_speech(text_input, file_name)
                logger.info(f"Audio file created: {file_name}")

                wav_file = f"audios/message_{i}.wav"
                json_file = f"audios/message_{i}.json"

                # تبدیل mp3 به wav
                logger.info(f"Converting {file_name} to {wav_file}")
                lipsync_service.mp3_to_wav(file_name, wav_file)

                # تولید lipsync
                logger.info(f"Generating lipsync for {wav_file}")
                lipsync_service.wav_to_lipsync_json(wav_file, json_file)

                # خواندن فایل‌ها
                audio_base64 = file_service.audio_file_to_base64(file_name)
                lipsync_data = file_service.read_json_transcript(json_file)

                result_messages.append(
                    Message(
                        text=message["text"],
                        audio=audio_base64,
                        lipsync=lipsync_data,
                        facialExpression=message["facialExpression"],
                        animation=message["animation"],
                    )
                )
                logger.info(f"Message {i} processed successfully")

            except Exception as e:
                logger.error(f"Error processing message {i}: {e}")
                # در صورت خطا، پیام بدون audio و lipsync برگردان
                result_messages.append(
                    Message(
                        text=message["text"],
                        audio=None,
                        lipsync=None,
                        facialExpression=message["facialExpression"],
                        animation=message["animation"],
                    )
                )

        logger.info(f"Chat completed successfully with {len(result_messages)} messages")
        return ChatResponse(messages=result_messages)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
def health():
    logger.info("Health endpoint called")
    return {"status": "ok", "message": "Backend is running!"}
