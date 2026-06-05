import requests

def intern3_analyze(text):
    url = "http://127.0.0.1:8000/api/sentiment/"  # Intern 3’s endpoint
    payload = {"text": text}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"sentiment": "ERROR", "confidence": 0}
    except Exception as e:
        return {"sentiment": "ERROR", "confidence": 0}
