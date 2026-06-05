from django.db import models
from django.contrib.auth.models import User

class MoodLog(models.Model):
    MOOD_CHOICES = [
        (1, "😢 Very Low"),
        (2, "😟 Low"),
        (3, "😐 Neutral"),
        (4, "🙂 Good"),
        (5, "😄 Excellent"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.IntegerField(choices=MOOD_CHOICES)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mood} ({self.created_at.date()})"

