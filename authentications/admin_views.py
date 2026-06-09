from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .helpers import (
    ALLOWED_ROLES,
    admin_required,
    ensure_profile_for_role,
    get_request_data,
    normalize_phone_number,
    parse_date_value,
    phone_number_exists,
    serialize_basic_user,
    serialize_patient_detail,
    serialize_patient_list_item,
    serialize_therapist_detail,
    serialize_therapist_list_item,
    serialize_user_detail,
    serialize_user_list_item,
)
from .models import PatientProfile, TherapistProfile, User


@admin_required
def admin_dashboard(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    return JsonResponse({
        "total_users": User.objects.count(),
        "total_patients": User.objects.filter(role="patient").count(),
        "total_therapists": User.objects.filter(role="therapist").count(),
        "total_admins": User.objects.filter(role="admin").count(),
        "verified_therapists": TherapistProfile.objects.filter(is_verified=True).count(),
        "unverified_therapists": TherapistProfile.objects.filter(is_verified=False).count(),
    })


@admin_required
def admin_users_list(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    users = User.objects.order_by("-date_joined")
    return JsonResponse([serialize_user_list_item(user) for user in users], safe=False)


@admin_required
def admin_user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "GET":
        return JsonResponse(serialize_user_detail(user))

    if request.method == "DELETE":
        user.delete()
        return JsonResponse({
            "success": True,
            "message": "User deleted successfully"
        })

    return JsonResponse({
        "success": False,
        "message": "GET or DELETE request required"
    }, status=405)


@admin_required
def admin_user_edit(request, user_id):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    user = get_object_or_404(User, pk=user_id)
    data = get_request_data(request)

    email = data.get("email")
    if email:
        email = str(email).strip()

    if "email" in data and not email:
        return JsonResponse({
            "success": False,
            "message": "Email cannot be empty"
        }, status=400)

    if email and User.objects.exclude(pk=user.pk).filter(email=email).exists():
        return JsonResponse({
            "success": False,
            "message": "Email already exists"
        }, status=400)

    if "first_name" in data:
        user.first_name = data.get("first_name", user.first_name)

    if "last_name" in data:
        user.last_name = data.get("last_name", user.last_name)

    if email is not None:
        user.email = email

    user.save()

    return JsonResponse({
        "success": True,
        "message": "User updated successfully",
        "user": serialize_basic_user(user)
    })


@admin_required
def admin_user_change_role(request, user_id):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    user = get_object_or_404(User, pk=user_id)
    data = get_request_data(request)
    role = data.get("role")

    if role not in ALLOWED_ROLES:
        return JsonResponse({
            "success": False,
            "message": "Invalid role"
        }, status=400)

    try:
        user.role = role
        user.save(update_fields=["role"])

        ensure_profile_for_role(user, role)
    except IntegrityError:
        return JsonResponse({
            "success": False,
            "message": "Role updated, but profile creation failed. Please check database migrations."
        }, status=500)

    return JsonResponse({
        "success": True,
        "message": "Role updated successfully",
        "role": user.role
    })


@admin_required
def admin_roles_list(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    users = User.objects.order_by("-date_joined")
    return JsonResponse([
        {
            "id": user.id,
            "username": user.username,
            "current_role": user.role,
        }
        for user in users
    ], safe=False)


@admin_required
def admin_patients_list(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    profiles = PatientProfile.objects.select_related("user").order_by("-created_at")
    return JsonResponse([serialize_patient_list_item(profile) for profile in profiles], safe=False)


@admin_required
def admin_patient_detail(request, user_id):
    profile = get_object_or_404(PatientProfile.objects.select_related("user"), user_id=user_id)

    if request.method == "GET":
        return JsonResponse(serialize_patient_detail(profile))

    if request.method == "DELETE":
        profile.delete()
        return JsonResponse({
            "success": True,
            "message": "Patient profile deleted successfully"
        })

    return JsonResponse({
        "success": False,
        "message": "GET or DELETE request required"
    }, status=405)


@admin_required
def admin_patient_edit(request, user_id):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    profile = get_object_or_404(PatientProfile, user_id=user_id)
    data = get_request_data(request)

    phone_number = normalize_phone_number(data.get("phone_number")) if "phone_number" in data else profile.phone_number
    if phone_number and phone_number_exists(phone_number, exclude_user_id=profile.user_id):
        return JsonResponse({
            "success": False,
            "message": "Phone number already exists"
        }, status=400)

    if "phone_number" in data:
        profile.phone_number = phone_number

    if "gender" in data:
        profile.gender = data.get("gender", profile.gender)

    if "date_of_birth" in data:
        profile.date_of_birth = parse_date_value(data.get("date_of_birth")) or profile.date_of_birth

    if "emergency_contact" in data:
        profile.emergency_contact = data.get("emergency_contact", profile.emergency_contact)

    profile.save()

    return JsonResponse({
        "success": True,
        "message": "Patient profile updated successfully",
        "profile": serialize_patient_detail(profile)
    })


@admin_required
def admin_therapists_list(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    profiles = TherapistProfile.objects.select_related("user").order_by("-created_at")
    return JsonResponse([serialize_therapist_list_item(profile) for profile in profiles], safe=False)


@admin_required
def admin_therapist_detail(request, user_id):
    profile = get_object_or_404(TherapistProfile.objects.select_related("user"), user_id=user_id)

    if request.method == "GET":
        return JsonResponse(serialize_therapist_detail(profile))

    if request.method == "DELETE":
        profile.delete()
        return JsonResponse({
            "success": True,
            "message": "Therapist profile deleted successfully"
        })

    return JsonResponse({
        "success": False,
        "message": "GET or DELETE request required"
    }, status=405)


@admin_required
def admin_therapist_edit(request, user_id):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    profile = get_object_or_404(TherapistProfile, user_id=user_id)
    data = get_request_data(request)

    phone_number = normalize_phone_number(data.get("phone_number")) if "phone_number" in data else profile.phone_number
    if phone_number and phone_number_exists(phone_number, exclude_user_id=profile.user_id):
        return JsonResponse({
            "success": False,
            "message": "Phone number already exists"
        }, status=400)

    if "phone_number" in data:
        profile.phone_number = phone_number

    if "date_of_birth" in data:
        profile.date_of_birth = parse_date_value(data.get("date_of_birth")) or profile.date_of_birth

    if "specialization" in data:
        profile.specialization = data.get("specialization", profile.specialization)

    if "qualification" in data:
        profile.qualification = data.get("qualification", profile.qualification)

    if "experience_years" in data:
        profile.experience_years = data.get("experience_years", profile.experience_years)

    if "bio" in data:
        profile.bio = data.get("bio", profile.bio)

    profile.save()

    return JsonResponse({
        "success": True,
        "message": "Therapist profile updated successfully",
        "profile": serialize_therapist_detail(profile)
    })


@admin_required
def admin_therapist_verify(request, user_id):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    profile = TherapistProfile.objects.filter(user_id=user_id).first()

    if not profile:
        return JsonResponse({
            "success": False,
            "message": "Therapist profile not found"
        }, status=404)

    profile.is_verified = True
    profile.save(update_fields=["is_verified", "updated_at"])

    return JsonResponse({
        "success": True,
        "message": "Therapist verified successfully",
        "is_verified": True
    })


@admin_required
def admin_therapist_unverify(request, user_id):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    profile = TherapistProfile.objects.filter(user_id=user_id).first()

    if not profile:
        return JsonResponse({
            "success": False,
            "message": "Therapist profile not found"
        }, status=404)

    profile.is_verified = False
    profile.save(update_fields=["is_verified", "updated_at"])

    return JsonResponse({
        "success": True,
        "message": "Therapist unverified successfully",
        "is_verified": False
    })


@admin_required
def admin_verification_summary(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    return JsonResponse({
        "verified_therapists": TherapistProfile.objects.filter(is_verified=True).count(),
        "unverified_therapists": TherapistProfile.objects.filter(is_verified=False).count(),
    })


@admin_required
def admin_recent_users(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    users = User.objects.order_by("-date_joined")[:5]
    return JsonResponse([
        {
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        }
        for user in users
    ], safe=False)


@admin_required
def admin_profile_stats(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    return JsonResponse({
        "total_users": User.objects.count(),
        "patient_profiles": PatientProfile.objects.count(),
        "therapist_profiles": TherapistProfile.objects.count(),
        "users_without_profiles": User.objects.filter(
            patientprofile__isnull=True,
            therapistprofile__isnull=True,
        ).count(),
    })


@admin_required
def admin_search_users(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    users = User.objects.filter(
        Q(username__icontains=query)
        | Q(first_name__icontains=query)
        | Q(last_name__icontains=query)
        | Q(email__icontains=query)
        | Q(patientprofile__phone_number__icontains=query)
        | Q(therapistprofile__phone_number__icontains=query)
    ).distinct().order_by("-date_joined")

    return JsonResponse([serialize_user_list_item(user) for user in users], safe=False)


@admin_required
def admin_profile(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "GET request required"
        }, status=405)

    return JsonResponse({
        "username": request.user.username,
        "email": request.user.email,
        "role": request.user.role,
        "last_login": request.user.last_login.isoformat() if request.user.last_login else None,
        "date_joined": request.user.date_joined.isoformat() if request.user.date_joined else None,
    })
