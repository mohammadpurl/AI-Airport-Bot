from fastapi import APIRouter, HTTPException
from api.schemas.girlfriend_schema import ChatRequest, ChatResponse, Message
from api.services.openai_service import OpenAIService
from api.services.elevenlabs_service import ElevenLabsService
from api.services.lipsync_service import LipSyncService
from api.services.file_service import FileService
import os

router = APIRouter()


def get_elevenlabs_api_key():
    return os.getenv("ELEVEN_LABS_API_KEY")


@router.get("/")
def root():
    return {"message": "Hello World!"}


@router.get("/test")
def test():
    return {"status": "ok", "message": "Test route is working!"}


@router.get("/voices")
def get_voices():
    api_key = get_elevenlabs_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="ELEVEN_LABS_API_KEY not set")
    # اینجا باید درخواست به API اصلی ElevenLabs برای گرفتن لیست صداها ارسال شود
    # برای سادگی، فقط یک پیام تست برمی‌گردانیم
    return {"voices": ["voice1", "voice2", "voice3"]}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    openai_service = OpenAIService()
    elevenlabs_service = ElevenLabsService()
    lipsync_service = LipSyncService()
    file_service = FileService()
    api_key = get_elevenlabs_api_key()

    if not request.message:
        # پیام پیش‌فرض (مانند Node)
        messages = [
            Message(
                text="Hey dear... How was your day?",
                audio=file_service.audio_file_to_base64("audios/intro_0.wav"),
                lipsync=file_service.read_json_transcript("audios/intro_0.json"),
                facialExpression="smile",
                animation="Talking_1",
            ),
            Message(
                text="I missed you so much... Please don't go for so long!",
                audio=file_service.audio_file_to_base64("audios/intro_1.wav"),
                lipsync=file_service.read_json_transcript("audios/intro_1.json"),
                facialExpression="sad",
                animation="Crying",
            ),
        ]
        return ChatResponse(messages=messages)

    if not api_key or not os.getenv("OPENAI_API_KEY"):
        messages = [
            Message(
                text="Please my dear, don't forget to add your API keys!",
                audio=file_service.audio_file_to_base64("audios/api_0.wav"),
                lipsync=file_service.read_json_transcript("audios/api_0.json"),
                facialExpression="angry",
                animation="Angry",
            ),
            Message(
                text="You don't want to ruin Wawa Sensei with a crazy ChatGPT and ElevenLabs bill, right?",
                audio=file_service.audio_file_to_base64("audios/api_1.wav"),
                lipsync=file_service.read_json_transcript("audios/api_1.json"),
                facialExpression="smile",
                animation="Laughing",
            ),
        ]
        return ChatResponse(messages=messages)

    # گرفتن پیام‌ها از OpenAI
    messages: list = openai_service.get_girlfriend_response(request.message)
    result_messages = []
    for i, message in enumerate(messages):
        file_name = f"audios/message_{i}.mp3"
        text_input = message["text"]
        elevenlabs_service.text_to_speech(text_input, file_name)
        wav_file = f"audios/message_{i}.wav"
        lipsync_service.mp3_to_wav(file_name, wav_file)
        json_file = f"audios/message_{i}.json"
        lipsync_service.wav_to_lipsync_json(wav_file, json_file)
        result_messages.append(
            Message(
                text=message["text"],
                audio=file_service.audio_file_to_base64(file_name),
                lipsync=file_service.read_json_transcript(json_file),
                facialExpression=message["facialExpression"],
                animation=message["animation"],
            )
        )
    return ChatResponse(messages=result_messages)


@router.get("/health")
def health():
    return {"status": "ok", "message": "Backend is running!"}
