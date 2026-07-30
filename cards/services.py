import random

from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import transaction
from .models import Card

from accounts.models import Account
from transactions.services import create_transaction
from transactions.models import Transaction
from notifications.tasks import send_email_task

def generate_card_number():

    while True:

        card_number = "".join(
            str(random.randint(0, 9))
            for _ in range(16)
        )

        if not Card.objects.filter(
            card_number=card_number
        ).exists():

            return card_number

def generate_cvv():

    return "".join(
        str(random.randint(0, 9))
        for _ in range(3)
    )
    
def generate_expiry_date():

    return (
        date.today()
        + relativedelta(years=5)
    )
    
def issue_card(
    *,
    account,
):
    existing_card = Card.objects.filter(
          account=account,
          status=Card.ACTIVE,
    ).first()

    if existing_card:

       raise ValueError(
        "An active debit card already exists for this account."
    )

    card = Card.objects.create(

        account=account,

        card_holder_name=account.user.get_full_name()
        or account.user.username,

        card_number=generate_card_number(),

        cvv=generate_cvv(),

        expiry_date=generate_expiry_date(),

    )

    return card

def toggle_card_status(
    *,
    card,
):

    with transaction.atomic():

        if card.status == Card.ACTIVE:

            card.status = Card.BLOCKED

        else:

            card.status = Card.ACTIVE

        card.save(
            update_fields=["status"],
        )

    return card

def update_transaction_limit(
    *,
    card,
    transaction_limit,
):

    with transaction.atomic():

        card.transaction_limit = transaction_limit

        card.save(
            update_fields=[
                "transaction_limit",
            ],
        )

    return card


def simulate_card_transaction(
    *,
    card_number,
    cvv,
    expiry_date,
    amount,
):

    try:

        card = Card.objects.select_related(
            "account",
            "account__user",
        ).get(
            card_number=card_number,
        )

    except Card.DoesNotExist:

        raise ValueError(
            "Invalid card details."
        )

    if card.cvv != cvv:

        raise ValueError(
            "Invalid card details."
        )

    if card.expiry_date != expiry_date:

        raise ValueError(
            "Invalid card details."
        )

    if card.status != Card.ACTIVE:

        raise ValueError(
            "Card is blocked."
        )

    if amount > card.transaction_limit:

        raise ValueError(
            "Transaction exceeds card limit."
        )

    account = card.account

    if account.balance < amount:

        raise ValueError(
            "Insufficient account balance."
        )

    with transaction.atomic():

        account.balance -= amount

        account.save(
            update_fields=[
                "balance",
            ],
        )

        create_transaction(
            account=account,
            transaction_type=Transaction.CARD_PAYMENT,
            amount=amount,
            balance_after_transaction=account.balance,
            remarks="Debit Card Transaction",
        )

    send_email_task.delay(
        subject="Debit Card Transaction",
        receiver_email=account.user.email,
        body=(
            f"Dear {account.user.username},\n\n"
            f"Your debit card transaction of ${amount} "
            f"was successful.\n\n"
            f"Remaining Balance: ${account.balance}\n\n"
            "Thank you for banking with us."
        ),
    )

    return account