from rest_framework import serializers
from .models import Survey, SectionScore, Answer, Patient

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["question", "selected_option", "score"]

class SectionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionScore
        fields = ["section_name", "score"]

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

        # Get or create survey for patient
        survey, created = Survey.objects.get_or_create(patient=patient)

        # ---------- Update total_score ----------
        if section_status.lower() == "postoperative":
            # Overwrite total score for postoperative
            survey.total_score = validated_data.get("total_score", survey.total_score)
        else:
            # Accumulate scores for previous sections
            section_total = sum(section.get("score", 0) for section in sections_data)
            survey.total_score = (survey.total_score or 0) + section_total

        # Update status and risk level
        survey.status = section_status
        survey.risk_level = validated_data.get("risk_level", survey.risk_level)
        survey.save()

        # Create or update SectionScore objects
        for section in sections_data:
            SectionScore.objects.update_or_create(
                survey=survey,
                section_name=section.get("section_name"),
                defaults={"score": section.get("score", 0)}
            )

        # Create or update Answer objects
        for ans in answers_data:
            Answer.objects.update_or_create(
                survey=survey,
                question=ans.get("question"),
                defaults={
                    "selected_option": ans.get("selected_option"),
                    "score": ans.get("score", 0)
                }
            )

        return survey


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
