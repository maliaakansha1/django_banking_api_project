from celery import shared_task

from django.utils import timezone
from django.core.files import File

from .models import StatementRequest
from .pdf_generator import generate_statement_pdf

from notifications.tasks import send_email_task
@shared_task
def generate_statement(
    statement_request_id,
):

    statement_request = (
        StatementRequest.objects.get(
            id=statement_request_id,
        )
    )

    statement_request.status = (
        StatementRequest.PROCESSING
    )

    statement_request.save(
        update_fields=["status"],
    )

    pdf_path = generate_statement_pdf(
        statement_request
    )

    with open(
        pdf_path,
        "rb",
    ) as pdf:

        statement_request.statement_file.save(
            pdf_path.split("/")[-1],
            File(pdf),
            save=False,
        )

    statement_request.status = (
        StatementRequest.COMPLETED
    )

    statement_request.completed_at = (
        timezone.now()
    )

    statement_request.save()
    
    send_email_task.delay(
       subject="Bank Statement Generated",
        receiver_email="aakanshamali01@gmail.com",
        body=(
             f"Dear {statement_request.user.username},\n\n"
              "Your account statement has been generated successfully.\n\n"
              "You can now download it from the banking application.\n\n"
              "Thank you for banking with us."
    ),
)
    
    # ---------------- UC12 ---------------- #
@shared_task
def scheduled_test_task():

    print("=" * 50)
    print("CELERY BEAT IS WORKING")
    print(f"Executed at: {timezone.now()}")
    print("=" * 50)

    return "SUCCESS"