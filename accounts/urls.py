from django.urls import path
from .views_password_reset import (
    ForgotPasswordView,
    VerifyOtpView,
    ResetPasswordWithOtpView,
)
from .views import (
    DeleteAccountView,
    RegisterView,
    CustomAuthToken,
    DoctorProfileView,
    DoctorProfileUpdateView,
    ChangeUsernameView,
    ChangePasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", CustomAuthToken.as_view()),

    path("profile/", DoctorProfileView.as_view()),
    path("profile/update/", DoctorProfileUpdateView.as_view()),
    path("change-username/", ChangeUsernameView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),

    # NEW OTP workflow
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("verify-otp/", VerifyOtpView.as_view()),
    path("reset-password/", ResetPasswordWithOtpView.as_view()),
    path("delete-account/", DeleteAccountView.as_view(), name="delete-account"),
]
