# config.py
# Configuration loaded from environment (use a `.env` file in development)
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite file (default)
DB_NAME = os.getenv("DB_NAME", "habits.db")

# Gemini API - set this in your `.env` file (do NOT commit your real key)
# Get a key: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gemini model (can be overridden in .env)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def _bool_env(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).lower() in ("1", "true", "yes", "on")

# Toggle AI and PDF export via environment variables
ENABLE_AI = _bool_env("ENABLE_AI", True)
ENABLE_PDF_EXPORT = _bool_env("ENABLE_PDF_EXPORT", True)

# If no API key configured, disable AI to avoid runtime errors
if not GEMINI_API_KEY:
    ENABLE_AI = False

# Notes:
# - Create a `.env` file at the project root and add `GEMINI_API_KEY=your_key_here`.
# - Example `.env.example` is provided in the repository to help with setup.