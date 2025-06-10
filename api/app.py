import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from dotenv import load_dotenv

from api.database.database import engine, Base, get_db
from api.routes.response_routes import router as response_router
from api.routes.passport_routes import router as passport_router
from api.services.openai_service import OpenAIService
from api.services.google_sheets_service import GoogleSheetsService
from api.services.speech_service import SpeechService

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

# Load environment variables
load_dotenv(override=True)

# Validate required environment variables
REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "KNOWLEDGE_SHEET_ID",
]  # Removed POSTGRES_PASSWORD
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

# Initialize FastAPI app
app = FastAPI(
    title="Airport AI Assistant",
    description="An AI-powered assistant that answers questions based on predefined information",
    version="1.0.0",
    redirect_slashes=False,
)

origins = [
    "http://localhost:3000",  # برای توسعه لوکال فرانت‌اند
    "http://localhost:4000",  # اگر بک‌اند و فرانت‌اند در یک پورت با هم تست می‌شوند (کمتر رایج)
    "https://next-livekit-streaming.vercel.app",  # **اینجا باید آدرس دیپلوی شده فرانت‌اند روی Vercel را وارد کنید**
    # می‌توانید wildcard هم استفاده کنید اگر دامنه ثابت نیست، اما توصیه نمی‌شود
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # لیست دامنه‌هایی که اجازه دسترسی دارند
    allow_credentials=True,  # اجازه ارسال کوکی‌ها در Cross-Origin
    allow_methods=["*"],  # اجازه تمام متدها (GET, POST, PUT, DELETE, etc)
    allow_headers=["*"],  # اجازه تمام هدرها
)
# # CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Try to create DB tables, but don't fail if database is not available
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not connect to database: {e}")

# Include API routes
app.include_router(response_router, prefix="/api/v1", tags=["responses"])
app.include_router(passport_router, prefix="/api/v1", tags=["passport"])


@app.get("/")
async def root():
    """Check application and services status."""
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

    # DB connection test
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        status["connections"]["database"] = "connected"
    except Exception as e:
        status["connections"]["database"] = f"not available: {e}"

    # OpenAI test
    try:
        _ = OpenAIService()
        status["connections"]["openai"] = "configured"
    except Exception as e:
        status["connections"]["openai"] = f"error: {e}"

    # Google Sheets test
    try:
        sheets_service = GoogleSheetsService()
        sheets_service.get_sheet_data()
        status["connections"]["google_sheets"] = "connected"
    except Exception as e:
        status["connections"]["google_sheets"] = f"error: {e}"

    return status
