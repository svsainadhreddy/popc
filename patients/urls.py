from django.urls import path
from . import views

urlpatterns = [
    path('next-id/', views.GeneratePatientIdView.as_view(), name='generate-patient-id'),
    path('create/', views.PatientCreateView.as_view(), name='create-patient'),
    path('<int:pk>/update/', views.PatientUpdateView.as_view(), name='update-patient'),
    path('<int:pk>/delete/', views.PatientDeleteView.as_view(), name='delete-patient'),
    path('<int:pk>/', views.PatientDetailView.as_view(), name='get-patient'),
    path('', views.PatientListView.as_view(), name='list-patients'),
]
