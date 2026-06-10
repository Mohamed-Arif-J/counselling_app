from django.urls import path
from .views import (
    list_appointments, 
    book, 
    cancel_appointment, 
    session_notes, 
    confirm_appointment_email, 
    send_mails, 
    cancel_appointment_email, 
    confirm_appointment, 
    complete_appointment, 
    generate_ai_summary, 
    appointment_page,
    therapist_history, 
    therapist_page,
    therapist_active_page,              # Renders standalone workspace HTML
    patient_session_context,            # Supplies context data (patient name, journal timeline logs)
    therapist_historical_records_api    # Supplies completed historical session data for case logs page
)

urlpatterns = [
    # ------------------------------------------------------------------------------------
    # Template Page Rendering Routes
    # ------------------------------------------------------------------------------------
    path('appointments/', appointment_page, name='appointment_page'),
    path('therapists/', therapist_page, name="therapist_page"),
    path('therapist-active/', therapist_active_page, name='therapist_active_page'),
    path('history/', therapist_history, name="therapist_history"),

    # ------------------------------------------------------------------------------------
    # Asynchronous REST DRF API Core Endpoints
    # ------------------------------------------------------------------------------------
    path('', list_appointments, name='list_appointments'),
    path('book/', book, name='book'),
    
    # Active Workspace Data Synchronization Endpoint (Fixes 404 Sync Error)
    path('context/<int:appointment_id>/', patient_session_context, name='patient_session_context'),
    
    # Historical Longitudinal Records Lookup API (Hydrates Patient Case History Page)
    path('api/historical-records/', therapist_historical_records_api, name='therapist_historical_records_api'),
    
    # Session Management Actions
    path('cancel/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
    path('confirm/<int:appointment_id>/', confirm_appointment, name='confirm_appointment'),
    path('<int:appointment_id>/complete/', complete_appointment, name='complete_appointment'),
    
    # Progress Notes & AI Text Processing Endpoints
    path('notes/<int:appointment_id>/', session_notes, name='session_notes'),
    path('notes/<int:appointment_id>/ai-summary/', generate_ai_summary, name='generate_ai_summary'),
    
    # Shorthand Notification & Email Pipeline Hooks
    path('send_mails/', send_mails, name='send_mails'),
    path('<int:appointment_id>/confirm/', confirm_appointment_email, name='confirm_appointment_email'),
    path('cancel_email/<int:appointment_id>/', cancel_appointment_email, name='cancel_appointment_email'),
]