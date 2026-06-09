from django.test import TestCase
from datetime import date

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
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Patient Dashboard")

    def test_login_with_email(self):

        response = self.client.post(
            "/login/",
            {
                "login_id": "test@test.com",
                "password": "test123"
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Patient Dashboard")

    def test_login_with_phone(self):

        response = self.client.post(
            "/login/",
            {
                "login_id": "9999999999",
                "password": "test123"
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Patient Dashboard")

    def test_logout_user(self):

        self.client.post(
            "/login/",
            {
                "login_id": "testuser",
                "password": "test123"
            },
            follow=True
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
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign In")

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
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email already exists")
        self.assertFalse(
            User.objects.filter(username="user2").exists()
        )

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
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Phone number already exists")
        self.assertFalse(
            User.objects.filter(username="user3").exists()
        )


class AdminManagementAPITest(TestCase):

    def create_patient_user(self, username, email, phone_number, first_name="Patient", last_name="User"):

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password="test123",
            role="patient"
        )

        profile = user.patientprofile
        profile.phone_number = phone_number
        profile.gender = "male" if username.endswith("one") else "female"
        profile.date_of_birth = date(2000, 1, 1)
        profile.emergency_contact = "7000000000"
        profile.save()
        return user

    def create_therapist_user(self, username, email, phone_number, is_verified=False):

        user = User.objects.create_user(
            username=username,
            first_name="Thera",
            last_name="Pist",
            email=email,
            password="test123",
            role="therapist"
        )

        profile = user.therapistprofile
        profile.phone_number = phone_number
        profile.date_of_birth = date(1990, 1, 1)
        profile.specialization = "Counselling"
        profile.qualification = "MSc Psychology"
        profile.experience_years = 5
        profile.bio = "Experienced therapist"
        profile.is_verified = is_verified
        profile.save()
        return user

    def setUp(self):

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="test123",
            role="admin"
        )

        self.patient_one = self.create_patient_user(
            "patientone",
            "patient1@test.com",
            "9000000001"
        )

        self.patient_two = self.create_patient_user(
            "patienttwo",
            "patient2@test.com",
            "9000000002"
        )

        self.therapist_one = self.create_therapist_user(
            "therapistone",
            "therapist1@test.com",
            "8000000001",
            is_verified=True
        )

        self.therapist_two = self.create_therapist_user(
            "therapisttwo",
            "therapist2@test.com",
            "8000000002",
            is_verified=False
        )

    def login_admin(self):
        self.client.login(username="adminuser", password="test123")

    def test_admin_access_allowed(self):
        self.login_admin()
        response = self.client.get("/admin/profile/")
        self.assertEqual(response.status_code, 200)

    def test_admin_access_requires_authentication(self):
        response = self.client.get("/admin/profile/")
        self.assertEqual(response.status_code, 401)

    def test_non_admin_access_denied(self):
        self.client.login(username="patientone", password="test123")
        response = self.client.get("/admin/profile/")
        self.assertEqual(response.status_code, 403)

    def test_list_users(self):
        self.login_admin()
        response = self.client.get("/admin/users/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 5)
        self.assertEqual(payload[0]["username"], "therapisttwo")
        self.assertEqual(payload[-1]["username"], "adminuser")

    def test_user_details_for_patient(self):
        self.login_admin()
        response = self.client.get(f"/admin/users/{self.patient_one.id}/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["username"], "patientone")
        self.assertEqual(payload["role"], "patient")
        self.assertEqual(payload["phone_number"], "9000000001")
        self.assertEqual(payload["gender"], "male")

    def test_user_details_for_therapist(self):
        self.login_admin()
        response = self.client.get(f"/admin/users/{self.therapist_one.id}/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["username"], "therapistone")
        self.assertEqual(payload["role"], "therapist")
        self.assertEqual(payload["phone_number"], "8000000001")
        self.assertTrue(payload["is_verified"])

    def test_edit_user(self):
        self.login_admin()
        response = self.client.post(
            f"/admin/users/{self.patient_one.id}/edit/",
            {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@test.com"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.patient_one.refresh_from_db()
        self.assertEqual(self.patient_one.first_name, "Updated")
        self.assertEqual(self.patient_one.last_name, "Name")
        self.assertEqual(self.patient_one.email, "updated@test.com")

    def test_email_uniqueness_validation(self):
        self.login_admin()
        response = self.client.post(
            f"/admin/users/{self.patient_one.id}/edit/",
            {
                "email": self.patient_two.email
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_user(self):
        self.login_admin()
        response = self.client.delete(f"/admin/users/{self.patient_two.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(id=self.patient_two.id).exists())

    def test_role_change(self):
        self.login_admin()
        response = self.client.post(
            f"/admin/users/{self.patient_two.id}/change-role/",
            {
                "role": "therapist"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.patient_two.refresh_from_db()
        self.assertEqual(self.patient_two.role, "therapist")
        self.assertTrue(
            User.objects.filter(
                id=self.patient_two.id,
                therapistprofile__isnull=False
            ).exists()
        )

    def test_invalid_role_rejected(self):
        self.login_admin()
        response = self.client.post(
            f"/admin/users/{self.patient_two.id}/change-role/",
            {
                "role": "invalid_role"
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_roles_list(self):
        self.login_admin()
        response = self.client.get("/admin/roles/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 5)
        self.assertEqual(payload[0]["username"], "therapisttwo")
        self.assertEqual(payload[0]["current_role"], "therapist")

    def test_list_patients(self):
        self.login_admin()
        response = self.client.get("/admin/patients/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 2)
        self.assertEqual(payload[0]["username"], "patienttwo")

    def test_patient_detail(self):
        self.login_admin()
        response = self.client.get(f"/admin/patients/{self.patient_one.id}/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["username"], "patientone")
        self.assertEqual(payload["phone_number"], "9000000001")

    def test_list_therapists(self):
        self.login_admin()
        response = self.client.get("/admin/therapists/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 2)
        self.assertEqual(payload[0]["username"], "therapisttwo")

    def test_therapist_detail(self):
        self.login_admin()
        response = self.client.get(f"/admin/therapists/{self.therapist_one.id}/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["username"], "therapistone")
        self.assertTrue(payload["is_verified"])

    def test_therapist_verify(self):
        self.login_admin()
        response = self.client.post(f"/admin/therapists/{self.therapist_two.id}/verify/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            User.objects.get(id=self.therapist_two.id).therapistprofile.is_verified
        )

    def test_therapist_verify_rejects_non_therapist_id(self):
        self.login_admin()
        response = self.client.post(f"/admin/therapists/{self.patient_one.id}/verify/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["message"], "Therapist profile not found")

    def test_therapist_unverify(self):
        self.login_admin()
        response = self.client.post(f"/admin/therapists/{self.therapist_one.id}/unverify/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.get(id=self.therapist_one.id).therapistprofile.is_verified
        )

    def test_search_users(self):
        self.login_admin()
        response = self.client.get("/admin/search/?q=8000000001")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["username"], "therapistone")

    def test_recent_users(self):
        self.login_admin()
        response = self.client.get("/admin/recent-users/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 5)
        self.assertEqual(payload[0]["username"], "therapisttwo")

    def test_profile_stats(self):
        self.login_admin()
        response = self.client.get("/admin/profile-stats/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_users"], 5)
        self.assertEqual(payload["patient_profiles"], 2)
        self.assertEqual(payload["therapist_profiles"], 2)
        self.assertEqual(payload["users_without_profiles"], 1)

    def test_verification_summary(self):
        self.login_admin()
        response = self.client.get("/admin/verification-summary/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["verified_therapists"], 1)
        self.assertEqual(payload["unverified_therapists"], 1)

    def test_admin_profile(self):
        self.login_admin()
        response = self.client.get("/admin/profile/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["username"], "adminuser")
        self.assertEqual(payload["email"], "admin@test.com")
        self.assertEqual(payload["role"], "admin")
