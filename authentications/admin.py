from django.contrib import admin
from .models import User, PatientProfile, TherapistProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'role',
        'is_active'
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )

    list_filter = (
        'role',
        'is_active'
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone_number',
        'gender',
        'date_of_birth',
        'emergency_contact',
        'created_at'
    )

    search_fields = (
        'user__username',
        'phone_number'
    )

    list_filter = (
        'gender',
    )


@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone_number',
        'specialization',
        'qualification',
        'experience_years',
        'is_verified',
        'created_at'
    )

    search_fields = (
        'user__username',
        'specialization',
        'qualification'
    )

    list_filter = (
        'is_verified',
        'specialization'
    )