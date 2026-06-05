from django.contrib import admin

from .models import MoodLog,JournalEntry

# Register your models here.
admin.site.register(MoodLog)
admin.site.register(JournalEntry)
