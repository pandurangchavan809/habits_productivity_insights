## Local Run :-

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

# # Notes:
# # - Create a `.env` file at the project root and add `GEMINI_API_KEY=your_key_here`.
# # - Example `.env.example` is provided in the repository to help with setup.


# ### for Streamlit Cloud :-
# # config.py
# # config.py
# import os
# from dotenv import load_dotenv

# # Try Streamlit secrets (only available in deployment)
# try:
#     import streamlit as st
#     USE_STREAMLIT = True
# except:
#     USE_STREAMLIT = False

# # -----------------------------
# # 1. LOAD FROM STREAMLIT SECRETS (DEPLOYED MODE)
# # -----------------------------
# if USE_STREAMLIT and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
#     DB_NAME = st.secrets.get("DB_NAME", "habits.db")

#     GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
#     GEMINI_MODEL = st.secrets.get("GEMINI_MODEL", "gemini-2.5-flash")

#     ENABLE_AI = str(st.secrets.get("ENABLE_AI", "true")).lower() == "true"
#     ENABLE_PDF_EXPORT = str(st.secrets.get("ENABLE_PDF_EXPORT", "true")).lower() == "true"

# else:
#     # -----------------------------
#     # 2. FALLBACK: LOCAL .env FILE (DEV MODE)
#     # -----------------------------
#     load_dotenv()

#     DB_NAME = os.getenv("DB_NAME", "habits.db")
#     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
#     GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

#     def _bool_env(name: str, default: bool = False) -> bool:
#         v = os.getenv(name)
#         if v is None:
#             return default
#         return str(v).lower() in ("1", "true", "yes", "on")

#     ENABLE_AI = _bool_env("ENABLE_AI", True)
#     ENABLE_PDF_EXPORT = _bool_env("ENABLE_PDF_EXPORT", True)

# # If no API key, disable AI safely
# if not GEMINI_API_KEY:
#     ENABLE_AI = False
