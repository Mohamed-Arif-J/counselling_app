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
You are a clinical note summarizer.

Summarize the provided text in 1-3 concise sentences.

Rules:
- Be objective.
- Do not diagnose.
- Do not invent information.
- Keep important emotional themes.
- Return ONLY JSON.

Example:

{
    "summary":"Client reports anxiety related to work and family stress."
}

Do not use markdown.
Do not explain.
"""
)


def summarize_text(text):

    try:
        response = model.generate_content(text)

        cleaned = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return cleaned

    except ResourceExhausted:
        return """
{
    "summary":"Summary temporarily unavailable."
}
"""

    except Exception:
        return """
{
    "summary":"Summary temporarily unavailable."
}
"""