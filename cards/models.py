from django.db import models

# Create your models here.
from django.db import models
from accounts.models import Account


class Card(models.Model):

    DEBIT = "DEBIT"

    CARD_TYPES = [
        (DEBIT, "Debit Card"),
    ]

    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"

    CARD_STATUS = [
        (ACTIVE, "Active"),
        (BLOCKED, "Blocked"),
    ]

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="cards",
    )

    card_holder_name = models.CharField(
        max_length=100,
    )

    card_number = models.CharField(
        max_length=16,
        unique=True,
    )

    cvv = models.CharField(
        max_length=3,
    )

    expiry_date = models.DateField()

    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPES,
        default=DEBIT,
    )

    status = models.CharField(
        max_length=20,
        choices=CARD_STATUS,
        default=ACTIVE,
    )
    transaction_limit = models.DecimalField(
       max_digits=12,
       decimal_places=2,
       default=50000.00,
)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):

        return (
            f"{self.card_holder_name} - "
            f"{self.card_number[-4:]}"
        )