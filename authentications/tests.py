from django.test import TestCase

from .models import User


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

    def test_patient_profile_created_by_signal(self):

        user = User.objects.create_user(
            username="patient1",
            email="patient@test.com",
            password="test123",
            role="patient"
        )

        self.assertTrue(hasattr(user, "patientprofile"))


class TherapistProfileTest(TestCase):

    def test_therapist_profile_created_by_signal(self):

        user = User.objects.create_user(
            username="therapist1",
            email="therapist@test.com",
            password="test123",
            role="therapist"
        )

        self.assertTrue(hasattr(user, "therapistprofile"))


class AuthViewsTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test123",
            role="patient"
        )

        self.user.patientprofile.phone_number = "9999999999"
        self.user.patientprofile.save()

    def test_login_with_username(self):

        response = self.client.post(
            "/login/",
            {
                "login_id": "testuser",
                "password": "test123"
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_login_with_email(self):

        response = self.client.post(
            "/login/",
            {
                "login_id": "test@test.com",
                "password": "test123"
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_login_with_phone(self):

        response = self.client.post(
            "/login/",
            {
                "login_id": "9999999999",
                "password": "test123"
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_logout_user(self):

        self.client.post(
            "/login/",
            {
                "login_id": "testuser",
                "password": "test123"
            }
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
                "phone_number": "8888888888",
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

    def test_duplicate_email_registration(self):

        response = self.client.post(
            "/register/",
            {
                "username": "user2",
                "first_name": "Test",
                "last_name": "User",
                "email": "test@test.com",
                "phone_number": "8888888888",
                "password": "test123",
                "confirm_password": "test123"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_duplicate_phone_registration(self):

        response = self.client.post(
            "/register/",
            {
                "username": "user3",
                "first_name": "Test",
                "last_name": "User",
                "email": "user3@test.com",
                "phone_number": "9999999999",
                "password": "test123",
                "confirm_password": "test123"
            }
        )

        self.assertEqual(response.status_code, 400)