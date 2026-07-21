from django.db import models

from django.conf import settings
from django.db import models

from accounts.models import Account


class StatementRequest(models.Model):

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="statement_requests",
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="statement_requests",
    )

    from_date = models.DateField()

    to_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    statement_file = models.FileField(
        upload_to="statements/",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.account.account_number} "
            f"- {self.status}"
        )
