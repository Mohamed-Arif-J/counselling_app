import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""
You are a therapist matching system.

Based on the user's description,
choose ONE specialization from:

- Anxiety
- Depression
- Stress Management
- Relationship Counseling
- Trauma
- Family Therapy
- General Counseling

Return ONLY JSON.

Example:

{
    "specialization":"Anxiety"
}

Do not explain.
Do not use markdown.
Do not add extra fields.
"""
)

def match_therapist(text):
    try:
        response = model.generate_content(text)
        cleaned = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        return cleaned
    except ResourceExhausted as e:
        print(e)
        return """
{
    "specialization":"General Counseling"
}
"""
    except Exception as e:
        print(type(e))
        print(e)
        return """
{
    "specialization":"General Counseling"
}
"""