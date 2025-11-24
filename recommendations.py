# recommendations.py
"""Generate AI recommendations using Google Gemini.

This module first tries the new `google-genai` SDK (recommended):
  pip install -U google-genai
and the import `from google import genai`.

If that is not available it falls back to the older
`google.generativeai` package and its `GenerativeModel` API.
"""
import pandas as pd
import traceback
from config import GEMINI_API_KEY, GEMINI_MODEL

import importlib

# Dynamically import the new SDK (`google-genai`) if available. We use
# importlib to avoid static import checks (Pylance) complaining when the
# package isn't installed in the active interpreter.
genai_v2 = None
NEW_GENAI_AVAILABLE = False
try:
    # Try module path `google.genai` first
    genai_v2 = importlib.import_module('google.genai')
    NEW_GENAI_AVAILABLE = True
except Exception:
    try:
        # Fallback: the `google` package may expose `genai` as an attribute
        mod_google = importlib.import_module('google')
        genai_v2 = getattr(mod_google, 'genai', None)
        NEW_GENAI_AVAILABLE = genai_v2 is not None
    except Exception:
        genai_v2 = None
        NEW_GENAI_AVAILABLE = False

# Dynamically import the older `google.generativeai` package if present
genai_v1 = None
OLD_GENAI_AVAILABLE = False
try:
    genai_v1 = importlib.import_module('google.generativeai')
    OLD_GENAI_AVAILABLE = True
except Exception:
    genai_v1 = None
    OLD_GENAI_AVAILABLE = False


def get_gemini_reco(df: pd.DataFrame, mode: str = "student") -> str:
    """
    Generate AI recommendations using the official Gemini API format.
    Includes full error handling, valid model usage, and stable response parsing.
    """

    # ----------------------------------------------------
    # 1. API key validation
    # ----------------------------------------------------
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
        return """
        ❌ **Gemini API key missing.**

        Add your key inside `.env`:

        GEMINI_API_KEY=your_key_here
        GEMINI_MODEL=gemini-1.5-flash

        Restart the app after adding the key.
        """

    # ----------------------------------------------------
    # 2. Configure Gemini (only needed for the legacy client)
    # The new `google-genai` client (`genai_v2`) uses `Client()` and reads the
    # API key from the environment automatically. Only call `configure` when
    # `google.generativeai` (legacy) is present.
    # ----------------------------------------------------
    try:
        if OLD_GENAI_AVAILABLE and genai_v1 is not None:
            genai_v1.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        return f"❌ Failed to configure legacy Gemini client: {str(e)}"

    # ----------------------------------------------------
    # 3. Prepare Data Summary
    # ----------------------------------------------------
    try:
        avg_sleep = float(df['sleep_hours'].mean()) if 'sleep_hours' in df else 0
        avg_study = float(df['study_hours'].mean()) if 'study_hours' in df else 0
        avg_prod = float(df['productivity_score'].mean()) if 'productivity_score' in df else 0
        mood = df['mood'].mode()[0] if 'mood' in df and not df['mood'].empty else "N/A"
        total_days = len(df)
    except Exception as e:
        return f"❌ Error reading dataframe: {str(e)}"

    # ----------------------------------------------------
    # 4. Build Prompt (Optimized)
    # ----------------------------------------------------
    prompt = f"""
    Analyze this {mode}'s habit and productivity dataset and provide clear, highly actionable insights.

    === User Habit Summary ===
    • Average Sleep: {avg_sleep:.1f} hrs/day
    • Average Study/Work: {avg_study:.1f} hrs/day
    • Average Productivity Score: {avg_prod:.1f}/10
    • Total Days Tracked: {total_days}
    • Most Common Mood: {mood}

    === Requirements ===
    1. Provide 3–5 key observations (specific to the numbers).
    2. Give 3–5 actionable recommendations they can apply today.
    3. Provide 2 productivity optimization tips backed by behavioral science.
    4. Keep format clean and concise.

    Respond in a structured bullet-point format.
    """

    # ----------------------------------------------------
    # 5. Generate Response (try new SDK first, then fallback)
    # ----------------------------------------------------
    last_exception = None

    # Try new google-genai client (preferred)
    if NEW_GENAI_AVAILABLE:
        try:
            # Client reads GEMINI_API_KEY from environment automatically
            client = genai_v2.Client()
            resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            # Try common response shapes
            if hasattr(resp, 'text') and resp.text:
                return resp.text
            # candidates/content fallbacks
            if hasattr(resp, 'candidates') and resp.candidates:
                try:
                    cand = resp.candidates[0]
                    if hasattr(cand, 'content'):
                        return cand.content
                    if hasattr(cand, 'text'):
                        return cand.text
                except Exception:
                    pass
            return str(resp)
        except Exception as e:
            last_exception = e

    # Fallback to older package (google.generativeai)
    if OLD_GENAI_AVAILABLE:
        try:
            # older package uses configure + GenerativeModel
            genai_v1.configure(api_key=GEMINI_API_KEY)
            model = genai_v1.GenerativeModel(model_name=GEMINI_MODEL)
            response = model.generate_content(prompt)
            text = getattr(response, 'text', None)
            if text:
                return text
            return str(response)
        except Exception as e:
            last_exception = e

    # No client succeeded — provide helpful diagnostics
    err_msg = str(last_exception) if last_exception else 'No compatible Gemini SDK found.'
    low = err_msg.lower()
    if 'quota' in low or 'rate' in low or 'limit' in low:
        return (
            "⚠️ **Gemini Rate Limit / Quota Error**\n\n"
            "Your key appears valid but has exceeded quota or rate limits.\n"
            "Options:\n"
            "1) Wait and retry later.\n"
            "2) Check Google Cloud/Gemini quotas and billing.\n"
            "3) Generate a new API key or upgrade your plan.\n\n"
            f"Raw error: {err_msg}"
        )

    if 'invalid' in low or 'unauthorized' in low or 'api key' in low:
        return (
            "❌ **Authentication Error**\n\n"
            "Gemini rejected the API key.\n"
            "Ensure `.env` contains `GEMINI_API_KEY` with no quotes or extra whitespace.\n"
            "Verify the key is active and has necessary permissions.\n\n"
            f"Raw error: {err_msg}"
        )

    # Generic fallback
    tb = traceback.format_exc()
    return (
        "⚠️ **Gemini API Error**\n\n"
        "The app attempted both the new and old Gemini clients but none returned a usable response.\n"
        "Troubleshoot:\n"
        "- Install the new SDK: `pip install --upgrade google-genai`\n"
        "- Or install the legacy package: `pip install --upgrade google-generativeai`\n"
        "- Ensure `GEMINI_API_KEY` in `.env` is correct (no extra newline).\n"
        "- Try different `GEMINI_MODEL` values like `gemini-1.5` or `gemini-2.5-flash`.\n\n"
        f"Last error: {err_msg}\n\nTraceback:\n{tb}"
    )
