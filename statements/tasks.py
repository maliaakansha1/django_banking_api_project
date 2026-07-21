from celery import shared_task

from django.utils import timezone
from django.core.files import File

from .models import StatementRequest
from .pdf_generator import generate_statement_pdf


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
    
    # ---------------- UC12 ---------------- #
@shared_task
def scheduled_test_task():

    print("=" * 50)
    print("CELERY BEAT IS WORKING")
    print(f"Executed at: {timezone.now()}")
    print("=" * 50)

    return "SUCCESS"