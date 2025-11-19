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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return surveys with status 'postoperative' or 'Post Operative'
        return Survey.objects.filter(status__in=["postoperative", "Post Operative"])

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []

        for survey in queryset:
            patient = survey.patient

            # Build full URL for photo
            photo_url = None
            if patient.photo:
                scheme = 'https' if request.is_secure() else 'http'
                host = request.get_host()
                photo_url = f"{scheme}://{host}{patient.photo.url}"

            data.append({
                "pk": patient.id,
                "id": patient.patient_id,
                "name": patient.name,
                "photoUrl": photo_url  # send as photoUrl for consistency
            })

        return Response(data)

    
# --------------------  survey not completed list --------------------
class PatientNotCompletedSurveys(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctor = request.user
        patients = Patient.objects.filter(doctor=doctor)
        pending_patients = []

        for patient in patients:
            # Get latest survey for patient
            survey = Survey.objects.filter(patient=patient).order_by("-created_at").first()

            # Build full photo URL if exists
            photo_url = None
            if patient.photo:
                scheme = 'https' if request.is_secure() else 'http'
                host = request.get_host()
                photo_url = f"{scheme}://{host}{patient.photo.url}"

            # Determine status
            status = "Not Started"
            if survey:
                if survey.status:
                    status = survey.status

            # Only include pending surveys (not postoperative)
            if not survey or survey.status.lower() != "postoperative":
                patient_dict = {
                    "pk": patient.id,
                    "id": patient.patient_id,
                    "name": patient.name,
                    "status": status,
                    "photo": photo_url
                }
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
                if survey.risk_level and survey.risk_level.lower() in ["high", "very high"]:
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
    
#---------------------Dashboard view for pie chart---------------------
class DashboardView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        doctor = request.user
        patients = Patient.objects.filter(doctor=doctor)

        total_patients = patients.count()

        # Part 1: Survey completion & risk counts
        pending_surveys = 0
        high_risk_patients = 0
        surveyed_count = 0

        # Part 2: Counts by risk level for postoperative surveys
        stable_count = 0
        moderate_count = 0
        high_risk_count = 0

        for patient in patients:
            surveys = Survey.objects.filter(patient=patient).order_by("-created_at")
            latest_survey = surveys.first()

            # Aggregate for survey completion & risks (all surveys)
            if latest_survey:
                if latest_survey.risk_level and latest_survey.risk_level.lower() in ["high", "very high"]:
                    high_risk_patients += 1
                if latest_survey.status.lower() != "postoperative":
                    pending_surveys += 1
                if latest_survey.status.lower() == "postoperative":
                    surveyed_count += 1

            else:
                pending_surveys += 1  # no survey → pending

            # Aggregate for pie chart (only postoperative status)
            postop_survey = surveys.filter(status="postoperative").first()
            if postop_survey and postop_survey.risk_level:
                risk = postop_survey.risk_level.lower()
                if risk == "low":
                    stable_count += 1
                elif risk == "moderate":
                    moderate_count += 1
                elif risk in ["high", "very high"]:
                    high_risk_count += 1

        total_risk_surveys = stable_count + moderate_count + high_risk_count or 1
        stable_pct = round((stable_count / total_risk_surveys) * 100, 2)
        moderate_pct = round((moderate_count / total_risk_surveys) * 100, 2)
        high_risk_pct = round((high_risk_count / total_risk_surveys) * 100, 2)

        data = {
            # dashboard counts
            "total_surveyed": surveyed_count,
            "pending_surveys": pending_surveys,
            "high_risk_patients": high_risk_patients,
            "total_patients": total_patients,

            # pie chart percentages
            "stable": stable_pct,
            "pending": moderate_pct,
            "high_risk": high_risk_pct,
        }

        return Response(data)

# -------------------- High Risk / Completed Patients with Risk --------------------
class HighRiskPatients(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ✅ Only postoperative surveys with High or Very High risk
        surveys = Survey.objects.filter(
            status__iexact="postoperative",
            risk_level__in=["High", "Very High"]
        )
        data = []

        for survey in surveys:
            patient = survey.patient

            # Build full photo URL if photo exists
            photo_url = None
            if patient.photo:
                scheme = 'https' if request.is_secure() else 'http'
                host = request.get_host()
                photo_url = f"{scheme}://{host}{patient.photo.url}"

            # Risk level (fallback = "Unknown")
            risk = survey.risk_level or "Unknown"

            # ✅ Append only high-risk patients
            data.append({
                "pk": patient.id,
                "id": patient.patient_id,
                "name": patient.name,
                "photoUrl": photo_url,
                "risk_status": risk,
            })

        return Response(data)


class SurveySectionAnswersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        section_name = request.query_params.get("section", "")
        if not section_name:
            return Response({"error": "Section name required"}, status=400)

        patient = get_object_or_404(Patient, id=patient_id)
        survey = Survey.objects.filter(patient=patient).order_by("-created_at").first()

        if not survey:
            return Response({"answers": []})

        # Filter answers only for the given section
        answers = survey.answers.filter(section_name=section_name)

        return Response({
            "answers": [
                {"question": a.question, "selected_option": a.selected_option}
                for a in answers
            ]
        })




