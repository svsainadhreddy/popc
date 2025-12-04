# accounts/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import MultiPartParser, FormParser

from django.contrib.auth import authenticate

from .models import Doctor
from .serializers import RegisterSerializer, DoctorProfileSerializer
from rest_framework.views import APIView

class RegisterView(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = RegisterSerializer


class CustomAuthToken(ObtainAuthToken):
    """
    Allows login via username OR email.
    """
    def post(self, request, *args, **kwargs):
        data = request.data
        identifier = data.get("username") or data.get("email")
        password = data.get("password")

        # If identifier is an email
        if "@" in identifier:
            try:
                doctor = Doctor.objects.get(email__iexact=identifier)
                identifier = doctor.username  # convert to actual username
            except Doctor.DoesNotExist:
                pass

        user = authenticate(username=identifier, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=400)

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "doctor_id": user.doctor_id,
            "username": user.username,
            "email": user.email,
        })


class DoctorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class DoctorProfileUpdateView(generics.UpdateAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user


class ChangeUsernameView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        new_username = request.data.get("username")
        if not new_username:
            return Response({"error": "Username is required"}, status=400)

        user = request.user
        user.username = new_username
        user.save()

        return Response({"message": "Username updated"})


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        old = request.data.get("old_password")
        new = request.data.get("new_password")

        user = request.user

        if not user.check_password(old):
            return Response({"error": "Incorrect old password"}, status=400)

        user.set_password(new)
        user.save()
        return Response({"message": "Password updated"})



class DeleteAccountView(APIView):
    """
    DELETE: Delete the authenticated doctor's account and related data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        # Optionally record an audit log, or soft-delete instead of hard delete, depending on your app needs.

        # Delete the user -> this will cascade if related models have on_delete=CASCADE
        user.delete()

        return Response({"message": "Account and related data deleted"}, status=status.HTTP_204_NO_CONTENT)