from celery import shared_task
import logging

from .services import send_email

logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_email_task(
    subject,
    receiver_email,
    body,
):

    try:

        send_email(
            subject=subject,
            receiver_email=receiver_email,
            body=body,
        )

        return "Email Sent Successfully"

    except Exception as exc:

        logger.exception(
            "Email sending failed."
        )

        raise exc