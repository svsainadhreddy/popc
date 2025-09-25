from django.db import models
from django.conf import settings

# import Patient model from your patients app
from patients.models import Patient

class Survey(models.Model):
    """
    One Survey instance per patient per assessment (can store total scores, section totals).
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="surveys")
    # optionally store doctor for quick access
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    total_score = models.IntegerField(default=0)
    # optional dictionary or text summary of section scores (if you want JSON)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Survey #{self.pk} for {self.patient}"


class SurveySectionScore(models.Model):
    """
    Optional: store per-section score (e.g., 'Demographics', 'Lifestyle', etc.)
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="section_scores")
    section_name = models.CharField(max_length=200)
    section_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.section_name}: {self.section_score} ({self.survey})"


class SurveyAnswer(models.Model):
    """
    Each answer record: which question, selected option text, and option score.
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="answers")
    question_text = models.TextField()
    selected_option = models.CharField(max_length=500)
    option_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.question_text[:40]} -> {self.selected_option} ({self.option_score})"
