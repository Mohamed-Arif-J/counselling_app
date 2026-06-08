from django.urls import path
from .views import chatbot, sentiment, crisis, therapist_match, summarize

urlpatterns = [
    path("chat/", chatbot),
    path("sentiment/", sentiment),
    path("crisis/", crisis),
    path("match/", therapist_match),
    path("summarize/", summarize),
]