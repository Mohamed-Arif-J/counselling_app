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
You are a crisis detection classifier.

Your job is to determine whether the given text
contains suicidal thoughts, self-harm intent,
or an immediate mental health crisis.

If the text indicates:
- suicide
- self harm
- ending life
- wanting to die
- hurting oneself
- immediate danger

Return ONLY this JSON:

{
    "crisis": true,
    "risk_level": "HIGH"
}

Otherwise return ONLY:

{
    "crisis": false,
    "risk_level": "LOW"
}

Rules:
- Return ONLY raw JSON.
- Do NOT use markdown.
- Do NOT wrap JSON inside ```json blocks.
- Do NOT explain your answer.
- Do NOT add extra fields.
"""
)


def detect_crisis(text):

    try:
        response = model.generate_content(text)

        cleaned_response = (
            response.text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return cleaned_response

    except ResourceExhausted:
        return """
{
    "crisis": false,
    "risk_level": "UNKNOWN"
}
"""

    except Exception:
        return """
{
    "crisis": false,
    "risk_level": "UNKNOWN"
}
"""