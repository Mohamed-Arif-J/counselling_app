from django.urls import path
from .views import chatbot, sentiment
urlpatterns = [
    path("chat/", chatbot),
    path("sentiment/", sentiment),
]