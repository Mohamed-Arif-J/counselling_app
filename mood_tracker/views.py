

# Create your views here.
# from django.shortcuts import render, redirect
# from .forms import MoodLogForm
# from .models import MoodLog
# from django.contrib.auth.decorators import login_required


# from django.http import JsonResponse
# from django.utils import timezone



# # @login_required
# def mood_checkin(request):
#     if request.method == "POST":
#         form = MoodLogForm(request.POST)
#         if form.is_valid():
#             mood_log = form.save(commit=False)
#             mood_log.user = request.user
#             mood_log.save()
#             return redirect('mood_history')
#     else:
#         form = MoodLogForm()
#     return render(request, 'checkin.html', {'form': form})

# # @login_required
# def mood_history(request):
#     logs = MoodLog.objects.filter(user=request.user).order_by('-created_at')
#     return render(request, 'history.html', {'logs': logs})



# # @login_required
# def mood_chart_data(request):
#     days = int(request.GET.get("days", 7)) 
#     cutoff = timezone.now() - timezone.timedelta(days=days)
#     logs = MoodLog.objects.filter(user=request.user, created_at__gte=cutoff).order_by("created_at")

#     data = {
#         "labels": [log.created_at.strftime("%b %d") for log in logs],
#         "moods": [log.mood for log in logs],
#     }
#     return JsonResponse(data)




from django.shortcuts import render, redirect, get_object_or_404

from .forms import MoodLogForm
from .models import MoodLog
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User

from .models import JournalEntry
from .forms import JournalEntryForm


def mood_checkin(request):
    if request.method == "POST":
        form = MoodLogForm(request.POST)
        if form.is_valid():
            mood_log = form.save(commit=False)
            # TEMP: assign to first user until auth is ready
            mood_log.user = User.objects.first()
            mood_log.save()
            return redirect('mood_history')
    else:
        form = MoodLogForm()
    return render(request, 'checkin.html', {'form': form})

def mood_history(request):
    # TEMP: show logs for first user
    logs = MoodLog.objects.filter(user=User.objects.first()).order_by('-created_at')
    return render(request, 'history.html', {'logs': logs})

def mood_chart_data(request):
    days = int(request.GET.get("days", 7))
    cutoff = timezone.now() - timezone.timedelta(days=days)
    # TEMP: filter logs for first user
    logs = MoodLog.objects.filter(user=User.objects.first(), created_at__gte=cutoff).order_by("created_at")

    data = {
        "labels": [log.created_at.strftime("%b %d") for log in logs],
        "moods": [log.mood for log in logs],
    }
    return JsonResponse(data)






# Create
def journal_create(request):
    if request.method == "POST":
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = User.objects.first()  # TEMP until auth ready
            entry.save()

            # 🔗 Call Intern 3’s tool
            analysis = intern3_analyze(entry.content)
            entry.sentiment = analysis["score"]
            entry.recommendation = analysis["suggestion"]
            entry.save()

            return redirect('journal_list')
    else:
        form = JournalEntryForm()
    return render(request, 'journal_create.html', {'form': form})

# Read + Search
def journal_list(request):
    query = request.GET.get("q")
    entries = JournalEntry.objects.filter(user=User.objects.first()).order_by('-created_at')
    if query:
        entries = entries.filter(title__icontains=query) | entries.filter(content__icontains=query)
    return render(request, 'journal_list.html', {'entries': entries})

# Update
def journal_update(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk, user=User.objects.first())
    if request.method == "POST":
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save()

            # 🔗 Re‑analyze after update
            analysis = intern3_analyze(entry.content)
            entry.sentiment = analysis["score"]
            entry.recommendation = analysis["suggestion"]
            entry.save()

            return redirect('journal_list')
    else:
        form = JournalEntryForm(instance=entry)
    return render(request, 'journal_update.html', {'form': form})

# Delete
def journal_delete(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk, user=User.objects.first())
    if request.method == "POST":
        entry.delete()
        return redirect('journal_list')
    return render(request, 'journal_delete.html', {'entry': entry})
