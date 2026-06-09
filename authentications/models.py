from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/users/", blank=True, null=True)
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('therapist', 'Therapist'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='patient'
    )

    def __str__(self):
        return self.username



class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.username




class TherapistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=150, blank=True)
    experience_years = models.PositiveIntegerField(default=0)

    bio = models.TextField(blank=True)

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
