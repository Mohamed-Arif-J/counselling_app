from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment, SessionNote
from django.contrib.auth.models import User
from django.core.mail import send_mail

# Create your views here.


@api_view(["GET"])
def available(request):
    therapists = User.objects.filter(groups__name="Therapist").values("id", "username")
    return Response(list(therapists))

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
    return Response(
        {
            "Message": "Appointment requested successfully!",
            "Appointment_id": appointment.id,
            "Status": appointment.status,
        }
    )




@api_view(["GET"])
def list_appointments(request):
    if (
        request.user.is_authenticated
        and request.user.groups.filter(name="Therapist").exists()
    ):
        appointments = Appointment.objects.filter(therapist=request.user)
    elif request.user.is_authenticated:
        appointments = Appointment.objects.filter(patient=request.user)
    else:
        appointments = Appointment.objects.all()

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
    return Response(
        {
            "Message": "Appointment cancelled successfully!",
            "appointment_id": appointment_id,
            "Status": appointment.status,
        }
    )




@api_view(["GET", "POST"])
def session_notes(request, appointment_id):
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
            }
        )
    elif request.method == "POST":
        note.private_notes = request.data.get("private_notes", note.private_notes)
        note.shared_summary = request.data.get("shared_summary", note.shared_summary)
        note.save()
        return Response(
            {
                "message": "Session notes recorded successfully.",
                "appointment_id": appointment.id,
                "private_notes": note.private_notes,
                "shared_summary": note.shared_summary,
            }
        )


@api_view(["POST"])
def send_mails(request):
    therapist_id = request.data.get("therapist_id")
    date = request.data.get("date")
    time = request.data.get("time")
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
def confirm_appointment(request, appointment_id):
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
