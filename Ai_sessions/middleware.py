import json
from .crisis import detect_crisis
class CrisisDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        CRISIS_PATHS = [
            "/api/chat/",
            "/mood_tracker/journal/create/",
        ]
        is_journal_update = (
            request.path.startswith("/mood_tracker/journal/")
            and request.path.endswith("/update/")
        )
        is_session_note = (
            request.path.startswith("/appointments/notes/")
            and not request.path.endswith("/ai-summary/")
        )
        should_check = (
            request.method in ["POST", "PUT", "PATCH"]
            and (
                request.path in CRISIS_PATHS
                or is_journal_update
                or is_session_note
            )
        )
        if should_check:
            try:
                body = json.loads(
                    request.body.decode("utf-8")
                )
                text = (
                    body.get("text")
                    or body.get("content")
                    or body.get("message")
                    or body.get("notes")
                )
                if text:
                    result = json.loads(
                        detect_crisis(text)
                    )
                    request.crisis_detected = result.get(
                        "crisis",
                        False
                    )
                    request.risk_level = result.get(
                        "risk_level",
                        "LOW"
                    )
                else:
                    request.crisis_detected = False
                    request.risk_level = "LOW"
            except Exception:
                request.crisis_detected = False
                request.risk_level = "LOW"
        response = self.get_response(request)
        return response