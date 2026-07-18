from django.db import models

# Create your models here.
from django.db import models

from accounts.models import Account


class Transaction(models.Model):

    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"

    TRANSACTION_TYPES = [
        (DEPOSIT, "Deposit"),
        (WITHDRAW, "Withdraw"),
        (TRANSFER_IN, "Transfer In"),
        (TRANSFER_OUT, "Transfer Out"),
    ]

    reference_number = models.CharField(
        max_length=30,
        unique=True,
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    balance_after_transaction = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    remarks = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.reference_number} - "
            f"{self.transaction_type}"
        )