from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Doctor

# ------------------ Register / Profile Serializers ------------------

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Doctor
        fields = [
            'doctor_id', 'name','username', 'email', 'phone', 'age', 'gender',
            'specialization', 'password', 'password2'
        ]

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        doctor = Doctor(**validated_data)
        doctor.set_password(password)
        doctor.save()
        return doctor


class DoctorProfileSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            "doctor_id", "name", "email", "phone", "age", "gender",
            "specialization", "profile_image", "profile_image_url"
        ]
        read_only_fields = ["doctor_id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make all fields optional for PATCH/PUT
        for field in self.fields:
            if field != "doctor_id":
                self.fields[field].required = False

    def get_profile_image_url(self, obj):
        request = self.context.get('request')
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            url = obj.profile_image.url
            if url.startswith('http://') or url.startswith('https://'):
                return url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None


# ------------------ OTP / Password Reset Serializers ------------------

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Accepts 'identifier' which can be username or email.
    """
    identifier = serializers.CharField()


class VerifyOtpSerializer(serializers.Serializer):
    """
    Accepts identifier + otp to verify code.
    """
    identifier = serializers.CharField()
    otp = serializers.CharField(max_length=10)


class ResetPasswordWithOtpSerializer(serializers.Serializer):
    """
    Accepts identifier + otp + new_password to actually reset password.
    """
    identifier = serializers.CharField()
    otp = serializers.CharField(max_length=10)
    new_password = serializers.CharField(write_only=True, min_length=8)


# ------------------ Optional: Backwards-compatible Confirm Serializer ------------------
# If you're still using the previous uid/token based confirm endpoint anywhere,
# keep this serializer (not required for OTP flow).
class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
