from decimal import Decimal

from django.conf import settings
from django.db import models


class Account(models.Model):

    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"

    ACCOUNT_TYPES = [
        (SAVINGS, "Savings Account"),
        (CURRENT, "Current Account"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
    )

    account_number = models.CharField(
        max_length=12,
        unique=True,
    )

    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES,
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    def save(self, *args, **kwargs):

        if not self.account_number:

           last_account = Account.objects.order_by("-id").first()

           if last_account:
              next_number = int(last_account.account_number) + 1
           else:
              next_number = 100000000001

           self.account_number = str(next_number)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.account_number}"