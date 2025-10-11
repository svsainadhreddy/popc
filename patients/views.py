from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Patient
from .serializers import PatientSerializer

# Create patient
class PatientCreateView(generics.CreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)

# Update patient
class PatientUpdateView(generics.UpdateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'pk'
    queryset = Patient.objects.all()

    def update(self, request, *args, **kwargs):
        patient = self.get_object()
        new_patient_id = request.data.get("patient_id")

        if new_patient_id is not None:  # field is present in request
            new_patient_id = str(new_patient_id).strip()
            current_patient_id = str(patient.patient_id).strip()
            
            # Only check uniqueness if non-empty and changed
            if new_patient_id and new_patient_id != current_patient_id:
                exists = Patient.objects.filter(patient_id=new_patient_id).exclude(pk=patient.pk).exists()
                if exists:
                    return Response(
                        {"error": f"Patient ID '{new_patient_id}' already exists."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        return super().update(request, *args, **kwargs)  

# Retrieve patient
class PatientDetailView(generics.RetrieveAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    queryset = Patient.objects.all()

# List patients (optional search)
class PatientListView(generics.ListAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Patient.objects.filter(doctor=user)
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset
class PatientDeleteView(generics.DestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    queryset = Patient.objects.all()