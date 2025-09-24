from rest_framework import generics, permissions
from .models import Survey
from .serializers import SurveySerializer

class SurveyCreateAPIView(generics.CreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]

    # you may override perform_create to set doctor from request.user if applicable
