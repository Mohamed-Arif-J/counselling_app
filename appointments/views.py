from django.contrib.auth.views import login_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment, SessionNote
from django.contrib.auth.models import User
from django.core.mail import send_mail
import json
from Ai_sessions.summarizer import summarize_text

# Create your views here.


# @api_view(["GET"])
# def available(request):
#     therapists = User.objects.filter(groups__name="Therapist").values("id", "username")
#     return Response(list(therapists))
#     # return Response({"message": "Therapists endpoint is working"})

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
        user_role = getattr(request.user, "role", "PATIENT")
        if user_role == "THERAPIST":
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
    user_role = getattr(request.user, "role", "PATIENT")
    if request.user.is_authenticated and user_role != "THERAPIST":
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
    message = (
        f"Your appointment for {date} at {time} is currently Pending confirmation."
    )
    try:
        send_mail(
            subject,
            message,
            "noreply@counsellingapp.com",
            [
                (
                    request.user.email
                    if request.user.is_authenticated
                    else "testpatient@test.com"
                )
            ],
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
            [
                (
                    request.user.email
                    if request.user.is_authenticated
                    else "testpatient@test.com"
                )
            ],
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
            [
                (
                    request.user.email
                    if request.user.is_authenticated
                    else "testpatient@test.com"
                )
            ],
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
    recipient = request.user.email if request.user.is_authenticated else 'testpatient@test.com'
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
    }, status=status.HTTP_200_OK
)


@api_view(['POST'])
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    appointment.status = 'DONE'
    appointment.save()
    
    return Response({
        "message": "Appointment marked as completed.",
        "appointment_id": appointment.id,
        "status": appointment.status
    },status=status.HTTP_200_OK
)


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

@login_required
def appointment_page(request):
    return render(request,'appointment.html')
@login_required
def therapist_page(request):
    return render(request,"therapist_list.html")