from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

from .models import User


@csrf_exempt
def register_view(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    username = request.POST.get("username")
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    email = request.POST.get("email")
    password = request.POST.get("password")
    confirm_password = request.POST.get("confirm_password")

    if not all([
        username,
        first_name,
        last_name,
        email,
        password,
        confirm_password
    ]):
        return JsonResponse({
            "success": False,
            "message": "All fields are required"
        }, status=400)

    if password != confirm_password:
        return JsonResponse({
            "success": False,
            "message": "Passwords do not match"
        }, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({
            "success": False,
            "message": "Username already exists"
        }, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({
            "success": False,
            "message": "Email already exists"
        }, status=400)

    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        role="patient"
    )

    return JsonResponse({
        "success": True,
        "message": "Registration successful",
        "username": user.username,
        "role": user.role
    })


@csrf_exempt
def login_view(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return JsonResponse({
            "success": False,
            "message": "Invalid credentials"
        }, status=401)

    login(request, user)

    return JsonResponse({
        "success": True,
        "message": "Login successful",
        "username": user.username,
        "role": user.role
    })


@csrf_exempt
def logout_view(request):

    logout(request)

    return JsonResponse({
        "success": True,
        "message": "Logout successful"
    })


def profile_view(request):

    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Login required"
        }, status=401)

    user = request.user

    data = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role
    }

    if user.role == "patient":

        profile = user.patientprofile

        data.update({
            "phone_number": profile.phone_number,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "emergency_contact": profile.emergency_contact
        })

    elif user.role == "therapist":

        profile = user.therapistprofile

        data.update({
            "phone_number": profile.phone_number,
            "specialization": profile.specialization,
            "qualification": profile.qualification,
            "experience_years": profile.experience_years,
            "bio": profile.bio,
            "is_verified": profile.is_verified
        })

    return JsonResponse(data)


@csrf_exempt
def update_profile(request):

    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Login required"
        }, status=401)

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    user = request.user

    user.first_name = request.POST.get(
        "first_name",
        user.first_name
    )

    user.last_name = request.POST.get(
        "last_name",
        user.last_name
    )

    user.email = request.POST.get(
        "email",
        user.email
    )

    user.save()

    if user.role == "patient":

        profile = user.patientprofile

        profile.phone_number = request.POST.get(
            "phone_number",
            profile.phone_number
        )

        profile.gender = request.POST.get(
            "gender",
            profile.gender
        )

        profile.emergency_contact = request.POST.get(
            "emergency_contact",
            profile.emergency_contact
        )

        profile.save()

    elif user.role == "therapist":

        profile = user.therapistprofile

        profile.phone_number = request.POST.get(
            "phone_number",
            profile.phone_number
        )

        profile.specialization = request.POST.get(
            "specialization",
            profile.specialization
        )

        profile.qualification = request.POST.get(
            "qualification",
            profile.qualification
        )

        profile.experience_years = request.POST.get(
            "experience_years",
            profile.experience_years
        )

        profile.bio = request.POST.get(
            "bio",
            profile.bio
        )

        profile.save()

    return JsonResponse({
        "success": True,
        "message": "Profile updated successfully"
    })


def patient_dashboard(request):
    return HttpResponse("Patient Dashboard")


def therapist_dashboard(request):
    return HttpResponse("Therapist Dashboard")


def admin_dashboard(request):
    return HttpResponse("Admin Dashboard")