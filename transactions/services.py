from decimal import Decimal

from django.db import transaction

from accounts.models import Account


def deposit_money(
    *,
    user,
    account_number,
    amount,
):
    """
    Deposit money into the user's account.
    """

    if amount <= Decimal("0"):
        raise ValueError(
            "Amount must be greater than zero."
        )

    with transaction.atomic():

        account = (
            Account.objects
            .select_for_update()
            .filter(
                account_number=account_number,
                user=user,
            )
            .first()
        )

        if account is None:
            raise ValueError(
                "Account not found."
            )

        account.balance += amount

        account.save(
            update_fields=["balance"]
        )

        return account
    
    
    
    
def withdraw_money(
    *,
    user,
    account_number,
    amount,
):

    if amount <= Decimal("0"):
        raise ValueError(
            "Amount must be greater than zero."
        )

    with transaction.atomic():

        account = (
            Account.objects
            .select_for_update()
            .filter(
                account_number=account_number,
                user=user,
            )
            .first()
        )

        if account is None:
            raise ValueError(
                "Account not found."
            )

        if account.balance < amount:
            raise ValueError(
                "Insufficient funds."
            )

        account.balance -= amount

        account.save(
            update_fields=["balance"]
        )

        return account