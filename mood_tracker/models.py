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


class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Integration fields
    sentiment = models.CharField(max_length=50, blank=True, null=True)
    confidence = models.IntegerField(blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class PsychoeducationArticle(models.Model):
    CATEGORY_CHOICES = [
        ("anxiety", "Anxiety"),
        ("depression", "Depression"),
        ("cbt", "CBT"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="cbt")
    video_url = models.URLField(blank=True, null=True)   # optional video link
    exercise = models.TextField(blank=True, null=True)   # optional exercise instructions
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title




class PHQ9Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answers = models.JSONField()   # store answers as {q1:2, q2:1, ...}
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PHQ-9 ({self.user.username}) - {self.score}"


class GAD7Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answers = models.JSONField()
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GAD-7 ({self.user.username}) - {self.score}"

