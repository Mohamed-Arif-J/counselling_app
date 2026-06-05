from django.contrib import admin

from .models import JournalEntry, MoodLog

# Register your models here.
admin.site.register(MoodLog)
admin.site.register(JournalEntry)