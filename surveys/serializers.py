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
        survey = Survey.objects.create(**validated_data)

        for section in sections_data:
            SectionScore.objects.create(survey=survey, **section)

        for ans in answers_data:
            Answer.objects.create(survey=survey, **ans)

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
