from django.urls import path
from .views import list_appointments, available, book, cancel_appointment, session_notes, confirm_appointment, send_mails, cancel_appointment_email

urlpatterns = [
    path("", list_appointments, name="list_appointments"),
    path("therapists/", available, name="available"),
    path("book/", book, name="book"),
    path("cancel/<int:appointment_id>/", cancel_appointment, name="cancel_appointment"),
    path("cancel_email/<int:appointment_id>/", cancel_appointment_email, name="cancel_appointment_email"),
    path("notes/<int:appointment_id>/", session_notes, name="session_notes"),
    path("confirm/<int:appointment_id>/", confirm_appointment, name="confirm_appointment"),
    path("send_mails/", send_mails, name="send_mails")
]
