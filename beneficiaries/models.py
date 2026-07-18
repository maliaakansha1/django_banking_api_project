from django.db import models

# Create your models here.
from django.db import models

from customers.models import User
from accounts.models import Account


class Beneficiary(models.Model):
    
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACTIVE, "Active"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="beneficiaries",
    )

    beneficiary_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    cooling_ends_at = models.DateTimeField()
    
    class Meta:

        unique_together = (
            "user",
            "beneficiary_account",
        )

    def __str__(self):

        return (
            f"{self.user.username} → "
            f"{self.beneficiary_account.account_number}"
        )