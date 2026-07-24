from .models import Loan

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