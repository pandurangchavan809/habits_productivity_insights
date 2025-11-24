# recommendations.py
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
import pandas as pd

def get_gemini_reco(df: pd.DataFrame, mode: str = "student") -> str:
    """
    Generate AI recommendations with better error handling
    """
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Prepare data summary
        avg_sleep = df['sleep_hours'].mean()
        avg_study = df['study_hours'].mean()
        avg_productivity = df['productivity_score'].mean()
        
        # Create prompt
        prompt = f"""
        Analyze this {mode}'s habit data and provide 3-5 actionable recommendations:
        
        Average Sleep: {avg_sleep:.1f} hours
        Average Study/Work: {avg_study:.1f} hours
        Average Productivity Score: {avg_productivity:.1f}/10
        Total Days Tracked: {len(df)}
        
        Most common mood: {df['mood'].mode()[0] if 'mood' in df.columns and not df['mood'].empty else 'N/A'}
        
        Provide:
        1. Key observations about their habits
        2. Specific, actionable recommendations
        3. Productivity optimization tips
        
        Keep it concise, encouraging, and practical.
        """
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        
        # Specific error messages
        if "API_KEY_INVALID" in error_msg or "expired" in error_msg.lower():
            return """
            ❌ **API Key Error**: Your Gemini API key has expired or is invalid.
            
            **To fix this:**
            1. Visit https://aistudio.google.com/app/apikey
            2. Create a new API key
            3. Update GEMINI_API_KEY in config.py
            
            The app will continue to work without AI recommendations.
            """
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return """
            ⚠️ **Rate Limit**: You've exceeded the free tier quota.
            
            **Options:**
            1. Wait a few minutes and try again
            2. Upgrade to a paid plan
            3. The app works fine without AI - check the Analytics page!
            """
        else:
            return f"""
            ⚠️ **AI Service Unavailable**
            
            Error details: {error_msg}
            
            Don't worry! You can still:
            - View all your analytics in the Analytics page
            - Use ML predictions and clustering
            - Track and visualize your habits
            """