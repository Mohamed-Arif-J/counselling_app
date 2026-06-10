import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from .forms import MoodLogForm, JournalEntryForm, PHQ9Form, GAD7Form
from .models import MoodLog, JournalEntry, PsychoeducationArticle, PHQ9Response, GAD7Response
from .utils import intern3_analyze

# ========================================================================================
# MOOD TRACKING SYSTEM VIEWS (INTEGRATED SINGLE-PAGE STYLE)
# ========================================================================================

@login_required
def mood_checkin(request):
    if request.method == "POST":
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                mood_val = int(body.get('mood'))
                note_val = body.get('note', 'Dashboard Quick Log')
                
                MoodLog.objects.create(user=request.user, mood=mood_val, note=note_val)
                return JsonResponse({"success": True, "message": "Mood updated!"})
            except (ValueError, TypeError, json.JSONDecodeError):
                return JsonResponse({"success": False, "error": "Invalid format data"}, status=400)
        
        form = MoodLogForm(request.POST)
        if form.is_valid():
            mood_log = form.save(commit=False)
            mood_log.user = request.user
            mood_log.save()
            return redirect('patient_dashboard')
            
    else:
        form = MoodLogForm()
    
    return redirect('patient_dashboard')


@login_required
def mood_chart_data(request):
    days = int(request.GET.get("days", 7))
    cutoff = timezone.now() - timezone.timedelta(days=days)
    
    logs = MoodLog.objects.filter(user=request.user, created_at__gte=cutoff).order_by("created_at")

    data = {
        "labels": [log.created_at.strftime("%b %d") for log in logs],
        "moods": [log.mood for log in logs],
    }
    return JsonResponse(data)


@login_required
def mood_history(request):
    return redirect('patient_dashboard')


# ========================================================================================
# PRIVATE JOURNAL STORAGE WORKSPACES (CRUD + TEXT INTEGRATION API)
# ========================================================================================

@login_required
def journal_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        mood = request.POST.get('mood', 'neutral')

        if not title or not content:
            return JsonResponse({"success": False, "errors": "Title and content are required fields."}, status=400)

        entry = JournalEntry.objects.create(
            user=request.user,
            title=title,
            content=content
        )
        
        if hasattr(entry, 'mood'):
            entry.mood = mood

        analysis = intern3_analyze(entry.content)
        entry.sentiment = analysis.get("sentiment", "neutral")
        entry.confidence = analysis.get("confidence", 0.0)
        entry.save()

        local_now = timezone.localtime(entry.created_at)

        return JsonResponse({
            "success": True,
            "journal_id": entry.id,
            "sentiment": entry.sentiment,
            "confidence": entry.confidence,
            "created_at_date": local_now.strftime("%Y-%m-%d"),
            "created_at_time": local_now.strftime("%H:%M"),
            "context": getattr(entry, 'context', 'Standard baseline logged.'),
            "crisis_detected": getattr(request, "crisis_detected", False),
            "risk_level": getattr(request, "risk_level", "LOW"),
        })

    return redirect('journal_list')


@login_required
def journal_list(request):
    query = request.GET.get("q")
    date = request.GET.get("date")

    entries_queryset = JournalEntry.objects.filter(user=request.user).order_by('-created_at')

    if query:
        entries_queryset = entries_queryset.filter(title__icontains=query) | entries_queryset.filter(content__icontains=query)
    if date:
        entries_queryset = entries_queryset.filter(created_at__date=date)

    serialized_entries = []
    for entry in entries_queryset:
        local_dt = timezone.localtime(entry.created_at)
        
        serialized_entries.append({
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "sentiment": entry.sentiment or "neutral",
            "confidence": getattr(entry, 'confidence', None),
            "mood": getattr(entry, 'mood', 'neutral'),
            "created_at_date": local_dt.strftime("%Y-%m-%d"),
            "created_at_time": local_dt.strftime("%H:%M"),
            "context": getattr(entry, 'context', 'Standard baseline logged.')
        })

    return render(request, 'Journals.html', {'entries': serialized_entries})


@login_required
def journal_update(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)

    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        mood = request.POST.get('mood')

        if not title or not content:
            return JsonResponse({"success": False, "errors": "Title and content cannot be empty."}, status=400)

        entry.title = title
        entry.content = content
        if hasattr(entry, 'mood') and mood:
            entry.mood = mood

        analysis = intern3_analyze(entry.content)
        entry.sentiment = analysis.get("sentiment", "neutral")
        entry.confidence = analysis.get("confidence", 0.0)
        entry.save()

        local_now = timezone.localtime(entry.created_at)

        return JsonResponse({
            "success": True,
            "journal_id": entry.id,
            "sentiment": entry.sentiment,
            "confidence": entry.confidence,
            "created_at_date": local_now.strftime("%Y-%m-%d"),
            "created_at_time": local_now.strftime("%H:%M"),
            "context": getattr(entry, 'context', 'Standard baseline logged.'),
            "crisis_detected": getattr(request, "crisis_detected", False),
            "risk_level": getattr(request, "risk_level", "LOW"),
        })

    return redirect('journal_list')


