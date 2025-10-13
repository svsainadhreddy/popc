from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['doctor']

    def validate(self, data):
        doctor = self.context['request'].user
        instance = getattr(self, 'instance', None)

        # Use existing patient_id if not provided in request (for updates)
        patient_id = data.get('patient_id', None)
        if not patient_id and instance:
            patient_id = instance.patient_id

        if not patient_id:
            # No patient_id to validate
            return data

        qs = Patient.objects.filter(doctor=doctor, patient_id=patient_id)
        if instance:
            qs = qs.exclude(pk=instance.pk)  # skip current patient

        if qs.exists():
            raise serializers.ValidationError({
                "patient_id": "This patient_id already exists for this doctor."
            })

        return data
