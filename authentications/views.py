from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import User, PatientProfile, TherapistProfile
from .helpers import normalize_phone_number, parse_date_value
from mood_tracker.models import MoodLog, PsychoeducationArticle
from appointments.models import Appointment, SessionNote

# ========================================================================================
# SYSTEM SECURITY PERMISSION CHECK HELPERS
# ========================================================================================

def is_system_administrator(user):
    """
    Verifies user authentication state and structural workspace administration roles.
    """
    return user.is_authenticated and (user.role == "admin" or user.is_superuser)


# ========================================================================================
# ACCOUNT SIGN-UP & GATEWAY LIFECYCLE CONTROLLERS
# ========================================================================================

@csrf_exempt
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")
        password = request.POST.get("password")
        phone_number = normalize_phone_number(phone_number)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'register.html')

        if (
            PatientProfile.objects.filter(phone_number=phone_number).exists()
            or
            TherapistProfile.objects.filter(phone_number=phone_number).exists()
        ):
            messages.error(request, "Phone number already exists")
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role="patient" # Default self-registration role hook
        )

        user.patientprofile.phone_number = phone_number
        user.patientprofile.save()
        return redirect('login')
        
    return render(request, 'register.html')


@csrf_exempt
def login_view(request):
    if request.method == "POST":  
        login_id = request.POST.get("login_id")
        password = request.POST.get("password")

        user = User.objects.filter(username=login_id).first()

        if not user:
            user = User.objects.filter(email=login_id).first()

        if not user:
            patient = PatientProfile.objects.filter(phone_number=login_id).first()
            if patient:
                user = patient.user
                
        if not user:
            therapist = TherapistProfile.objects.filter(phone_number=login_id).first()
            if therapist:
                user = therapist.user
                
        if not user or not user.check_password(password):
            messages.error(request, "Invalid credentials")
            return render(request, 'login.html')
            
        login(request, user)
        
        # ========================================================================================
        # DYNAMIC ROLE-BASED DASHBOARD REDIRECTION ROUTING ENGINE
        # ========================================================================================
        if user.role == "therapist":
            return redirect('therapist_dashboard')
        elif user.role == "admin":
            return redirect('profile-admin') # Redirects admin characters straight to dashboard scopes
        else:
            return redirect('patient_dashboard')
            
    return render(request, 'login.html')


@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('home')


# ========================================================================================
# PROFILE DISPLAY & PROFILE PERSISTENCE ENDPOINTS
# ========================================================================================

def profile_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Login required"
        }, status=401)

    user = request.user
    data = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role,
        "profile_picture": user.profile_picture.url if user.profile_picture else None
    }

    if user.role == "patient":
        profile = user.patientprofile
        data.update({
            "phone_number": profile.phone_number,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "emergency_contact": profile.emergency_contact
        })
    elif user.role == "therapist":
        profile = user.therapistprofile
        data.update({
            "phone_number": profile.phone_number,
            "date_of_birth": profile.date_of_birth,
            "specialization": profile.specialization,
            "qualification": profile.qualification,
            "experience_years": profile.experience_years,
            "bio": profile.bio,
            "is_verified": profile.is_verified
        })

    return JsonResponse(data)


@csrf_exempt
def update_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Login required"
        }, status=401)

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    user = request.user
    user.first_name = request.POST.get("first_name", user.first_name)
    user.last_name = request.POST.get("last_name", user.last_name)
    email = request.POST.get("email")

    if email and User.objects.exclude(id=user.id).filter(email=email).exists():
        return JsonResponse({
            "success": False,
            "message": "Email already exists"
        }, status=400)  

    if email:
        user.email = email

    profile_picture = request.FILES.get("profile_picture")
    if profile_picture:
        user.profile_picture = profile_picture

    user.save()

    if user.role == "patient":
        profile = user.patientprofile
        phone_number = normalize_phone_number(request.POST.get("phone_number"))

        if phone_number:
            if (
                PatientProfile.objects.exclude(user=user).filter(phone_number=phone_number).exists()
                or
                TherapistProfile.objects.exclude(user=user).filter(phone_number=phone_number).exists()
            ):
                return JsonResponse({
                    "success": False,
                    "message": "Phone number already exists"
                }, status=400)

        profile.phone_number = phone_number if phone_number is not None else profile.phone_number
        profile.date_of_birth = parse_date_value(request.POST.get("date_of_birth")) or profile.date_of_birth
        profile.gender = request.POST.get("gender", profile.gender)
        profile.emergency_contact = request.POST.get("emergency_contact", profile.emergency_contact)
        profile.save()

    elif user.role == "therapist":
        profile = user.therapistprofile

        if not user.profile_picture and not request.FILES.get("profile_picture"):
            return JsonResponse({
                "success": False,
                "message": "Profile picture is required for therapists"
            }, status=400)

        phone_number = normalize_phone_number(request.POST.get("phone_number"))

        if phone_number:
            if (
                PatientProfile.objects.exclude(user=user).filter(phone_number=phone_number).exists()
                or
                TherapistProfile.objects.exclude(user=user).filter(phone_number=phone_number).exists()
            ):
                return JsonResponse({
                    "success": False,
                    "message": "Phone number already exists"
                }, status=400)

        profile.phone_number = phone_number if phone_number is not None else profile.phone_number
        profile.date_of_birth = parse_date_value(request.POST.get("date_of_birth")) or profile.date_of_birth
        profile.specialization = request.POST.get("specialization", profile.specialization)
        profile.qualification = request.POST.get("qualification", profile.qualification)
        profile.experience_years = request.POST.get("experience_years", profile.experience_years)
        profile.bio = request.POST.get("bio", profile.bio)
        profile.save()

    return JsonResponse({
        "success": True,
        "message": "Profile updated successfully"
    })


