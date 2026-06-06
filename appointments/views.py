from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment
from django.contrib.auth.models import User
from django.http import request


# Create your views here.

@api_view(['GET'])
def available(request):
    therapists = User.objects.filter(groups__name='Therapist').values('id', 'username')
    return Response(list(therapists))


@api_view(['POST'])
def book(request):
    if not request.user.is_authenticated:
        return Response({"error": "You must be logged in to book an appointment."}, status=status.HTTP_401_UNAUTHORIZED)

    therapist_id = request.data.get('therapist_id')
    date = request.data.get('appointment_date')
    time = request.data.get('appointment_time')
    appointment = Appointment.objects.create(
        patient=request.user,
        therapist_id=therapist_id,
        date=date,
        time=time,
        status='Pending'
    )
    return Response({
        "Message": "Appointment requested successfully!",
        'Appointment_id': appointment.id,
        "Status": appointment.status
    })


@api_view(['GET'])
def list_appointments(request):
    if request.user.is_authenticated and request.user.groups.filter(name="Therapist").exists():
        appointments = Appointment.objects.filter(therapist=request.user)
    elif request.user.is_authenticated:
        appointments = Appointment.objects.filter(patient=request.user)
    else:
        appointments = Appointment.objects.all()

    data = list(appointments.values('id', 'patient__username', 'therapist__username', 'date', 'time', 'status'))
    return Response(data)


@api_view(['POST'])
def cancel_appointment(request,appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Cancelled'
    appointment.save()
    return Response({
        "Message": "Appointment cancelled successfully!",
        "appointment_id": appointment_id,
        "Status": appointment.status
    })