

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
from .forms import MoodLogForm, JournalEntryForm, PHQ9Form, GAD7Form
from .models import MoodLog, JournalEntry, PsychoeducationArticle, PHQ9Response, GAD7Response
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .utils import intern3_analyze



from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from .models import MoodLog






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
            entry.user = User.objects.first()
            entry.save()

            # 🔗 Call Intern 3’s API
            analysis = intern3_analyze(entry.content)
            entry.sentiment = analysis.get("sentiment")
            entry.confidence = analysis.get("confidence")
            entry.save()

            return redirect('journal_list')
    else:
        form = JournalEntryForm()
    return render(request, 'journal_create.html', {'form': form})

# Read + Search

def journal_list(request):
    query = request.GET.get("q")
    date = request.GET.get("date")  # new filter

    entries = JournalEntry.objects.filter(user=User.objects.first()).order_by('-created_at')

    if query:
        entries = entries.filter(title__icontains=query) | entries.filter(content__icontains=query)

    if date:
        # Expecting format YYYY-MM-DD
        entries = entries.filter(created_at__date=date)

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
            entry.sentiment = analysis.get("sentiment")
            entry.confidence = analysis.get("confidence")
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



# List all articles
def article_list(request):
    articles = PsychoeducationArticle.objects.all().order_by('-created_at')
    return render(request, 'article_list.html', {'articles': articles})

# View single article
def article_detail(request, pk):
    article = get_object_or_404(PsychoeducationArticle, pk=pk)
    return render(request, 'article_detail.html', {'article': article})




def phq9_assessment(request):
    if request.method == "POST":
        form = PHQ9Form(request.POST)
        if form.is_valid():
            answers = {q: int(val) for q, val in form.cleaned_data.items()}
            score = sum(answers.values())
            PHQ9Response.objects.create(user=request.user, answers=answers, score=score)
            return render(request, "phq9_result.html", {"score": score})
    else:
        form = PHQ9Form()
    return render(request, "phq9_form.html", {"form": form})


def gad7_assessment(request):
    if request.method == "POST":
        form = GAD7Form(request.POST)
        if form.is_valid():
            answers = {q: int(val) for q, val in form.cleaned_data.items()}
            score = sum(answers.values())
            GAD7Response.objects.create(user=request.user, answers=answers, score=score)
            return render(request, "gad7_result.html", {"score": score})
    else:
        form = GAD7Form()
    return render(request, "gad7_form.html", {"form": form})


def phq9_history(request):
    responses = PHQ9Response.objects.filter(user=request.user).order_by("created_at")
    return render(request, "phq9_history.html", {"responses": responses})


def gad7_history(request):
    responses = GAD7Response.objects.filter(user=request.user).order_by("created_at")
    return render(request, "gad7_history.html", {"responses": responses})


def recommended_articles(request):
    if not request.user.is_authenticated:
        return render(request, "recommended.html", {"articles": [], "message": "Please log in to see recommendations."})

    # Get latest scores
    phq9 = PHQ9Response.objects.filter(user=request.user).order_by("-created_at").first()
    gad7 = GAD7Response.objects.filter(user=request.user).order_by("-created_at").first()
    mood = MoodLog.objects.filter(user=request.user).order_by("-created_at").first()

    category = None

    # Map scores/mood to categories
    if phq9 and phq9.score >= 10:
        category = "depression"
    elif gad7 and gad7.score >= 10:
        category = "anxiety"
    elif mood and mood.mood <= 2:  # very low or low mood
        category = "cbt"

    articles = PsychoeducationArticle.objects.filter(category=category) if category else []
    return render(request, "recommended.html", {"articles": articles, "category": category})






def mood_trend(request, days=7):
    cutoff = timezone.now() - timedelta(days=days)
    logs = MoodLog.objects.filter(user=request.user, created_at__gte=cutoff).order_by("created_at")
    return render(request, "mood_trend.html", {"logs": logs, "days": days})


