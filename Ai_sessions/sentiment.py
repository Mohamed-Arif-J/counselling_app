import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""
You are a sentiment classifier.

Return ONLY valid JSON.

Format:
{
    "sentiment":"POSITIVE|NEGATIVE|NEUTRAL",
    "confidence":95
}

Do not explain anything.
Do not add markdown.
Do not add extra text.
"""
)


def analyze_sentiment(text):
    response = model.generate_content(text)
    return response.text