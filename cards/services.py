import random

from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import transaction
from .models import Card

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