# accounts/views_password_reset.py

from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from accounts.serializers import ForgotPasswordSerializer
import datetime

from .models import Doctor
from .serializers import (
    ForgotPasswordSerializer,
    VerifyOtpSerializer,
    ResetPasswordWithOtpSerializer,
)

OTP_EXPIRY_MINUTES = 10


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]

        # find user
        try:
            if "@" in identifier:
                user = Doctor.objects.get(email__iexact=identifier)
            else:
                user = Doctor.objects.get(username__iexact=identifier)
        except Doctor.DoesNotExist:
            return Response({"message": "If account exists, OTP sent"}, status=200)

        # generate OTP
        otp = user.generate_otp()

        # send email
        send_mail(
            "POPC Password Reset OTP",
            f"Your OTP to reset password is: {otp}\nValid for 10 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

        return Response({"message": "OTP sent to registered email"}, status=200)


class VerifyOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        otp = serializer.validated_data["otp"]

        try:
            if "@" in identifier:
                user = Doctor.objects.get(email__iexact=identifier)
            else:
                user = Doctor.objects.get(username__iexact=identifier)
        except Doctor.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        # check OTP
        if user.reset_otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        # expiry check
        if user.reset_otp_created < timezone.now() - datetime.timedelta(minutes=OTP_EXPIRY_MINUTES):
            return Response({"error": "OTP expired"}, status=400)

        return Response({"message": "OTP verified"}, status=200)


class ResetPasswordWithOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordWithOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:
            if "@" in identifier:
                user = Doctor.objects.get(email__iexact=identifier)
            else:
                user = Doctor.objects.get(username__iexact=identifier)
        except Doctor.DoesNotExist:
            return Response({"error": "Invalid request"}, 400)

        if user.reset_otp != otp:
            return Response({"error": "Invalid OTP"}, 400)

        if user.reset_otp_created < timezone.now() - datetime.timedelta(minutes=OTP_EXPIRY_MINUTES):
            return Response({"error": "OTP expired"}, 400)

        # reset password
        user.set_password(new_password)
        user.reset_otp = None
        user.save()

        return Response({"message": "Password updated successfully"}, status=200)
