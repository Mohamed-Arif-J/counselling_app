from django.urls import path
from .views import list_appointments, book, cancel_appointment, session_notes, confirm_appointment_email, send_mails,cancel_appointment_email, confirm_appointment, complete_appointment,generate_ai_summary,appointment_page, therapist_page

urlpatterns = [
    path("", list_appointments, name="list_appointments"),
    # path("therapists/", available, name="available"),
    path("book/", book, name="book"),
    path("cancel/<int:appointment_id>/", cancel_appointment, name="cancel_appointment"),
    path("cancel_email/<int:appointment_id>/", cancel_appointment_email, name="cancel_appointment_email"),
    path("notes/<int:appointment_id>/", session_notes, name="session_notes"),
    path("confirm/<int:appointment_id>/", confirm_appointment, name="confirm_appointment"),
    path("send_mails/", send_mails, name="send_mails"),
    path('<int:appointment_id>/confirm/',confirm_appointment_email, name='confirm_appointment_email'),
    path('<int:appointment_id>/complete/', complete_appointment, name='complete_appointment'),
    path('notes/<int:appointment_id>/ai-summary/',generate_ai_summary, name='generate_ai_summary'),
    path('appointments/',appointment_page,name='appointment_page'),
    path('therapists/',therapist_page,name="therapist_page")
]