# ========================================================================================
# CORE CLINICAL PLATFORM INTERFACE RENDER VIEWS
# ========================================================================================

@login_required
def patient_dashboard(request):
    try:
        from mood_tracker.models import JournalEntry 
        journal_count = JournalEntry.objects.filter(user=request.user).count()
    except ImportError:
        journal_count = 0

    completed_sessions_count = Appointment.objects.filter(
        patient=request.user, 
        status__in=['DONE', 'Done', 'Completed']
    ).count()

    latest_note = SessionNote.objects.filter(
        appointment__patient=request.user,
        appointment__status__in=['DONE', 'Done', 'CONFIRMED', 'CONFIRMED']
    ).exclude(shared_summary__isnull=True).exclude(shared_summary="").order_by('-created_at').first()

    shared_summary_text = ""
    session_formatted_date = ""
    if latest_note:
        shared_summary_text = latest_note.shared_summary
        session_formatted_date = latest_note.appointment.date.strftime("%B %d, %Y")

    today = timezone.now().date()
    mood_logs = MoodLog.objects.filter(user=request.user).order_by('-created_at')
    
    streak = 0
    check_date = today
    for log in mood_logs:
        log_date = log.created_at.date()
        if log_date == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        elif log_date == (check_date + timedelta(days=1)):
            continue
        else:
            break 

    context = {
        "journal_count": journal_count,
        "total_sessions": completed_sessions_count,
        "mood_streak": streak if streak > 0 else 1,
        "latest_summary_text": shared_summary_text,
        "latest_summary_date": session_formatted_date
    }
    return render(request, 'dashboard.html', context)


@login_required
def therapist_dashboard(request):
    """Collects authenticated practitioner properties directly to cleanly hydrate the master dashboard."""
    user = request.user
    try:
        profile = user.therapistprofile
        specialization = profile.specialization or "General Mental Wellness Counseling"
        qualification = profile.qualification or "Certified Mental Health Consultant"
        experience = profile.experience_years
        bio = profile.bio or ""
        dob = profile.date_of_birth.strftime("%B %d, %Y") if profile.date_of_birth else "Unspecified"
    except TherapistProfile.DoesNotExist:
        specialization = "General Mental Wellness"
        qualification = "Clinical Practitioner"
        experience = 0
        bio = ""
        dob = "Unspecified"

    therapist_data = {
        "name": f"{user.first_name} {user.last_name}".strip() or user.username,
        "id_tag": f"THP-{user.id:04d}",
        "specialization": specialization,
        "qualification": qualification,
        "experience": f"{experience} Years Experience",
        "dob": dob,
        "email": user.email,
    }

    return render(request, 'therapist_dashboard.html', {
        "therapist": therapist_data
    })


@login_required
def about_us(request):
    return render(request, 'About.html')


@login_required
def patient_profile(request):
    return render(request, 'Patient_profile_pg.html')


@login_required
def admin_profile(request):
    return render(request, 'admin_dashboard.html')


# ========================================================================================
# SECURE ADMINISTRATIVE WORKSPACE CONSOLE USER OPERATIONS
# ========================================================================================