@login_required
def journal_delete(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        return JsonResponse({"success": True, "message": "Deleted successfully"})
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)


# ========================================================================================
# PSYCHOEDUCATION RESOURCE DESKS (UNIFIED SINGLE-PAGE TAB SWITCHING VIEW)
# ========================================================================================

@login_required
def article_list(request):
    # 1. Fetch full global article dataset
    all_articles = PsychoeducationArticle.objects.all().order_by('-created_at')
    
    # 2. Analyze user diagnostics profile context to calculate clinical category targets
    phq9 = PHQ9Response.objects.filter(user=request.user).order_by("-created_at").first()
    gad7 = GAD7Response.objects.filter(user=request.user).order_by("-created_at").first()
    mood = MoodLog.objects.filter(user=request.user).order_by("-created_at").first()

    category = None
    if phq9 and phq9.score >= 10:
        category = "depression"
    elif gad7 and gad7.score >= 10:
        category = "anxiety"
    elif mood and mood.mood <= 2:
        category = "cbt"

    # 3. Filter personalized recommendations based on evaluated category tracking criteria
    if category:
        recommended_articles_queryset = PsychoeducationArticle.objects.filter(category=category).order_by('-created_at')
    else:
        recommended_articles_queryset = PsychoeducationArticle.objects.all().order_by('-created_at')

    # Helper serializer function to convert database rows safely to strict JSON layout blocks
    def parse_articles_to_dict(queryset):
        dataset_array = []
        for art in queryset:
            dataset_array.append({
                "id": art.id,
                "title": art.title,
                "content": art.content,
                "category_display": art.get_category_display() if hasattr(art, 'get_category_display') else art.category.title(),
                "thumbnail_url": art.thumbnail.url if art.thumbnail else "https://images.unsplash.com/photo-1518495973542-4542c06a5843?auto=format&fit=crop&w=800&q=80",
                "video_url": art.video_url or ""
            })
        return dataset_array

    context = {
        'all_articles_json': json.dumps(parse_articles_to_dict(all_articles)),
        'rec_articles_json': json.dumps(parse_articles_to_dict(recommended_articles_queryset)),
        'category': category
    }
    return render(request, 'Articles.html', context)


@login_required
def article_detail(request, pk):
    article = get_object_or_404(PsychoeducationArticle, pk=pk)
    return render(request, 'article_detail.html', {'article': article})


@login_required
def recommended_articles(request):
    # Backward compatibility redirect—automatically moves client paths back into unified tab view
    return redirect('article_list')


# ========================================================================================
# UNIFIED CLINICAL DIAGNOSTIC SCREENING SYSTEMS
# ========================================================================================

@login_required
def gad7_assessment(request):
    score = None
    
    if request.method == "POST":
        answers = {
            "q1": int(request.POST.get("q1", 0)),
            "q2": int(request.POST.get("q2", 0)),
            "q3": int(request.POST.get("q3", 0)),
            "q4": int(request.POST.get("q4", 0)),
            "q5": int(request.POST.get("q5", 0)),
            "q6": int(request.POST.get("q6", 0)),
            "q7": int(request.POST.get("q7", 0)),
        }
        score = sum(answers.values())
        GAD7Response.objects.create(user=request.user, answers=answers, score=score)

    responses = GAD7Response.objects.filter(user=request.user).order_by("-created_at")
    
    return render(request, "GAD7-Form.html", {
        "responses": responses,
        "score": score
    })


@login_required
def phq9_assessment(request):
    score = None
    if request.method == "POST":
        answers = {
            "q1": int(request.POST.get("q1", 0)),
            "q2": int(request.POST.get("q2", 0)),
            "q3": int(request.POST.get("q3", 0)),
            "q4": int(request.POST.get("q4", 0)),
            "q5": int(request.POST.get("q5", 0)),
            "q6": int(request.POST.get("q6", 0)),
            "q7": int(request.POST.get("q7", 0)),
            "q8": int(request.POST.get("q8", 0)),
            "q9": int(request.POST.get("q9", 0)),
        }
        score = sum(answers.values())
        PHQ9Response.objects.create(user=request.user, answers=answers, score=score)
        
    responses = PHQ9Response.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "PHQ9-Form.html", {
        "responses": responses,
        "score": score
    })


# ========================================================================================
# ACCESS CONTROLLER DESKS
# ========================================================================================

@login_required
def role_redirect(request):
    if request.user.role == "counsellor":
        return redirect("counsellor_dashboard")
    elif request.user.role == "admin":
        return redirect("admin_dashboard")
    elif request.user.role == "client":
        return redirect("client_dashboard")
    else:
        return redirect("patient_dashboard")