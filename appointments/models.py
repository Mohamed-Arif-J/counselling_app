from django.db import models


# Create your models here.
class Appointment(models.Model):
    patient = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="patient_appointments"
    )
    therapist = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="therapist_appointments"
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, default="Pending")

    def __str__(self):
        return f"Appointment {self.id}: {self.patient.username} with {self.therapist.username}"


class SessionNote(models.Model):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name="session_note"
    )
    therapist = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    private_notes = models.TextField()
    shared_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
