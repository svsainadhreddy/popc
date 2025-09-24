from rest_framework import serializers
from .models import Survey, Section, Question, Answer
from patients.models import Patient

class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Answer
        fields = ['question_id', 'selected_option', 'score']

class SectionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['name', 'score', 'answers']

    def get_answers(self, section):
        # filter answers by survey+section if you have those fields
        answers = Answer.objects.filter(section=section)
        return AnswerSerializer(answers, many=True).data



class SurveySerializer(serializers.ModelSerializer):
    # nested
    sections = SectionSerializer(many=True)
    patient_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'patient_id', 'total_score', 'risk_level', 'recommendation', 'sections']
        read_only_fields = ['id']

    def create(self, validated_data):
        sections_data = validated_data.pop('sections')
        patient_id = validated_data.pop('patient_id')
        survey = Survey.objects.create(patient_id=patient_id, **validated_data)
        for sec_data in sections_data:
            answers_data = sec_data.get('answers', [])
            section = Section.objects.create(survey=survey, **sec_data)
            for ans_data in answers_data:
                question_id = ans_data.pop('question_id')
                Answer.objects.create(survey=survey, question_id=question_id, **ans_data)
        return survey
