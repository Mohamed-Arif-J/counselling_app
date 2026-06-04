

# Create your views here.
from django.shortcuts import render, redirect
from .forms import MoodLogForm
from .models import MoodLog
from django.contrib.auth.decorators import login_required

@login_required
def mood_checkin(request):
    if request.method == "POST":
        form = MoodLogForm(request.POST)
        if form.is_valid():
            mood_log = form.save(commit=False)
            mood_log.user = request.user
            mood_log.save()
            return redirect('mood_history')
    else:
        form = MoodLogForm()
    return render(request, 'mood/checkin.html', {'form': form})

@login_required
def mood_history(request):
    logs = MoodLog.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'mood/history.html', {'logs': logs})

