from rest_framework import serializers
from .models import Survey, SurveyAnswer, SurveySectionScore
from patients.models import Patient

class SurveyAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyAnswer
        fields = ("id", "question_text", "selected_option", "option_score")


class SurveySectionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySectionScore
        fields = ("id", "section_name", "section_score")


class SurveySerializer(serializers.ModelSerializer):
    answers = SurveyAnswerSerializer(many=True, required=False)
    section_scores = SurveySectionScoreSerializer(many=True, required=False)
    patient_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Survey
        fields = ("id", "patient_id", "total_score", "answers", "section_scores", "created_at")

    def create(self, validated_data):
        answers_data = validated_data.pop("answers", [])
        section_scores_data = validated_data.pop("section_scores", [])
        patient_id = validated_data.pop("patient_id")

        try:
            patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            raise serializers.ValidationError({"patient_id": "Patient not found"})

        # attach doctor if patient has doctor foreign key
        doctor = getattr(patient, "doctor", None)

        survey = Survey.objects.create(patient=patient, doctor=getattr(patient, "doctor", None),
                                       **validated_data)

        for ans in answers_data:
            SurveyAnswer.objects.create(survey=survey, **ans)

        for sec in section_scores_data:
            SurveySectionScore.objects.create(survey=survey, **sec)

        return survey
