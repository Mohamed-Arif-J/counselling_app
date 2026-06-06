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

        

PHQ9_CHOICES = [
    (0, "Not at all"),
    (1, "Several days"),
    (2, "More than half the days"),
    (3, "Nearly every day"),
]

class PHQ9Form(forms.Form):
    q1 = forms.ChoiceField(choices=PHQ9_CHOICES, widget=forms.RadioSelect, label="Little interest or pleasure in doing things")
    q2 = forms.ChoiceField(choices=PHQ9_CHOICES, widget=forms.RadioSelect, label="Feeling down, depressed, or hopeless")
    q3 = forms.ChoiceField(choices=PHQ9_CHOICES, widget=forms.RadioSelect, label="Trouble falling or staying asleep, or sleeping too much")
    q4 = forms.ChoiceField(choices=PHQ9_CHOICES, widget=forms.RadioSelect, label="Feeling tired or having little energy")
    q5 = forms.ChoiceField(choices=PHQ9_CHOICES, widget=forms.RadioSelect, label="Poor appetite or overeating")
    q6 = forms.ChoiceField(choices=PHQ9_CHOICES, widget=forms.RadioSelect, label="Feeling bad about yourself — or that you are a failure or have let yourself or your family down")
    q7 = forms.ChoiceField(choices=PHQ9_CHOICES, widget=forms.RadioSelect, label="Trouble concentrating on things, such as reading the newspaper or watching television")
    q8 = forms.ChoiceField(choices=PHQ9_CHOICES, widget=forms.RadioSelect, label="Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual")
    q9 = forms.ChoiceField(choices=PHQ9_CHOICES, widget=forms.RadioSelect, label="Thoughts that you would be better off dead, or of hurting yourself in some way")


GAD7_CHOICES = PHQ9_CHOICES  # same scale

class GAD7Form(forms.Form):
    q1 = forms.ChoiceField(choices=GAD7_CHOICES, widget=forms.RadioSelect, label="Feeling nervous, anxious, or on edge")
    q2 = forms.ChoiceField(choices=GAD7_CHOICES, widget=forms.RadioSelect, label="Not being able to stop or control worrying")
    q3 = forms.ChoiceField(choices=GAD7_CHOICES, widget=forms.RadioSelect, label="Worrying too much about different things")
    q4 = forms.ChoiceField(choices=GAD7_CHOICES, widget=forms.RadioSelect, label="Trouble relaxing")
    q5 = forms.ChoiceField(choices=GAD7_CHOICES, widget=forms.RadioSelect, label="Being so restless that it is hard to sit still")
    q6 = forms.ChoiceField(choices=GAD7_CHOICES, widget=forms.RadioSelect, label="Becoming easily annoyed or irritable")
    q7 = forms.ChoiceField(choices=GAD7_CHOICES, widget=forms.RadioSelect, label="Feeling afraid as if something awful might happen")



