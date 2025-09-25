from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Survey
from .serializers import SurveySerializer

class SurveyViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()

    # POST /api/surveys/  -> create survey with nested answers
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        survey = serializer.save()
        return Response(self.get_serializer(survey).data, status=status.HTTP_201_CREATED)

    # Optional: retrieve survey
    def retrieve(self, request, pk=None):
        survey = self.get_object()
        return Response(self.get_serializer(survey).data)
