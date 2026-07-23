import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings

def send_email(
    subject,
    receiver_email,
    body,
):

    message = MIMEMultipart()

    message["From"] = (
        settings.EMAIL_HOST_USER
    )
    
    receiver_email = settings.TEST_EMAIL
    message["To"] = receiver_email

    message["Subject"] = subject

    message.attach(
        MIMEText(
            body,
            "plain",
        )
    )

    with smtplib.SMTP_SSL(
        settings.EMAIL_HOST,
        settings.EMAIL_PORT,
    ) as server:

        server.login(
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD,
        )

        server.sendmail(
            settings.EMAIL_HOST_USER,
            receiver_email,
            message.as_string(),
        )