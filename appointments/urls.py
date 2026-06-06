from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_appointments, name='list_appointments'),
    path('therapists/', views.available, name='available'),
    path('book/', views.book, name='book'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    # path('notes/<int:appointment_id>/', views.manage_session_notes, name='manage_session_notes'),
]