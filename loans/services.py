from .models import Loan
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from accounts.models import Account
from transactions.services import create_transaction
from transactions.models import Transaction
from .models import EMI
from datetime import timedelta
from notifications.tasks import send_email_task
def apply_loan(
    *,
    user,
    loan_type,
    loan_amount,
    interest_rate,
    tenure_months,
):
    """
    Apply for a new loan.
    """

    loan = Loan.objects.create(
        customer=user,
        loan_type=loan_type,
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        tenure_months=tenure_months,
        status=Loan.PENDING,
    )

    return loan



def update_loan_status(
    *,
    loan,
    status,
):
    """
    Approve or reject a loan.
    """

    if loan.status != Loan.PENDING:
        raise ValueError(
            "Loan has already been processed."
        )

    loan.status = status

    loan.save(
        update_fields=["status"],
    )
    if loan.status == Loan.APPROVED:
        from .tasks import generate_emi_schedule_task

        generate_emi_schedule_task.delay(
           loan.id,
    )

        subject = "Loan Approved"

        body = (
         f"Dear {loan.customer.username},\n\n"
         f"Congratulations!\n\n"
         f"Your {loan.loan_type} loan application "
         f"for ₹{loan.loan_amount} has been approved.\n\n"
         f"Interest Rate: {loan.interest_rate}%\n"
         f"Tenure: {loan.tenure_months} months\n\n"
         "Thank you for banking with us."
    )

    else:

       subject = "Loan Rejected"

       body = (
        f"Dear {loan.customer.username},\n\n"
        f"We regret to inform you that your "
        f"{loan.loan_type} loan application "
        f"for ₹{loan.loan_amount} has been rejected.\n\n"
        "For further details, please contact your branch.\n\n"
        "Thank you for banking with us."
    )

    send_email_task.delay(
      subject=subject,
      receiver_email="aakanshamali01@gmail.com",
      body=body,
)

    return loan

def list_loans(
    *,
    user,
):
    """
    Return all loans of the logged-in customer.
    """

    return (
        Loan.objects
        .filter(
            customer=user,
        )
        .order_by("-created_at")
    )




def process_due_emi():
    """
    Process all EMIs that are due today.
    """

    today = timezone.now().date()

    due_emis = EMI.objects.filter(
        due_date=today,
        status=EMI.PENDING,
    )

    for emi in due_emis:

        with transaction.atomic():

            account = (
                Account.objects
                .select_for_update()
                .filter(
                    user=emi.loan.customer,
                )
                .first()
            )

            if account is None:
                continue

            # Insufficient balance
            if account.balance < emi.emi_amount:

                emi.status = EMI.FAILED
                emi.penalty_amount += Decimal("250.00")
                emi.due_date += timedelta(days=7)

                emi.save(
                    update_fields=[
                        "status",
                        "penalty_amount",
                        "due_date",
                    ],
                )

                send_email_task.delay(
                    subject="EMI Auto Debit Failed",
                    receiver_email="aakanshamali01@gmail.com",
                    body=(
                        f"Dear {account.user.username},\n\n"
                        f"Your EMI payment of ₹{emi.emi_amount} "
                        "could not be processed due to "
                        "insufficient balance.\n\n"
                        "A penalty of ₹250 has been applied.\n"
                        "Your EMI has been rescheduled.\n\n"
                        "Please maintain sufficient balance."
                    ),
                )

                continue

            # Sufficient balance
            account.balance -= emi.emi_amount

            account.save(
                update_fields=["balance"],
            )

            create_transaction(
                account=account,
                transaction_type=Transaction.EMI_PAYMENT,
                amount=emi.emi_amount,
                balance_after_transaction=account.balance,
                remarks=f"EMI Payment - Loan #{emi.loan.id}",
            )

            emi.status = EMI.PAID

            emi.save(
                update_fields=["status"],
            )

            send_email_task.delay(
                subject="EMI Auto Debit Successful",
                receiver_email="aakanshamali01@gmail.com",
                body=(
                    f"Dear {account.user.username},\n\n"
                    f"Your EMI of ₹{emi.emi_amount} "
                    "has been successfully debited.\n\n"
                    f"Remaining Balance: ₹{account.balance}\n\n"
                    "Thank you for banking with us."
                ),
            )

    return (
        f"{due_emis.count()} due EMI(s) processed."
    )

from .models import EMI
def foreclose_loan(
    *,
    loan,
):
    """
    Foreclose an approved loan.
    """

    if loan.status != Loan.APPROVED:
        raise ValueError(
            "Only approved loans can be foreclosed."
        )

    pending_emi = (
        EMI.objects
        .filter(
            loan=loan,
            status=EMI.PENDING,
        )
        .order_by("emi_number")
        .first()
    )

    if pending_emi is None:
        raise ValueError(
            "Loan is already fully paid."
        )

    foreclosure_amount = pending_emi.remaining_balance

    with transaction.atomic():

        account = (
            Account.objects
            .select_for_update()
            .filter(
                user=loan.customer,
            )
            .first()
        )

        if account is None:
            raise ValueError(
                "Customer account not found."
            )

        if account.balance < foreclosure_amount:
            raise ValueError(
                "Insufficient balance for loan foreclosure."
            )

        # Deduct amount
        account.balance -= foreclosure_amount

        account.save(
            update_fields=["balance"],
        )

        # Create transaction
        create_transaction(
               account=account,
              transaction_type=Transaction.LOAN_FORECLOSURE,
               amount=foreclosure_amount,
                balance_after_transaction=account.balance,
                remarks=f"Loan Foreclosure - Loan #{loan.id}",
)

        # Close loan
        loan.status = Loan.CLOSED

        loan.save(
            update_fields=["status"],
        )

        # Cancel remaining EMIs
        EMI.objects.filter(
            loan=loan,
            status=EMI.PENDING,
        ).update(
            status=EMI.CANCELLED,
        )

    # Send email asynchronously
    send_email_task.delay(
        subject="Loan Foreclosed Successfully",
        receiver_email="aakanshamali01@gmail.com",
        body=(
            f"Dear {loan.customer.username},\n\n"
            "Your loan has been successfully foreclosed.\n\n"
            f"Loan Type : {loan.loan_type}\n"
            f"Foreclosure Amount Paid: ₹{foreclosure_amount}\n\n"
            "All remaining EMIs have been cancelled.\n\n"
            "Thank you for banking with us."
        ),
    )

    return loan