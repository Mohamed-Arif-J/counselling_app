from django.urls import path

from . import admin_views

urlpatterns = [
    path("dashboard/", admin_views.admin_dashboard, name="admin_dashboard"),
    path("users/", admin_views.admin_users_list, name="admin_users_list"),
    path("users/<int:user_id>/", admin_views.admin_user_detail, name="admin_user_detail"),
    path("users/<int:user_id>/edit/", admin_views.admin_user_edit, name="admin_user_edit"),
    path("users/<int:user_id>/change-role/", admin_views.admin_user_change_role, name="admin_user_change_role"),
    path("roles/", admin_views.admin_roles_list, name="admin_roles_list"),
    path("patients/", admin_views.admin_patients_list, name="admin_patients_list"),
    path("patients/<int:user_id>/", admin_views.admin_patient_detail, name="admin_patient_detail"),
    path("patients/<int:user_id>/edit/", admin_views.admin_patient_edit, name="admin_patient_edit"),
    path("therapists/", admin_views.admin_therapists_list, name="admin_therapists_list"),
    path("therapists/<int:user_id>/", admin_views.admin_therapist_detail, name="admin_therapist_detail"),
    path("therapists/<int:user_id>/edit/", admin_views.admin_therapist_edit, name="admin_therapist_edit"),
    path("therapists/<int:user_id>/verify/", admin_views.admin_therapist_verify, name="admin_therapist_verify"),
    path("therapists/<int:user_id>/unverify/", admin_views.admin_therapist_unverify, name="admin_therapist_unverify"),
    path("verification-summary/", admin_views.admin_verification_summary, name="admin_verification_summary"),
    path("recent-users/", admin_views.admin_recent_users, name="admin_recent_users"),
    path("profile-stats/", admin_views.admin_profile_stats, name="admin_profile_stats"),
    path("search/", admin_views.admin_search_users, name="admin_search_users"),
    path("profile/", admin_views.admin_profile, name="admin_profile"),
]
