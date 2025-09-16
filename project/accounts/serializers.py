from rest_framework import serializers
from .models import Doctor
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Doctor
        fields = ['doctor_id', 'name','username', 'email', 'phone', 'age', 'gender',
                  'specialization', 'password', 'password2']
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        doctor = Doctor(**validated_data)
        doctor.set_password(password)
        doctor.save()
        return doctor
class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["doctor_id", "name", "email", "phone", "age", "gender", "specialization", "profile_image"]
        read_only_fields = ["doctor_id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make all fields optional for PATCH/PUT
        for field in self.fields:
            if field != "doctor_id":
                self.fields[field].required = False