@api_view(["GET"])
@user_passes_test(is_system_administrator)
def admin_telemetry_stats(request):
    """Calculates metadata KPI metrics for dashboard analytics panels."""
    total_users = User.objects.count()
    total_patients = User.objects.filter(role="patient").count()
    total_therapists = User.objects.filter(role="therapist").count()
    total_admins = User.objects.filter(role="admin").count()
    
    verified_therapists = TherapistProfile.objects.filter(is_verified=True).count()
    unverified_therapists = TherapistProfile.objects.filter(is_verified=False).count()
    
    return Response({
        "total_users": total_users,
        "total_patients": total_patients,
        "total_therapists": total_therapists,
        "total_admins": total_admins,
        "verified_therapists": verified_therapists,
        "unverified_therapists": unverified_therapists
    })


@api_view(["GET"])
@user_passes_test(is_system_administrator)
def admin_list_users(request):
    """Retrieves standard profiles serialization array for the registry panel."""
    users = User.objects.all().order_by('-date_joined')
    user_list = []
    for u in users:
        is_verified = False
        if u.role == "therapist":
            try:
                is_verified = u.therapistprofile.is_verified
            except Exception:
                is_verified = False
                
        user_list.append({
            "id": u.id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "role": u.role,
            "is_verified": is_verified
        })
    return Response(user_list)


@api_view(["GET", "DELETE"])
@user_passes_test(is_system_administrator)
def admin_user_detail(request, user_id):
    """Fetches comprehensive telemetry metrics or executes profile destruction logs."""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == "DELETE":
        user_obj.delete()
        return Response({"success": True, "message": "Registry node purged successfully."})
        
    data = {
        "id": user_obj.id,
        "username": user_obj.username,
        "first_name": user_obj.first_name,
        "last_name": user_obj.last_name,
        "email": user_obj.email,
        "role": user_obj.role,
        "date_joined": user_obj.date_joined.isoformat(),
        "last_login": user_obj.last_login.isoformat() if user_obj.last_login else None,
        "profile_picture_url": user_obj.profile_picture.url if user_obj.profile_picture and hasattr(user_obj.profile_picture, 'url') else None,
        "phone_number": "",
        "date_of_birth": ""
    }
    
    if user_obj.role == "patient":
        try:
            p = user_obj.patientprofile
            data.update({
                "phone_number": p.phone_number or "",
                "date_of_birth": p.date_of_birth.strftime("%Y-%m-%d") if p.date_of_birth else "",
                "gender": p.gender,
                "emergency_contact": p.emergency_contact
            })
        except Exception: pass
    elif user_obj.role == "therapist":
        try:
            t = user_obj.therapistprofile
            data.update({
                "phone_number": t.phone_number or "",
                "date_of_birth": t.date_of_birth.strftime("%Y-%m-%d") if t.date_of_birth else "",
                "specialization": t.specialization,
                "qualification": t.qualification,
                "experience_years": t.experience_years,
                "is_verified": t.is_verified,
                "bio": t.bio
            })
        except Exception: pass
        
    return Response(data)


@api_view(["POST"])
@user_passes_test(is_system_administrator)
def admin_edit_user(request, user_id):
    """Commits direct updates to core user identifiers and profile metadata types from FormData."""
    user_obj = get_object_or_404(User, id=user_id)
    
    user_obj.first_name = request.POST.get("first_name", user_obj.first_name)
    user_obj.last_name = request.POST.get("last_name", user_obj.last_name)
    user_obj.email = request.POST.get("email", user_obj.email)
    
    phone_input = request.POST.get("phone_number", "").strip() or None
    dob_input = parse_date_value(request.POST.get("date_of_birth"))

    if user_obj.role == "patient":
        try:
            profile = user_obj.patientprofile
            profile.phone_number = phone_input
            profile.date_of_birth = dob_input
            profile.save()
        except PatientProfile.DoesNotExist:
            pass

    elif user_obj.role == "therapist":
        try:
            profile = user_obj.therapistprofile
            profile.phone_number = phone_input
            profile.date_of_birth = dob_input
            profile.specialization = request.POST.get("specialization", profile.specialization)
            profile.qualification = request.POST.get("qualification", profile.qualification)
            
            exp_years = request.POST.get("experience_years")
            if exp_years is not None and exp_years.isdigit():
                profile.experience_years = int(exp_years)
                
            profile.bio = request.POST.get("bio", profile.bio)
            profile.save()
            
            new_photo = request.FILES.get("profile_picture")
            if new_photo:
                user_obj.profile_picture = new_photo
        except TherapistProfile.DoesNotExist:
            pass

    user_obj.save()
    return Response({"success": True, "message": "User registry data synchronized completely."})


