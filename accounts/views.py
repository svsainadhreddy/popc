from rest_framework import generics,permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Doctor
from .serializers import RegisterSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Doctor
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Doctor
from .serializers import DoctorProfileSerializer

from django.contrib.auth.password_validation import validate_password

class RegisterView(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = RegisterSerializer

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        doctor = token.user
        return Response({
            "token": token.key,
            "doctor_id": doctor.doctor_id,
            "username": doctor.username,
            "email": doctor.email
        })
        

        

# UPDATE profile (with image)
class DoctorProfileUpdateView(generics.UpdateAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user   
        
       #image          
class DoctorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
#username and password
class ChangeUsernameView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        new_username = request.data.get("username")
        if not new_username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.username = new_username
        user.save()
        return Response({"message": "Username updated successfully"}, status=status.HTTP_200_OK)


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        user = request.user
        if not user.check_password(old_password):
            return Response({"error": "Incorrect old password"}, status=status.HTTP_400_BAD_REQUEST)



        user.set_password(new_password)
        user.save()
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
    