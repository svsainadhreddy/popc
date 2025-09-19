from django.urls import path
from .views import PatientCreateView, PatientDeleteView, PatientUpdateView, PatientDetailView, PatientListView

urlpatterns = [
    path('create/', PatientCreateView.as_view(), name='create-patient'),
    path('<int:pk>/update/', PatientUpdateView.as_view(), name='update-patient'),
        path('<int:pk>/delete/', PatientDeleteView.as_view(), name='delete-patient'), 
    path('<int:pk>/', PatientDetailView.as_view(), name='get-patient'),
    path('', PatientListView.as_view(), name='list-patients'),

]
