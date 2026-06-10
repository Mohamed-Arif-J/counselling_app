from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json

from authentications.models import TherapistProfile
from .models import Appointment, SessionNote
from Ai_sessions.summarizer import summarize_text

User = get_user_model()

# ========================================================================================
# TEMPLATE RENDER VIEWS
# ========================================================================================

@login_required
def appointment_page(request):
    """
    Queries the TherapistProfile table directly, extracts active record fields natively,
    and injects them into the appointment.html context as a JSON script payload to 
    power the interactive directory booking calendar drop rows.
    """
    profiles_queryset = TherapistProfile.objects.select_related('user').all()
    
    therapists_list = []
    for profile in profiles_queryset:
        t = profile.user 
        
        degree = profile.qualification or "Credentials Unspecified"
        focus = profile.specialization or "General Mental Wellness"
        
        if t.profile_picture:
            img_url = t.profile_picture.url
        else:
            img_url = "https://hips.hearstapps.com/hmg-prod/images/portrait-of-a-happy-young-doctor-in-his-clinic-royalty-free-image-1661432441.jpg?crop=0.66698xw:1xh;center,top&resize=640:*"
        
        therapists_list.append({
            "id": t.id,
            "name": f"Dr. {t.first_name} {t.last_name}".strip() if (t.first_name or t.last_name) else t.username,
            "degree": degree,
            "focus": focus,
            "is_verified": profile.is_verified,
            "img": img_url
        })
        
    context = {
        "therapists_json": json.dumps(therapists_list)
    }
    return render(request, 'appointment.html', context)


@login_required
def therapist_page(request):
    """
    Queries the TherapistProfile table directly, extracts active record fields 
    natively, and injects real database data straight to the frontend payload.
    """
    profiles_queryset = TherapistProfile.objects.select_related('user').all()
    
    therapists_list = []
    for profile in profiles_queryset:
        t = profile.user 
        
        degree = profile.qualification or "Credentials Unspecified"
        desc = profile.bio or "No background description provided yet."
        focus = profile.specialization or "General Mental Wellness"
        
        # Determine the filter category sorting axis dynamically from the focus text string
        category_axis = "trauma" if "trauma" in focus.lower() or "ptsd" in focus.lower() else "anxiety"

        if t.profile_picture:
            img_url = t.profile_picture.url
        else:
            img_url = "https://hips.hearstapps.com/hmg-prod/images/portrait-of-a-happy-young-doctor-in-his-clinic-royalty-free-image-1661432441.jpg?crop=0.66698xw:1xh;center,top&resize=640:*"
        
        therapists_list.append({
            "id": t.id,
            "category": category_axis,
            "name": f"Dr. {t.first_name} {t.last_name}".strip() if (t.first_name or t.last_name) else t.username,
            "degree": degree,
            "is_verified": profile.is_verified, 
            "cred": f"{profile.experience_years} Years Experience.",
            "focus": focus,
            "desc": desc,
            "img": img_url
        })
        
    context = {
        "therapists_json": json.dumps(therapists_list)
    }
    return render(request, "therapist_list.html", context)


# ========================================================================================
# ASYNCHRONOUS API REST DRF CONTROLLERS
# ========================================================================================

