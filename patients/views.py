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