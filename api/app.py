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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to create DB tables, but don't fail if database is not available
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not connect to database: {e}")

# Include API routes
app.include_router(response_router, prefix="/api/v1", tags=["responses"])
app.include_router(passport_router, prefix="/api/v1", tags=["passport"])


@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    response = Response(status_code=200)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    response = Response(status_code=200)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


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
