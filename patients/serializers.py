from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['doctor']  # ✅ prevent client from sending doctor

    def validate(self, data):
        # Get doctor from request context
        doctor = self.context['request'].user
        patient_id = data.get('patient_id')
        # Check uniqueness
        if Patient.objects.filter(doctor=doctor, patient_id=patient_id).exists():
            raise serializers.ValidationError(
                "This patient_id already exists for this doctor."
            )
        return data
