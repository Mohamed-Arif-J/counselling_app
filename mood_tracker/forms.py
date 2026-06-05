from django import forms
from .models import JournalEntry, MoodLog

class MoodLogForm(forms.ModelForm):
    class Meta:
        model = MoodLog
        fields = ['mood', 'note']
        widgets = {
            'mood': forms.RadioSelect(),
            'note': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional note...'}),
        }


        

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['title', 'content']


