from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from .models import User, PatientProfile, TherapistProfile
from .helpers import normalize_phone_number, parse_date_value
from django.contrib import messages


@csrf_exempt
def register_view(request):

    # if request.method != "POST":
    #     return JsonResponse({
    #         "success": False,
    #         "message": "POST request required"
    #     }, status=405)
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")
        password = request.POST.get("password")
        phone_number = normalize_phone_number(phone_number)

        # if not all([
        #     username,
        #     first_name,
        #     last_name,
        #     email,
        #     phone_number,
        #     password,
        #     confirm_password
        # ]):
        #     messages.error(request, "All fields are required")
        #     return render(request, 'register.html')

        # if password != confirm_password:
        #     messages.error(request, "Passwords do not match")
        #     return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'register.html')

        if (
            PatientProfile.objects.filter(phone_number=phone_number).exists()
            or
            TherapistProfile.objects.filter(phone_number=phone_number).exists()
        ):
            messages.error(request, "Phone number already exists")
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role="patient"
        )

        user.patientprofile.phone_number = phone_number
        user.patientprofile.save()
        return redirect('login')
    return render(request, 'register.html')


@csrf_exempt
def login_view(request):

    # if request.method != "POST":
    #     return JsonResponse({
    #         "success": False,
    #         "message": "POST request required"
    #     }, status=405)
    if request.method == "POST":  
        login_id = request.POST.get("login_id")
        password = request.POST.get("password")

        # if not login_id or not password:
        #     messages.error(request, "Login ID and Password are required")
        #     return render(request, 'login.html')

        user = User.objects.filter(
            username=login_id
        ).first()

        if not user:
            user = User.objects.filter(
                email=login_id
            ).first()

        if not user:

            patient = PatientProfile.objects.filter(
                phone_number=login_id
            ).first()

            if patient:
                user = patient.user
        if not user:
            therapist = TherapistProfile.objects.filter(
                phone_number=login_id
            ).first()
            if therapist:
                user = therapist.user
        if not user or not user.check_password(password):
            messages.error(request, "Invalid credentials")
            return render(request, 'login.html')
        login(request, user)
        return redirect('patient_dashboard')
    return render(request, 'login.html')


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
            "date_of_birth": profile.date_of_birth,
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
    email = request.POST.get("email")

    if email and User.objects.exclude(
        id=user.id
    ).filter(
        email=email
    ).exists():

        return JsonResponse({
            "success": False,
            "message": "Email already exists"
        }, status=400)  

    if email:
        user.email = email

    user.save()

    if user.role == "patient":

        profile = user.patientprofile

        phone_number = normalize_phone_number(request.POST.get("phone_number"))

        if phone_number:

            if (
                PatientProfile.objects.exclude(user=user)
                .filter(phone_number=phone_number)
                .exists()
                or
                TherapistProfile.objects.exclude(user=user)
                .filter(phone_number=phone_number)
                .exists()
            ):
                return JsonResponse({
                    "success": False,
                    "message": "Phone number already exists"
                }, status=400)

        profile.phone_number = phone_number if phone_number is not None else profile.phone_number

        profile.date_of_birth = parse_date_value(request.POST.get("date_of_birth")) or profile.date_of_birth

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

        phone_number = normalize_phone_number(request.POST.get("phone_number"))

        if phone_number:

            if (
                PatientProfile.objects.exclude(user=user)
                .filter(phone_number=phone_number)
                .exists()
                or
                TherapistProfile.objects.exclude(user=user)
                .filter(phone_number=phone_number)
                .exists()
            ):
                return JsonResponse({
                    "success": False,
                    "message": "Phone number already exists"
                }, status=400)

        profile.phone_number = phone_number if phone_number is not None else profile.phone_number

        profile.date_of_birth = parse_date_value(request.POST.get("date_of_birth")) or profile.date_of_birth

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
    return render (request,'dashboard.html')


def therapist_dashboard(request):
    return render (request,'therapist_dashboard.html')
