from django.urls import path
from .views import (
    SurveyByPatientWithRiskView,
    SurveyCreateView,
    PatientCompletedSurveys,
    PatientNotCompletedSurveys,
    SurveyStatsView,
    SurveyByPatientView,
    DashboardView
)

urlpatterns = [
    path("surveys/", SurveyCreateView.as_view(), name="survey-create"),
    path("surveys/completed/", PatientCompletedSurveys.as_view(), name="completed-surveys"),
    path("surveys/not-completed/", PatientNotCompletedSurveys.as_view(), name="not-completed-surveys"),
    path("surveys/stats/", DashboardView.as_view(), name="survey-stats"),
    path("surveys/patient/<int:patient_id>/", SurveyByPatientView.as_view(), name="survey-by-patient"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),  # ✅ New
    path("surveys/patient-risk/<int:patient_id>/", SurveyByPatientWithRiskView.as_view(), name="survey-patient-risk"),
]
