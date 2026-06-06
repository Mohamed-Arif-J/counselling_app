from django.contrib import admin

from .models import JournalEntry, MoodLog,PsychoeducationArticle
 

# Register your models here.
admin.site.register(MoodLog)
admin.site.register(JournalEntry)
admin.site.register(PsychoeducationArticle)




