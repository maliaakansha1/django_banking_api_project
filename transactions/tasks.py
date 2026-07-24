from celery import shared_task

from .services import (
    credit_monthly_interest,
)


@shared_task
def credit_monthly_interest_task():
    """
    Celery task to credit monthly interest.
    """

    credit_monthly_interest()

    return "Monthly interest credited successfully."