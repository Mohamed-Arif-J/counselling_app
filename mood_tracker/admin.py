from django.contrib import admin

from .models import JournalEntry, MoodLog, PHQ9Response,PsychoeducationArticle,GAD7Response
 

# Register your models here.
admin.site.register(MoodLog)
admin.site.register(JournalEntry)
admin.site.register(PsychoeducationArticle)
admin.site.register(PHQ9Response)
admin.site.register(GAD7Response)




