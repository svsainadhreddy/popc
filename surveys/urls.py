from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurveyViewSet

router = DefaultRouter()
router.register(r"surveys", SurveyViewSet, basename="surveys")

urlpatterns = [
    path("", include(router.urls)),
]
