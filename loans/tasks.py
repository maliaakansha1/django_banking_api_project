from celery import shared_task

from .models import Loan
from .services_emi import generate_emi_schedule


@shared_task
def generate_emi_schedule_task(
    loan_id,
):
    """
    Generate EMI schedule for an approved loan.
    """

    loan = Loan.objects.get(
        id=loan_id,
    )

    return generate_emi_schedule(
        loan=loan,
    )