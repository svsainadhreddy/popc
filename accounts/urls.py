from django.urls import path
from .views import ChangePasswordView, ChangeUsernameView, DoctorProfileUpdateView, DoctorProfileView, RegisterView, CustomAuthToken

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path("profile/", DoctorProfileView.as_view(), name="doctor-profile"),
    path("profile/update/", DoctorProfileUpdateView.as_view(), name="doctor-profile-update"),
    path('change-username/', ChangeUsernameView.as_view(), name='change-username'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
