from rest_framework.decorators import api_view
from rest_framework.response import Response
from google.api_core.exceptions import ResourceExhausted

from .serializer import ChatSerializer
from .chatbot import get_ai_response


@api_view(["POST"])
def chatbot(request):
    serializer = ChatSerializer(data=request.data)

    if serializer.is_valid():
        message = serializer.validated_data["message"]
        reply = get_ai_response(message)
        return Response({"reply": reply})
    return Response(serializer.errors, status=400)