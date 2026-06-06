from django.urls import path
from .import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path(
    'patient-dashboard/',
    views.patient_dashboard,
    name='patient_dashboard'
),

path(
    'therapist-dashboard/',
    views.therapist_dashboard,
    name='therapist_dashboard'
),

path(
    'admin-dashboard/',
    views.admin_dashboard,
    name='admin_dashboard'
),
]