from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Survey, Patient
from .serializers import SurveySerializer, SurveyDisplaySerializer, DashboardSerializer

class SurveyCreateView(generics.CreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

class PatientCompletedSurveys(generics.ListAPIView):
    serializer_class = SurveySerializer
    def get_queryset(self):
        return Survey.objects.filter(status="completed")

class PatientNotCompletedSurveys(generics.ListAPIView):
    serializer_class = SurveySerializer
    def get_queryset(self):
        return Survey.objects.filter(status="not_completed")

class SurveyStatsView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        total_completed = Survey.objects.filter(status="completed").count()
        total_not_completed = Survey.objects.filter(status="not_completed").count()
        return Response({
            "completed": total_completed,
            "not_completed": total_not_completed
        })

class SurveyByPatientView(generics.RetrieveAPIView):
    serializer_class = SurveyDisplaySerializer
    def get_object(self):
        patient_id = self.kwargs.get("patient_id")
        patient = get_object_or_404(Patient, id=patient_id)
        return Survey.objects.filter(patient=patient).order_by("-created_at").first()

# -------------------- Dashboard API --------------------
class DashboardView(generics.GenericAPIView):
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total_surveyed = Survey.objects.filter(status="completed").count()
        pending_surveys = Survey.objects.filter(status="not_completed").count()
        high_risk_patients = Survey.objects.filter(risk_level__iexact="high").count()

        data = {
            "total_surveyed": total_surveyed,
            "pending_surveys": pending_surveys,
            "high_risk_patients": high_risk_patients
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)
