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

        # ---------- Get or Create Survey ----------
        survey, _ = Survey.objects.get_or_create(patient=patient)

        # ---------- Update or Create Section Scores ----------
        for section in sections_data:
            SectionScore.objects.update_or_create(
                survey=survey,
                section_name=section.get("section_name"),
                defaults={"score": section.get("score", 0)},
            )

        # ---------- Recalculate Total Score ----------
        all_sections = SectionScore.objects.filter(survey=survey)
        survey.total_score = sum(sec.score for sec in all_sections)

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

        # ---------- Automatically Assign Section Name to Answers ----------
        # If multiple section names exist, map each answer to the correct one if possible.
        section_map = {s.get("section_name"): s.get("score") for s in sections_data}

        for ans in answers_data:
            section_name = ans.get("section_name") or next(iter(section_map.keys()), "General")

            Answer.objects.update_or_create(
                survey=survey,
                question=ans.get("question"),
                defaults={
                    "selected_option": ans.get("selected_option"),
                    "score": ans.get("score", 0),
                    "section_name": section_name,
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
