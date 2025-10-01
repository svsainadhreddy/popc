from django.urls import path
from .views import (
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
    path("surveys/stats/", SurveyStatsView.as_view(), name="survey-stats"),
    path("surveys/patient/<int:patient_id>/", SurveyByPatientView.as_view(), name="survey-by-patient"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),  # ✅ New
]
