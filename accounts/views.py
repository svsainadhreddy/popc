from rest_framework import generics
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
        
# GET profile
class DoctorProfileView(generics.RetrieveAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # logged-in doctor
        

# UPDATE profile (with image)
class DoctorProfileUpdateView(generics.UpdateAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user       
