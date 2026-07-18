from django.db import models

# Create your models here.
from django.db import models

from customers.models import User
from accounts.models import Account


class Beneficiary(models.Model):

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

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

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