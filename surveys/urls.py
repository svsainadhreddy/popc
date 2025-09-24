from django.urls import path
from .views import SurveyCreateAPIView

urlpatterns = [
    path('', SurveyCreateAPIView.as_view(), name='survey-create'),
]
