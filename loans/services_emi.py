from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import EMI

def generate_emi_schedule(
    *,
    loan,
):
    """
    Generate EMI schedule for an approved loan.
    """

    principal = loan.loan_amount

    annual_interest_rate = loan.interest_rate

    tenure = loan.tenure_months

    monthly_interest_rate = (
        annual_interest_rate / Decimal("12") / Decimal("100")
    )
    emi_amount = (
        principal
        * monthly_interest_rate
        * (1 + monthly_interest_rate) ** tenure
    ) / (
        ((1 + monthly_interest_rate) ** tenure) - 1
    )

    emi_amount = emi_amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    
    remaining_balance = principal

    emi_objects = []

    due_date = timezone.now().date()
    
    for emi_number in range(1, tenure + 1):

       interest_amount = (
          remaining_balance * monthly_interest_rate
       ).quantize(
          Decimal("0.01"),
          rounding=ROUND_HALF_UP,
    )

       principal_amount = (
          emi_amount - interest_amount
       ).quantize(
          Decimal("0.01"),
          rounding=ROUND_HALF_UP,
    )

       remaining_balance = (
           remaining_balance - principal_amount
       ).quantize(
           Decimal("0.01"),
           rounding=ROUND_HALF_UP,
    )

       if remaining_balance < Decimal("0.00"):
          remaining_balance = Decimal("0.00")  
       emi_objects.append(

          EMI(

            loan=loan,

            emi_number=emi_number,

            due_date=due_date,

            emi_amount=emi_amount,

            principal_amount=principal_amount,

            interest_amount=interest_amount,

            remaining_balance=remaining_balance,

            status=EMI.PENDING,
        )
    )

       due_date += timedelta(days=30)
    
    
    with transaction.atomic():

       EMI.objects.bulk_create(
        emi_objects
    )

    return (
       f"{len(emi_objects)} EMI records generated successfully."
)