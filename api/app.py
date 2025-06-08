import os
import speech_recognition as sr  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from google.auth.transport.requests import Request  # type: ignore
from googleapiclient.discovery import build  # type: ignore
import openai
from dotenv import load_dotenv
from api.services.speech_service import SpeechService
from api.services.google_sheets_service import GoogleSheetsService
from api.services.openai_service import OpenAIService
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.routes.response_routes import router as response_router
from api.database.database import engine, Base, get_db
from sqlalchemy import text

# Load environment variables from .env file
load_dotenv(override=True)  # Added override=True to ensure values are loaded

# Print environment variables for debugging
print("Environment variables loaded:")
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print(
    "POSTGRES_PASSWORD:",
    os.getenv("POSTGRES_PASSWORD") if os.getenv("POSTGRES_PASSWORD") else None,
)
print("KNOWLEDGE_SHEET_ID:", os.getenv("KNOWLEDGE_SHEET_ID"))


# Verify required environment variables
required_vars = [
    "OPENAI_API_KEY",
    "POSTGRES_PASSWORD",
    "KNOWLEDGE_SHEET_ID",
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )

# Google Sheets setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
RANGE_NAME = "Sheet1!A1:Z1000"  # Adjust based on your sheet's range


def get_google_sheets_data():
    """Get data from Google Sheets."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    )
    return result.get("values", [])


def get_speech_input():
    """Get speech input from user."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None


def get_openai_response(user_input, context_data):
    """Get response from OpenAI based on user input and context data."""
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Prepare context from Google Sheets data
    context = "\n".join([str(row) for row in context_data])

    # Create prompt with context
    prompt = f"""Based on the following information:
    {context}
    
    Please answer this question: {user_input}"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on the provided context.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting OpenAI response: {e}")
        return None


def main():
    print("Starting the application...")

    # Initialize services
    speech_service = SpeechService()
    sheets_service = GoogleSheetsService()
    openai_service = OpenAIService()

    # Get data from Google Sheets
    print("Fetching data from Google Sheets...")
    context_data = sheets_service.get_sheet_data()

    while True:
        # Get speech input
        user_input = speech_service.get_speech_input()
        if user_input:
            # Get response from OpenAI
            response = openai_service.get_response(user_input, context_data)
            if response:
                print(f"Assistant: {response}")
            else:
                print("Sorry, I couldn't generate a response.")

        # Ask if user wants to continue
        print("\nDo you want to ask another question? (yes/no)")
        continue_input = input().lower()
        if continue_input != "yes":
            break


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Airport AI Assistant",
    description="An AI-powered assistant that answers questions based on predefined information",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(response_router, prefix="/api/v1", tags=["responses"])


@app.get("/")
async def root():
    """Root endpoint to check application status and connections."""
    status = {
        "status": "running",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "connections": {
            "database": "checking...",
            "openai": "checking...",
            "google_sheets": "checking...",
        },
    }

    # Check database connection
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        status["connections"]["database"] = "connected"
    except Exception as e:
        status["connections"]["database"] = f"error: {str(e)}"

    # Check OpenAI connection
    try:
        openai_service = OpenAIService()
        status["connections"]["openai"] = "configured"
    except Exception as e:
        status["connections"]["openai"] = f"error: {str(e)}"

    # Check Google Sheets connection
    try:
        sheets_service = GoogleSheetsService()
        sheets_service.get_sheet_data()
        status["connections"]["google_sheets"] = "connected"
    except Exception as e:
        status["connections"]["google_sheets"] = f"error: {str(e)}"

    return status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
