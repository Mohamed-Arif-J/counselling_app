from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import ChatSerializer, SentimentSerializer
from .chatbot import get_ai_response
from .sentiment import analyze_sentiment
import json
from google.api_core.exceptions import ResourceExhausted
from .serializer import CrisisSerializer
from .crisis import detect_crisis
from .matching import match_therapist
from .serializer import MatchSerializer


@api_view(["POST"])
def chatbot(request):
    serializer = ChatSerializer(data=request.data)

    if serializer.is_valid():
        message = serializer.validated_data["message"]
        reply = get_ai_response(message)
        return Response({"reply": reply})
    return Response(serializer.errors, status=400)

@api_view(["POST"])
def sentiment(request):
    serializer = SentimentSerializer(data=request.data)
    if serializer.is_valid():
        text = serializer.validated_data["text"]
        try:
            result = analyze_sentiment(text)
            return Response(json.loads(result))
        except ResourceExhausted:
            return Response(
                {"detail": "AI service temporarily unavailable. Please try again later or contact support."},
                status=503
            )

@api_view(["POST"])
def crisis(request):
    serializer = CrisisSerializer(data=request.data)
    if serializer.is_valid():
        text = serializer.validated_data["text"]
        result = detect_crisis(text)
        return Response(json.loads(result))
    return Response(serializer.errors, status=400)

@api_view(["POST"])
def therapist_match(request):
    serializer = MatchSerializer(data=request.data)
    if serializer.is_valid():
        text = serializer.validated_data["text"]
        result = match_therapist(text)
        return Response(json.loads(result))
    return Response(serializer.errors, status=400)