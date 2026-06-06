from django.test import TestCase

from .models import User, PatientProfile, TherapistProfile


class UserModelTest(TestCase):

    def test_create_user(self):

        user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@test.com",
            password="test123",
            role="patient"
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.role, "patient")


class PatientProfileTest(TestCase):

    def test_create_patient_profile(self):

        user = User.objects.create_user(
            username="patient1",
            password="test123"
        )

        profile = PatientProfile.objects.create(
            user=user,
            phone_number="9999999999",
            gender="male",
            emergency_contact="8888888888"
        )

        self.assertEqual(profile.user.username, "patient1")
        self.assertEqual(profile.phone_number, "9999999999")
        self.assertEqual(profile.gender, "male")
        self.assertEqual(profile.emergency_contact, "8888888888")


class TherapistProfileTest(TestCase):

    def test_create_therapist_profile(self):

        user = User.objects.create_user(
            username="therapist1",
            password="test123",
            role="therapist"
        )

        profile = TherapistProfile.objects.create(
            user=user,
            phone_number="7777777777",
            specialization="Anxiety",
            qualification="MSc Psychology",
            experience_years=5,
            bio="Experienced therapist",
            is_verified=True
        )

        self.assertEqual(profile.user.username, "therapist1")
        self.assertEqual(profile.phone_number, "7777777777")
        self.assertEqual(profile.specialization, "Anxiety")
        self.assertEqual(profile.qualification, "MSc Psychology")
        self.assertEqual(profile.experience_years, 5)
        self.assertEqual(profile.is_verified, True)

class AuthViewsTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test123",
            role="patient"
        )

    def test_login_user(self):

        response = self.client.post(
            "/login/",
            {
                "username": "testuser",
                "password": "test123"
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_logout_user(self):

        self.client.login(
            username="testuser",
            password="test123"
        )

        response = self.client.post("/logout/")

        self.assertEqual(response.status_code, 200)

    def test_register_user(self):

        response = self.client.post(
            "/register/",
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "new@test.com",
                "password": "test123",
                "confirm_password": "test123"
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            User.objects.filter(
                username="newuser"
            ).exists()
        )