from django.urls import path
from .views import chatbot, sentiment, crisis

urlpatterns = [
    path("chat/", chatbot),
    path("sentiment/", sentiment),
    path("crisis/", crisis),
]