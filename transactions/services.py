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
    
    
def transfer_money(
    *,
    user,
    from_account_number,
    to_account_number,
    amount,
):

    if amount <= Decimal("0"):
        raise ValueError(
            "Amount must be greater than zero."
        )

    with transaction.atomic():

        sender_account = (
            Account.objects
            .select_for_update()
            .filter(
                account_number=from_account_number,
                user=user,
            )
            .first()
        )

        if sender_account is None:
            raise ValueError(
                "Sender account not found."
            )

        receiver_account = (
            Account.objects
            .select_for_update()
            .filter(
                account_number=to_account_number,
            )
            .first()
        )

        if receiver_account is None:
            raise ValueError(
                "Receiver account not found."
            )

        if from_account_number == to_account_number:
            raise ValueError(
                "Source and destination accounts cannot be the same."
            )

        if sender_account.balance < amount:
            raise ValueError(
                "Insufficient funds."
            )

        sender_account.balance -= amount
        receiver_account.balance += amount

        sender_account.save(
            update_fields=["balance"]
        )

        receiver_account.save(
            update_fields=["balance"]
        )

        return {
            "sender": sender_account,
            "receiver": receiver_account,
        }