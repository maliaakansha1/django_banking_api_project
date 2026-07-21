import os

from django.conf import settings

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from transactions.models import Transaction


def generate_statement_pdf(
    statement_request,
):

    account = statement_request.account

    transactions = (
        Transaction.objects
        .filter(
            account=account,
            created_at__date__gte=statement_request.from_date,
            created_at__date__lte=statement_request.to_date,
        )
        .order_by("created_at")
    )

    folder = os.path.join(
        settings.MEDIA_ROOT,
        "statements",
    )

    os.makedirs(
        folder,
        exist_ok=True,
    )

    filename = (
        f"statement_{statement_request.id}.pdf"
    )

    filepath = os.path.join(
        folder,
        filename,
    )

    pdf = canvas.Canvas(filepath)

    width, height = (
        8.5 * inch,
        11 * inch,
    )

    y = height - 50

    pdf.setFont(
        "Helvetica-Bold",
        18,
    )

    pdf.drawString(
        180,
        y,
        "ABC BANK",
    )

    y -= 30

    pdf.setFont(
        "Helvetica",
        14,
    )

    pdf.drawString(
        150,
        y,
        "Account Statement",
    )

    y -= 40

    pdf.setFont(
        "Helvetica",
        11,
    )

    pdf.drawString(
        40,
        y,
        f"Customer : {statement_request.user.username}",
    )

    y -= 20

    pdf.drawString(
        40,
        y,
        f"Account Number : {account.account_number}",
    )

    y -= 20

    pdf.drawString(
        40,
        y,
        f"From : {statement_request.from_date}",
    )

    y -= 20

    pdf.drawString(
        40,
        y,
        f"To : {statement_request.to_date}",
    )

    y -= 40

    pdf.setFont(
        "Helvetica-Bold",
        10,
    )

    pdf.drawString(
        40,
        y,
        "Date",
    )

    pdf.drawString(
        140,
        y,
        "Reference",
    )

    pdf.drawString(
        250,
        y,
        "Type",
    )

    pdf.drawString(
        340,
        y,
        "Amount",
    )

    pdf.drawString(
        440,
        y,
        "Balance",
    )

    y -= 20

    pdf.line(
        30,
        y,
        560,
        y,
    )

    y -= 20

    pdf.setFont(
        "Helvetica",
        9,
    )

    for transaction in transactions:

        if y < 60:

            pdf.showPage()

            y = height - 50

        pdf.drawString(
            40,
            y,
            transaction.created_at.strftime(
                "%d-%m-%Y"
            ),
        )

        pdf.drawString(
            140,
            y,
            transaction.reference_number,
        )

        pdf.drawString(
            250,
            y,
            transaction.transaction_type,
        )

        pdf.drawString(
            340,
            y,
            str(transaction.amount),
        )

        pdf.drawString(
            440,
            y,
            str(
                transaction.balance_after_transaction
            ),
        )

        y -= 18

    y -= 20

    pdf.line(
        30,
        y,
        560,
        y,
    )

    y -= 30

    pdf.drawString(
        40,
        y,
        f"Closing Balance : {account.balance}",
    )

    pdf.save()

    return filepath