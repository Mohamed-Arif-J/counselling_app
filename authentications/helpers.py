import json
from functools import wraps

from django.http import JsonResponse

from .models import User, PatientProfile, TherapistProfile

ADMIN_ROLE = "admin"
ALLOWED_ROLES = {"patient", "therapist", "admin"}


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                "success": False,
                "message": "Authentication required"
            }, status=401)

        if getattr(request.user, "role", None) != ADMIN_ROLE:
            return JsonResponse({
                "success": False,
                "message": "Admin access required"
            }, status=403)

        return view_func(request, *args, **kwargs)

    return wrapper


def normalize_phone_number(value):
    if value is None:
        return None

    value = str(value).strip()
    return value or None


def parse_date_value(value):
    if not value:
        return None

    if hasattr(value, "isoformat"):
        return value

    from django.utils.dateparse import parse_date

    parsed_value = parse_date(str(value))
    return parsed_value


def serialize_datetime(value):
    if value is None:
        return None

    return value.isoformat()


def get_request_data(request):
    content_type = request.META.get("CONTENT_TYPE", "")

    if "application/json" in content_type:
        try:
            raw_body = request.body.decode("utf-8").strip()
            return json.loads(raw_body) if raw_body else {}
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}

    return request.POST


def get_patient_profile(user):
    try:
        return user.patientprofile
    except PatientProfile.DoesNotExist:
        return None


def get_therapist_profile(user):
    try:
        return user.therapistprofile
    except TherapistProfile.DoesNotExist:
        return None


def ensure_profile_for_role(user, role):
    auto_phone_number = f"auto-{user.id}"

    if role == "patient":
        profile, _ = PatientProfile.objects.get_or_create(
            user=user,
            defaults={"phone_number": auto_phone_number}
        )
        return profile

    if role == "therapist":
        profile, _ = TherapistProfile.objects.get_or_create(
            user=user,
            defaults={"phone_number": auto_phone_number}
        )
        return profile

    return None


def phone_number_exists(phone_number, exclude_user_id=None):
    if not phone_number:
        return False

    patient_profiles = PatientProfile.objects.filter(phone_number=phone_number)
    therapist_profiles = TherapistProfile.objects.filter(phone_number=phone_number)

    if exclude_user_id is not None:
        patient_profiles = patient_profiles.exclude(user_id=exclude_user_id)
        therapist_profiles = therapist_profiles.exclude(user_id=exclude_user_id)

    return patient_profiles.exists() or therapist_profiles.exists()


def serialize_basic_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role,
        "date_joined": serialize_datetime(user.date_joined),
        "last_login": serialize_datetime(user.last_login),
    }


def serialize_user_detail(user):
    data = serialize_basic_user(user)

    if user.role == "patient":
        profile = get_patient_profile(user)

        if profile:
            data.update({
                "phone_number": profile.phone_number,
                "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                "gender": profile.gender,
                "emergency_contact": profile.emergency_contact,
            })

    elif user.role == "therapist":
        profile = get_therapist_profile(user)

        if profile:
            data.update({
                "phone_number": profile.phone_number,
                "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                "specialization": profile.specialization,
                "qualification": profile.qualification,
                "experience_years": profile.experience_years,
                "bio": profile.bio,
                "is_verified": profile.is_verified,
            })

    return data


def serialize_user_list_item(user):
    return serialize_basic_user(user)


def serialize_patient_list_item(profile):
    return {
        "id": profile.user.id,
        "username": profile.user.username,
        "email": profile.user.email,
        "phone_number": profile.phone_number,
        "gender": profile.gender,
        "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        "emergency_contact": profile.emergency_contact,
        "created_at": serialize_datetime(profile.created_at),
    }


def serialize_patient_detail(profile):
    data = serialize_basic_user(profile.user)
    data.update({
        "phone_number": profile.phone_number,
        "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        "gender": profile.gender,
        "emergency_contact": profile.emergency_contact,
        "created_at": serialize_datetime(profile.created_at),
        "updated_at": serialize_datetime(profile.updated_at),
    })
    return data


def serialize_therapist_list_item(profile):
    return {
        "id": profile.user.id,
        "username": profile.user.username,
        "email": profile.user.email,
        "phone_number": profile.phone_number,
        "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        "specialization": profile.specialization,
        "qualification": profile.qualification,
        "experience_years": profile.experience_years,
        "bio": profile.bio,
        "is_verified": profile.is_verified,
        "created_at": serialize_datetime(profile.created_at),
    }


def serialize_therapist_detail(profile):
    data = serialize_basic_user(profile.user)
    data.update({
        "phone_number": profile.phone_number,
        "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        "specialization": profile.specialization,
        "qualification": profile.qualification,
        "experience_years": profile.experience_years,
        "bio": profile.bio,
        "is_verified": profile.is_verified,
        "created_at": serialize_datetime(profile.created_at),
        "updated_at": serialize_datetime(profile.updated_at),
    })
    return data
