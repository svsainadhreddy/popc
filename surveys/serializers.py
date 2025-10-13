from rest_framework import serializers
from .models import Survey, SectionScore, Answer
from patients.models import Patient


# ---------- Answer Serializer ----------
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["question", "selected_option", "score", "section_name"]


# ---------- SectionScore Serializer ----------
class SectionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionScore
        fields = ["section_name", "score"]


# ---------- Main Survey Serializer ----------
class SurveySerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        source="patient", queryset=Patient.objects.all()
    )
    answers = AnswerSerializer(many=True)
    section_scores = SectionScoreSerializer(many=True)

    class Meta:
        model = Survey
        fields = [
            "patient_id",
            "total_score",
            "risk_level",
            "status",
            "answers",
            "section_scores",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        answers_data = validated_data.pop("answers", [])
        sections_data = validated_data.pop("section_scores", [])
        patient = validated_data.pop("patient")
        section_status = validated_data.get("status", "")

        # Get or create Survey for the patient
        survey, created = Survey.objects.get_or_create(patient=patient)

        # ---------- Calculate total section score ----------
        section_total = sum(section.get("score", 0) for section in sections_data)
        survey.total_score = (survey.total_score or 0) + section_total

        # ---------- Determine Risk Level ----------
        total = survey.total_score
        if total <= 20:
            survey.risk_level = "Low"
        elif total <= 40:
            survey.risk_level = "Moderate"
        elif total <= 60:
            survey.risk_level = "High"
        else:
            survey.risk_level = "Very high"

        survey.status = section_status
        survey.save()

        # ---------- Create or Update SectionScore ----------
        for section in sections_data:
            SectionScore.objects.update_or_create(
                survey=survey,
                section_name=section.get("section_name"),
                defaults={"score": section.get("score", 0)},
            )

        # ---------- Automatically Assign Section Name to Answers ----------
        # Use section_name from first section if available
        section_name = None
        if sections_data:
            section_name = sections_data[0].get("section_name")

        for ans in answers_data:
            Answer.objects.update_or_create(
                survey=survey,
                question=ans.get("question"),
                defaults={
                    "selected_option": ans.get("selected_option"),
                    "score": ans.get("score", 0),
                    "section_name": section_name or survey.status or "General",
                },
            )

        return survey


# ---------- Display Serializer ----------
class SurveyDisplaySerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    section_scores = SectionScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = [
            "patient_id",
            "total_score",
            "risk_level",
            "status",
            "answers",
            "section_scores",
            "created_at",
        ]


# ---------- Dashboard Serializers ----------
class DashboardSerializer(serializers.Serializer):
    total_surveyed = serializers.IntegerField()
    pending_surveys = serializers.IntegerField()
    high_risk_patients = serializers.IntegerField()


class SurveySectionRiskSerializer(serializers.Serializer):
    section_name = serializers.CharField()
    score = serializers.IntegerField()
    risk_advice = serializers.CharField()


class PendingPatientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField()


# ---------- Completed Patients Serializer ----------
class CompletedPatientSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(source="patient.id", read_only=True)  # Patient DB PK
    id = serializers.CharField(source="patient.patient_id", read_only=True)  # Patient custom ID
    name = serializers.CharField(source="patient.name", read_only=True)  # Patient name

    class Meta:
        model = Survey
        fields = ["pk", "id", "name"]
