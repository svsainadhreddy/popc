from django.urls import path

# from surveys.views_qwen import PPCQwenChatView
from .views import (
    HighRiskPatients,
    SurveyByPatientWithRiskView,
    SurveyCreateView,
    PatientCompletedSurveys,
    PatientNotCompletedSurveys,
    SurveySectionAnswersView,
    SurveyStatsView,
    SurveyByPatientView,
    DashboardView,
    PPCQwenChatView
    
)

urlpatterns = [
    path("surveys/", SurveyCreateView.as_view(), name="survey-create"),
    path("surveys/completed/", PatientCompletedSurveys.as_view(), name="completed-surveys"),
    path("surveys/not-completed/", PatientNotCompletedSurveys.as_view(), name="not-completed-surveys"),
    path("surveys/stats/", DashboardView.as_view(), name="survey-stats"),
    path("surveys/patient/<int:patient_id>/", SurveyByPatientView.as_view(), name="survey-by-patient"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),  
    path("surveys/patient-risk/<int:patient_id>/", SurveyByPatientWithRiskView.as_view(), name="survey-patient-risk"),
    path("surveys/high-risk/", HighRiskPatients.as_view(), name="high-risk-patients"),  
    path("surveys/<int:patient_id>/section-answers/",SurveySectionAnswersView.as_view(),name="survey-section-answers"),
    path("ppc-qwen-chat/", PPCQwenChatView.as_view()),
]
