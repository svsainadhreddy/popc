from django.urls import path
from .views import DoctorProfileUpdateView, DoctorProfileView, RegisterView, CustomAuthToken

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path("profile/", DoctorProfileView.as_view(), name="doctor-profile"),
    path("profile/update/", DoctorProfileUpdateView.as_view(), name="doctor-profile-update"),
]
