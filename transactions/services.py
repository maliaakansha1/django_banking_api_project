from decimal import Decimal

from django.db import transaction

from accounts.models import Account
from beneficiaries.models import Beneficiary
from beneficiaries.services import (
    activate_beneficiary_if_ready,
)
from uuid import uuid4

from .models import Transaction

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
        create_transaction(
             account=account,
             transaction_type=Transaction.DEPOSIT,
             amount=amount,
             balance_after_transaction=account.balance,
             remarks="Cash Deposit",
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
        create_transaction(
              account=account,
              transaction_type=Transaction.WITHDRAW,
              amount=amount,
              balance_after_transaction=account.balance,
              remarks="Cash Withdrawal",
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
    if from_account_number == to_account_number:
            raise ValueError(
                "Source and destination accounts cannot be the same."
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
        
        beneficiary = (
                Beneficiary.objects
                .filter(
                      user=user,
                      beneficiary_account=receiver_account,
    )
                .first()
)

        if beneficiary is None:
           raise ValueError(
             "Receiver account is not added as a beneficiary."
    )

        beneficiary = activate_beneficiary_if_ready(
              beneficiary
)

        if beneficiary.status != Beneficiary.ACTIVE:
             raise ValueError(
                 "Beneficiary is in cooling period. Please try again later."
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
        create_transaction(
               account=sender_account,
               transaction_type=Transaction.TRANSFER_OUT,
               amount=amount,
               balance_after_transaction=sender_account.balance,
               remarks=f"Transfer to {receiver_account.account_number}",
)

        create_transaction(
               account=receiver_account,
               transaction_type=Transaction.TRANSFER_IN,
               amount=amount,
               balance_after_transaction=receiver_account.balance,
               remarks=f"Transfer from {sender_account.account_number}",
)

        return {
            "sender": sender_account,
            "receiver": receiver_account,
        }
        
# for uc9
def create_transaction(
    *,
    account,
    transaction_type,
    amount,
    balance_after_transaction,
    remarks="",
):

    reference_number = (
        f"TXN-{uuid4().hex[:12].upper()}"
    )

    return Transaction.objects.create(
        reference_number=reference_number,
        account=account,
        transaction_type=transaction_type,
        amount=amount,
        balance_after_transaction=balance_after_transaction,
        remarks=remarks,
    )