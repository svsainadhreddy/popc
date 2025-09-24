from django.db import models
from patients.models import Patient  # or wherever your Patient model is
from accounts.models import Doctor

class Survey(models.Model):
    """
    Represents one completed survey/assessment for a patient.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="surveys")
    doctor  = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name="surveys")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=50, blank=True)
    recommendation = models.TextField(blank=True)

    def __str__(self):
        return f"Survey #{self.pk} — {self.patient}"


class Section(models.Model):
    """
    Each survey is divided into sections (e.g. Patient Demographics, Medical History, etc.)
    Store the score per section.
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=100)  # e.g. "Patient Demographics", "Medical History"
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ("survey", "name")

    def __str__(self):
        return f"{self.survey} — {self.name}"


class Question(models.Model):
    """
    Master question bank. Each question belongs to a section (category).
    """
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=255)
    # Optionally, you can store possible choices, or just send plain text choices from client

    def __str__(self):
        return f"{self.section.name}: {self.text}"


class Answer(models.Model):
    """
    Stores the patient's answer (clicked option) plus the awarded score for that question.
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=255)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ("survey", "question")

    def __str__(self):
        return f"{self.survey.patient} — {self.question.text}: {self.selected_option}"
