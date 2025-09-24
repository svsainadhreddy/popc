from django.contrib.auth.models import AbstractUser
from django.db import models

class Doctor(AbstractUser):
    doctor_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=200, blank=True)

    profile_image = models.ImageField(upload_to="doctor_profiles/", null=True, blank=True)

    def __str__(self):
        return f"{self.doctor_id} - {self.username}"
