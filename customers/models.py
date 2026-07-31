

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    
#FOR KYC UC22
class KYC(models.Model):

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

    KYC_STATUS = [
        (PENDING, "Pending"),
        (VERIFIED, "Verified"),
        (REJECTED, "Rejected"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kyc",
    )

    aadhaar_number = models.CharField(
        max_length=12,
        unique=True,
    )

    pan_number = models.CharField(
        max_length=10,
        unique=True,
    )

    address = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=KYC_STATUS,
        default=PENDING,
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_kycs",
    )

    def __str__(self):
        return (
            f"{self.user.username} - {self.status}"
        )