# config.py
# Simple configuration for the Smart Habit project

# SQLite file
DB_NAME = "habits.db"

# Gemini API - GET YOUR NEW KEY FROM: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = "AIzaSyAj4k7AGgFRvSay_HbtaDzEBNhO4GEdgxs"  # Replace with new key

# Updated model name (newer versions available)
GEMINI_MODEL = "gemini-1.5-flash"  # Changed from gemini-pro

# App behavior toggles
ENABLE_AI = True
ENABLE_PDF_EXPORT = True