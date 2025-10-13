from django.db import models
from patients.models import Patient


class Survey(models.Model):
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("not_completed", "Not Completed"),
        ("patient_Demographics","Patient Demographics"),
        ("medical_history","Medical History"),
        ("surgery_Factors","Surgery Factors"),
        ("preoperative_considerations","Preoperative Considerations"),
        ("postoperative","Post Operative"),
        ("planned_Anesthesia","Planned Anesthesia"),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="surveys"
    )
    total_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=50, blank=True, null=True)  # optional
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="not_completed"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Survey for {self.patient.name} ({self.status})"


class SectionScore(models.Model):
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="section_scores"
    )
    section_name = models.CharField(max_length=200)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.section_name} - {self.score}"


class Answer(models.Model):
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="answers"
    )
    section_name = models.CharField(max_length=200)
    question = models.CharField(max_length=255)
    selected_option = models.CharField(max_length=255)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.question} -> {self.selected_option} ({self.score})"