@api_view(["POST"])
def book(request):
    if not request.user.is_authenticated:
        return Response(
            {"error": "You must be logged in to book an appointment."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    therapist_id = request.data.get("therapist_id")
    date = request.data.get("appointment_date")
    time = request.data.get("appointment_time")
    
    appointment = Appointment.objects.create(
        patient=request.user,
        therapist_id=therapist_id,
        date=date,
        time=time,
        status="Pending",
    )
    
    subject = "New Appointment Requested"
    message = f"Your appointment for {date} at {time} is currently Pending confirmation."
    recipient = request.user.email if request.user.email else "testpatient@test.com"
    
    try:
        send_mail(subject, message, "noreply@counsellingapp.com", [recipient], fail_silently=True)
        email_status = "Success"
    except Exception:
        email_status = "Failed"
        
    return Response(
        {
            "Message": "Appointment requested successfully!",
            "Appointment_id": appointment.id,
            "Status": appointment.status,
            "Email_status": email_status
        },
        status=status.HTTP_201_CREATED
    )


@api_view(["GET"])
def list_appointments(request):
    if not request.user.is_authenticated:
        appointments = Appointment.objects.all()
    else:
        user_role = getattr(request.user, "role", "patient")
        if user_role == "therapist":
            appointments = Appointment.objects.filter(therapist=request.user)
        else:
            appointments = Appointment.objects.filter(patient=request.user)

    data = list(
        appointments.values(
            "id", "patient__username", "therapist__username", "date", "time", "status"
        )
    )
    return Response(data)


@api_view(["POST"])
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = "Cancelled"
    appointment.save()

    subject = "Appointment Cancelled"
    message = f"The appointment scheduled for {appointment.date} has been successfully cancelled."
    recipient = request.user.email if request.user.is_authenticated and request.user.email else "testpatient@test.com"
    
    try:
        send_mail(subject, message, "noreply@counsellingapp.com", [recipient], fail_silently=True)
        email_status = "Success"
    except Exception:
        email_status = "Failed"

    return Response(
        {
            "Message": "Appointment cancelled successfully!",
            "appointment_id": appointment_id,
            "Status": appointment.status,
            "Email_status": email_status
        },
        status=status.HTTP_200_OK
    )


@api_view(["GET", "POST"])
def session_notes(request, appointment_id):
    user_role = getattr(request.user, "role", "patient")
    if request.user.is_authenticated and user_role != "therapist":
        return Response({"error": "Access denied. Only therapists can manage session notes."},
        status=status.HTTP_403_FORBIDDEN)

    appointment = get_object_or_404(Appointment, id=appointment_id)
    note, created = SessionNote.objects.get_or_create(
        appointment=appointment, defaults={"therapist": appointment.therapist}
    )

    if request.method == "GET":
        return Response(
            {
                "appointment_id": appointment.id,
                "private_notes": note.private_notes,
                "shared_summary": note.shared_summary,
                "created_at": note.created_at,
            },
            status=status.HTTP_200_OK
        )
        
    elif request.method == "POST":
        note.private_notes = request.data.get("private_notes", note.private_notes)
        note.shared_summary = request.data.get("shared_summary", note.shared_summary)
        note.save()        
        crisis_flag = getattr(request, "crisis_detected", False)
        risk_level = getattr(request, "risk_level", "LOW")

        return Response(
            {
                "message": "Session notes recorded successfully.",
                "appointment_id": appointment.id,
                "private_notes": note.private_notes,
                "shared_summary": note.shared_summary,
                "crisis_alert": crisis_flag,
                "risk_level": risk_level
            },
            status=status.HTTP_200_OK
        )


@api_view(["POST"])
def send_mails(request):
    therapist_id = request.data.get("therapist_id")
    date = request.data.get("date")
    time = request.data.get("time")
    
    if not request.user.is_authenticated:
        return Response(
            {"error": "You must be logged in to request an appointment."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    appointment = Appointment.objects.create(
        patient=request.user,
        therapist_id=therapist_id,
        date=date,
        time=time,
        status="Pending",
    )

    subject = "New Appointment Requested"
    message = f"Your appointment for {date} at {time} is currently Pending confirmation."
    try:
        send_mail(
            subject,
            message,
            "noreply@counsellingapp.com",
            [request.user.email if request.user.email else "testpatient@test.com"],
            fail_silently=True,
        )
        email_status = "Success"
    except Exception:
        email_status = "Failed"
        
    return Response(
        {
            "message": "Appointment requested successfully!",
            "appointment_id": appointment.id,
            "status": appointment.status,
            "email_status": email_status,
        }
    )


@api_view(["POST"])
def cancel_appointment_email(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = "CANCELLED"
    appointment.save()
    subject = "Appointment Cancelled"
    message = f"The appointment scheduled for {appointment.date} has been successfully cancelled."
    try:
        send_mail(
            subject,
            message,
            "noreply@counsellingapp.com",
            [request.user.email if request.user.email else "testpatient@test.com"],
            fail_silently=True,
        )
        email_status = "Success"
    except Exception: 
        email_status = "Failed"
        
    return Response(
        {
            "message": "Appointment successfully cancelled.",
            "appointment_id": appointment.id,
            "status": appointment.status,
            "email_status": email_status,
        }
    )


@api_view(["POST"])
def confirm_appointment_email(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = "Confirmed"
    appointment.save()
    subject = "Appointment Confirmed"
    message = f"The appointment scheduled for {appointment.date} has been successfully confirmed."
    try:
        send_mail(
            subject,
            message,
            "noreply@counsellingapp.com",
            [request.user.email if request.user.email else "testpatient@test.com"],
            fail_silently=True,
        )
        email_status = "Success"
    except Exception:
        email_status = "Failed"
        
    return Response(
        {
            "message": "Appointment successfully confirmed.",
            "appointment_id": appointment.id,
            "status": appointment.status,
            "email_status": email_status,
        }
    )


@api_view(['POST'])
def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'CONFIRMED'
    appointment.save()
    
    subject = "Appointment Confirmed"
    message = f"Good news! Your appointment scheduled for {appointment.date} has been CONFIRMED by your therapist."
    recipient = request.user.email if request.user.email else 'testpatient@test.com'
    try:
        send_mail(subject, message, 'noreply@counsellingapp.com', [recipient], fail_silently=True)
        email_status = "Sent successfully"
    except Exception:
        email_status = "Failed (Queued)"

    return Response({
        "message": "Appointment has been confirmed.",
        "appointment_id": appointment.id,
        "status": appointment.status,
        "email_notification": email_status
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'DONE'
    appointment.save()
    
    return Response({
        "message": "Appointment marked as completed.",
        "appointment_id": appointment.id,
        "status": appointment.status
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def generate_ai_summary(request, appointment_id):
    note = get_object_or_404(SessionNote, appointment_id=appointment_id)
    raw_notes = note.private_notes
    
    if not raw_notes.strip():
        return Response(
            {"error": "Private notes are empty. Cannot generate an AI summary."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    ai_response_string = summarize_text(raw_notes)
    
    try:
        ai_data = json.loads(ai_response_string)
        clean_summary = ai_data.get("summary", "Summary processing failed.")
    except Exception:
        clean_summary = "Failed to parse the generated summary formatting."
    
    note.shared_summary = clean_summary
    note.save()
    
    return Response({
        "message": "AI Auto-summary generated successfully.",
        "appointment_id": appointment_id,
        "shared_summary": note.shared_summary
    }, status=status.HTTP_200_OK)

from mood_tracker.models import MoodLog  # Make sure to import the MoodLog model safely here

@login_required
def therapist_active_page(request):
    """
    Renders the live clinical session workspace wrapper shell safely.
    """
    # Fetch therapist properties for the navbar badge and credentials modal
    user = request.user
    try:
        profile = user.therapistprofile
        qualification = profile.qualification or "Clinical Practitioner"
        specialization = profile.specialization or "General Mental Wellness"
        experience = profile.experience_years
        dob = profile.date_of_birth.strftime("%B %d, %Y") if profile.date_of_birth else "Unspecified"
    except TherapistProfile.DoesNotExist:
        qualification = "Clinical Consultant"
        specialization = "General Mental Wellness"
        experience = 0
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
    return render(request, 'therapist_active_session_workspace.html', {"therapist": therapist_data})


from mood_tracker.models import JournalEntry # Adjust this import path to match your app layout

@api_view(["GET"])
def patient_session_context(request, appointment_id):
    """
    Gathers detailed patient meta-data and pulls their true handwritten journal 
    reflections straight from the database to assist the clinician.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    patient_user = appointment.patient
    
    # 1. Query real text-based journal entries instead of superficial mood log emoji clicks
    journal_queryset = JournalEntry.objects.filter(user=patient_user).order_by('-created_at')
    
    serialized_journals = []
    for log in journal_queryset:
        # Accessing content text. If your model uses fields like log.content or log.text, swap it here:
        entry_text = getattr(log, "note", None) or getattr(log, "content", None) or "Empty journal entry body text."
        
        # Pull associated mood text if your model tracks it, otherwise fallback gracefully
        associated_mood = getattr(log, "mood", "Logged") 
        if isinstance(associated_mood, int):
            mood_map = {5: "Excellent", 4: "Good", 3: "Okay", 2: "Down", 1: "Bad"}
            associated_mood = mood_map.get(associated_mood, "Logged")

        serialized_journals.append({
            "date": log.created_at.strftime("%Y-%m-%d"),
            "mood": associated_mood,
            "logs": entry_text
        })
        
    return Response({
        "patient_username": patient_user.username,
        "patient_full_name": f"{patient_user.first_name} {patient_user.last_name}".strip() or patient_user.username,
        "appointment_date": appointment.date.strftime("%Y-%m-%d"),
        "appointment_time": appointment.time.strftime("%I:%M %p"),
        "appointment_status": appointment.status,
        "journal_logs": serialized_journals # Pushes real diaries down to the timeline container loop
    }, status=status.HTTP_200_OK)
@login_required
def therapist_history(request):
    """
    Collects authenticated practitioner properties directly from User 
    and TherapistProfile tables to hydrate the historical longitudinal case hub.
    """
    user = request.user
    try:
        profile = user.therapistprofile
        qualification = profile.qualification or "Clinical Practitioner"
        specialization = profile.specialization or "General Mental Wellness"
        experience = profile.experience_years
        dob = profile.date_of_birth.strftime("%B %d, %Y") if profile.date_of_birth else "Unspecified"
    except TherapistProfile.DoesNotExist:
        qualification = "Clinical Consultant"
        specialization = "General Mental Wellness"
        experience = 0
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

    return render(request, 'therapist_patient_case_history.html', {
        "therapist": therapist_data
    })
@api_view(["GET"])
def therapist_historical_records_api(request):
    """
    Queries completed clinical case logs assigned to the active practitioner,
    pre-joining related profile models to deliver comprehensive search arrays.
    """
    if not request.user.is_authenticated:
        return Response({"error": "Unauthorized Access"}, status=status.HTTP_401_UNAUTHORIZED)
        
    # Query finished consultations prefetching cross-app model layers
    sessions = Appointment.objects.filter(
        therapist=request.user,
        status__in=["DONE", "Done", "Completed"]
    ).select_related('patient').order_by('-date', '-time')
    
    serialized_history_records = []
    
    for appt in sessions:
        # Pull associated progressive session note layer safely
        note_obj = SessionNote.objects.filter(appointment=appt).first()
        private_notes = note_obj.private_notes if note_obj else ""
        shared_summary = note_obj.shared_summary if note_obj else ""
        
        serialized_history_records.append({
            "id": appt.id,
            "patientName": f"{appt.patient.first_name} {appt.patient.last_name}".strip() or appt.patient.username,
            "patientUsername": appt.patient.username,
            "date": appt.date.strftime("%Y-%m-%d"),
            "time": appt.time.strftime("%I:%M %p"),
            "notes": private_notes,
            "shared_summary": shared_summary
        })
        
    return Response(serialized_history_records, status=status.HTTP_200_OK)    
