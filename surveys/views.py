from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Survey, Patient
from .serializers import CompletedPatientSerializer, PendingPatientSerializer, SurveySectionRiskSerializer, SurveySerializer, SurveyDisplaySerializer, DashboardSerializer
from rest_framework.views import APIView

class SurveyCreateView(generics.CreateAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

# --------------------  survey completed list --------------------
class PatientCompletedSurveys(generics.ListAPIView):
    serializer_class = CompletedPatientSerializer

    def get_queryset(self):
        # Return surveys with status 'postoperative' or 'Post Operative'
        return Survey.objects.filter(status__in=["postoperative", "Post Operative"])
    
# --------------------  survey not completed list --------------------
class PatientNotCompletedSurveys(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctor = request.user
        patients = Patient.objects.filter(doctor=doctor)
        pending_patients = []

        for patient in patients:
            survey = Survey.objects.filter(patient=patient).order_by("-created_at").first()
            patient_dict = {
                "pk": patient.pk,             # ✅ database primary key
                "id": patient.patient_id,     # custom patient ID
                "name": patient.name,
            }

            if survey:
                if survey.status.lower() != "postoperative":
                    patient_dict["status"] = survey.status
                    pending_patients.append(patient_dict)
            else:
                patient_dict["status"] = "Not Started"
                pending_patients.append(patient_dict)

        return Response(pending_patients)



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
        # ✅ return single Survey row per patient
        return Survey.objects.filter(patient=patient).first()



# -------------------- Dashboard API --------------------
class DashboardView(generics.GenericAPIView):
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        doctor = request.user  # assuming doctor is the logged-in user

        # ✅ Get only patients of this doctor
        patients = Patient.objects.filter(doctor=doctor)

        total_patients = patients.count()

        # ✅ Get latest survey per patient
        pending_surveys = 0
        high_risk_patients = 0
        surveyed_count = 0

        for patient in patients:
            survey = Survey.objects.filter(patient=patient).order_by("-created_at").first()
            if survey:
                surveyed_count += 1
                if survey.risk_level and survey.risk_level.lower() == "high" or "very high":
                    high_risk_patients += 1
                if survey.status.lower() != "postoperative":
                    pending_surveys += 1
            else:
                # Patient without any survey → considered pending
                pending_surveys += 1  

        data = {
            "total_surveyed": surveyed_count,   # only patients with at least 1 survey
            "pending_surveys": pending_surveys,
            "high_risk_patients": high_risk_patients,
            "total_patients": total_patients    # ✅ add if you want full count
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)



class SurveyByPatientWithRiskView(generics.RetrieveAPIView):
    serializer_class = SurveySectionRiskSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        patient = get_object_or_404(Patient, id=patient_id)
        survey = Survey.objects.filter(patient=patient).first()
        if not survey:
            return Response({"detail": "No survey found"}, status=404)

        # Prepare section scores
        section_data = []
        risk_level = survey.risk_level.lower() if survey.risk_level else "low"
        risk_dict = {
            "low": "Standard anesthesia; routine monitoring.",
            "moderate": "Lung-protective ventilation, multimodal analgesia, encourage early mobilization.",
            "high": "Prefer regional if feasible, strict lung-protective strategy, consider postoperative ICU/HDU.",
            "very high": "Strongly consider avoiding GA/ETT if possible; optimize comorbidities pre-op, mandatory ICU planning."
        }

        for section in survey.section_scores.all():
            section_data.append({
                "section_name": section.section_name,
                "score": section.score,
                "risk_advice": risk_dict.get(risk_level, "Standard anesthesia; routine monitoring.")
            })

        return Response(section_data)