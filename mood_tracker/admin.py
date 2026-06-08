from django.contrib import admin

from .models import JournalEntry, MoodLog, PHQ9Response,PsychoeducationArticle,GAD7Response,CustomUser
 

# Register your models here.
admin.site.register(MoodLog)
admin.site.register(JournalEntry)
admin.site.register(PsychoeducationArticle)
admin.site.register(PHQ9Response)
admin.site.register(GAD7Response)
admin.site.register(CustomUser)