@api_view(["POST"])
@user_passes_test(is_system_administrator)
def admin_reassign_role(request, user_id):
    """Reallocates authorization role keys and generates fallback profiles matching shifts."""
    user_obj = get_object_or_404(User, id=user_id)
    target_role = request.data.get("role")
    
    if target_role in ["patient", "therapist", "admin"]:
        user_obj.role = target_role
        user_obj.save()
        
        if target_role == "patient":
            PatientProfile.objects.get_or_create(user=user_obj)
        elif target_role == "therapist":
            TherapistProfile.objects.get_or_create(user=user_obj)
            
        return Response({"success": True})
    return Response({"success": False, "message": "Invalid system role designation."}, status=400)


@api_view(["POST"])
@user_passes_test(is_system_administrator)
def admin_verify_therapist(request, user_id):
    """Toggles credential validation clearances flags inside the practitioner records."""
    user_obj = get_object_or_404(User, id=user_id)
    if user_obj.role == "therapist":
        profile = user_obj.therapistprofile
        profile.is_verified = request.data.get("is_verified", False)
        profile.save()
        return Response({"success": True})
    return Response({"success": False, "message": "Target account is not a therapist profile node."}, status=400)   


# ========================================================================================
# NATIVE MODEL-ALIGNED PSYCHOEDUCATION ARTICLE MANAGEMENT CRUD ENDPOINTS
# ========================================================================================

@api_view(["GET"])
@user_passes_test(is_system_administrator)
def admin_list_articles(request):
    """Queries all database records from your PsychoeducationArticle table model."""
    articles = PsychoeducationArticle.objects.all().order_by('-created_at')
    serialized_list = []
    
    for art in articles:
        serialized_list.append({
            "id": art.id,
            "title": art.title,
            "category": art.category.upper() if art.category else "CBT",
            "status": "published", 
            "created_at": art.created_at.strftime("%Y-%m-%d")
        })
    return Response(serialized_list, status=status.HTTP_200_OK)


@api_view(["GET", "DELETE"])
@user_passes_test(is_system_administrator)
def admin_article_detail(request, article_id):
    """Fetches details for a specific article row or handles absolute database deletion."""
    article_obj = get_object_or_404(PsychoeducationArticle, id=article_id)
    
    if request.method == "DELETE":
        article_obj.delete()
        return Response({"success": True, "message": "Article dropped from registry collections."})
        
    return Response({
        "id": article_obj.id,
        "title": article_obj.title,
        "content": article_obj.content,
        "category": article_obj.category,
        "video_url": article_obj.video_url or "",
        "exercise": article_obj.exercise or "",
        "thumbnail_url": article_obj.thumbnail.url if article_obj.thumbnail and hasattr(article_obj.thumbnail, 'url') else None,
        "status": "published"
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
@user_passes_test(is_system_administrator)
def admin_create_article(request):
    """Creates a new article entry parsing multi-part form parameters explicitly."""
    title = request.POST.get("title", "").strip()
    content = request.POST.get("content", "").strip()
    category = request.POST.get("category", "cbt")
    video_url = request.POST.get("video_url", "").strip() or None
    exercise = request.POST.get("exercise", "").strip() or None
    thumbnail_file = request.FILES.get("thumbnail")

    if not title or not content:
        return Response({"success": False, "message": "Title and content properties cannot be empty."}, status=400)

    new_article = PsychoeducationArticle.objects.create(
        title=title,
        content=content,
        category=category,
        video_url=video_url,
        exercise=exercise,
        thumbnail=thumbnail_file
    )
    return Response({"success": True, "id": new_article.id}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@user_passes_test(is_system_administrator)
def admin_edit_article(request, article_id):
    """Updates the explicit model fields from raw multipart transaction requests."""
    article_obj = get_object_or_404(PsychoeducationArticle, id=article_id)
    
    article_obj.title = request.POST.get("title", article_obj.title).strip()
    article_obj.content = request.POST.get("content", article_obj.content).strip()
    article_obj.category = request.POST.get("category", article_obj.category)
    article_obj.video_url = request.POST.get("video_url", "").strip() or None
    article_obj.exercise = request.POST.get("exercise", "").strip() or None
    
    if request.FILES.get("thumbnail"):
        article_obj.thumbnail = request.FILES.get("thumbnail")
        
    article_obj.save()
    return Response({"success": True})


@api_view(["POST"])
@user_passes_test(is_system_administrator)
def admin_publish_article(request, article_id):
    return Response({"success": True, "message": "Article publish confirmed."})


# ------------------------------------------------------------------------------------
# LANDING PAGE RENDERING PUBLIC ROUTINES
# ------------------------------------------------------------------------------------

def Home(request):
    return render(request, "Home.html")

def about(request):
    return render(request, "About.html")

def Therapist_Home(request):
    return render(request, "therapist_home.html")