# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import datetime

class Doctor(AbstractUser):
    doctor_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=200, blank=True)
    profile_image = models.ImageField(upload_to="doctor_profiles/", null=True, blank=True)

    # NEW FIELDS FOR OTP RESET
    reset_otp = models.CharField(max_length=6, blank=True, null=True)
    reset_otp_created = models.DateTimeField(null=True, blank=True)

    def generate_otp(self):
        otp = f"{random.randint(100000, 999999)}"
        self.reset_otp = otp
        self.reset_otp_created = datetime.datetime.now()
        self.save()
        return otp
