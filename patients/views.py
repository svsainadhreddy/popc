from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Patient
from .serializers import PatientSerializer
from django.db import transaction
import re

class PatientCreateView(generics.CreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def _generate_next_patient_id(self, doctor):
        """
        Generate next patient_id for a doctor in format PID0001, PID0002, ...
        Uses the last-created Patient for that doctor to derive the next number.
        """
        last = Patient.objects.filter(doctor=doctor).order_by('-id').first()
        if last and last.patient_id:
            m = re.search(r'(\d+)$', last.patient_id)
            if m:
                try:
                    n = int(m.group(1)) + 1
                except ValueError:
                    n = Patient.objects.filter(doctor=doctor).count() + 1
            else:
                n = Patient.objects.filter(doctor=doctor).count() + 1
        else:
            n = 1
        return f"PID{n:04d}"

    @transaction.atomic
    def perform_create(self, serializer):
        doctor = self.request.user
        # If client provided patient_id in request.data -> use it (after validation in serializer)
        provided_pid = self.request.data.get('patient_id', None)
        if provided_pid:
            serializer.save(doctor=doctor, patient_id=provided_pid)
        else:
            new_pid = self._generate_next_patient_id(doctor)
            serializer.save(doctor=doctor, patient_id=new_pid)

class GeneratePatientIdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _generate_next_patient_id(self, doctor):
        last = Patient.objects.filter(doctor=doctor).order_by('-id').first()
        if last and last.patient_id:
            m = re.search(r'(\d+)$', last.patient_id)
            if m:
                try:
                    n = int(m.group(1)) + 1
                except ValueError:
                    n = Patient.objects.filter(doctor=doctor).count() + 1
            else:
                n = Patient.objects.filter(doctor=doctor).count() + 1
        else:
            n = 1
        return f"PID{n:04d}"

    def get(self, request, *args, **kwargs):
        doctor = request.user
        next_pid = self._generate_next_patient_id(doctor)
        return Response({"patient_id": next_pid}, status=status.HTTP_200_OK)


class PatientUpdateView(generics.UpdateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Patient.objects.all()

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class PatientDetailView(generics.RetrieveAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    queryset = Patient.objects.all()


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
