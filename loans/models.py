from django.db import models

# Create your models here.
from decimal import Decimal

from django.conf import settings



class Loan(models.Model):

    PERSONAL = "PERSONAL"
    HOME = "HOME"
    VEHICLE = "VEHICLE"

    LOAN_TYPES = [
        (PERSONAL, "Personal Loan"),
        (HOME, "Home Loan"),
        (VEHICLE, "Vehicle Loan"),
    ]

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

    LOAN_STATUS = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",
    )

    loan_type = models.CharField(
        max_length=20,
        choices=LOAN_TYPES,
    )

    loan_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
    )

    tenure_months = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=LOAN_STATUS,
        default=PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.customer.username} - "
            f"{self.loan_type} - "
            f"{self.status}"
        )

from decimal import Decimal

class EMI(models.Model):

    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"

    EMI_STATUS = [
        (PENDING, "Pending"),
        (PAID, "Paid"),
        (FAILED,"Failed"),
    ]

    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name="emis",
    )

    emi_number = models.PositiveIntegerField()

    due_date = models.DateField()

    emi_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    principal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    interest_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    remaining_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    penalty_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
)

    status = models.CharField(
        max_length=20,
        choices=EMI_STATUS,
        default=PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "emi_number",
        ]

    def __str__(self):

        return (
            f"Loan {self.loan.id} - EMI {self.emi_number}"
        )