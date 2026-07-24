from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from accounts.models import Account
from beneficiaries.models import Beneficiary
from beneficiaries.services import (
    activate_beneficiary_if_ready,
)
from uuid import uuid4

from .models import Transaction
from notifications.tasks import (
    send_email_task,
)


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
            update_fields=["balance"],
        )

        create_transaction(
            account=account,
            transaction_type=Transaction.DEPOSIT,
            amount=amount,
            balance_after_transaction=account.balance,
            remarks="Cash Deposit",
        )

        send_email_task.delay(
            subject="Deposit Successful",
            receiver_email="aakanshamali01@gmail.com",
            body=(
                f"Dear {account.user.username},\n\n"
                f"₹{amount} has been credited successfully to "
                f"Account {account.account_number}.\n\n"
                f"Available Balance: ₹{account.balance}\n\n"
                "Thank you for banking with us."
            ),
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
        send_email_task.delay(
              subject="Withdrawal Successful",
               receiver_email="aakanshamali01@gmail.com",
               body=(
               f"Dear {account.user.username},\n\n"
               f"₹{amount} has been debited from "
               f"Account {account.account_number}.\n\n"
               f"Available Balance: ₹{account.balance}\n\n"
               "Thank you for banking with us."
    ),
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
        send_email_task.delay(
            subject="Money Transfer Successful",
            receiver_email="aakanshamali01@gmail.com",
            body=(
                f"Dear {sender_account.user.username},\n\n"
                f"₹{amount} has been transferred successfully "
                f"from Account {sender_account.account_number}.\n\n"
                f"Remaining Balance: ₹{sender_account.balance}\n\n"
                "Thank you for banking with us."
    ),
)

        create_transaction(
               account=receiver_account,
               transaction_type=Transaction.TRANSFER_IN,
               amount=amount,
               balance_after_transaction=receiver_account.balance,
               remarks=f"Transfer from {sender_account.account_number}",
)
        send_email_task.delay(
               subject="Money Received",
               receiver_email="aakanshamali01@gmail.com",
                body=(
                  f"Dear {receiver_account.user.username},\n\n"
                   f"₹{amount} has been credited successfully "
                   f"to Account {receiver_account.account_number}.\n\n"
                   f"Available Balance: ₹{receiver_account.balance}\n\n"
                    "Thank you for banking with us."
    ),
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
    
from .models import Transaction


def list_transactions(
    *,
    user,
    account_number=None,
    transaction_type=None,
    from_date=None,
    to_date=None,
    reference_number=None,
):

    transactions = (
        Transaction.objects
        .filter(
            account__user=user,
        )
        .select_related("account")
        .order_by("-created_at")
    )

    if account_number:
        transactions = transactions.filter(
            account__account_number=account_number
        )

    if transaction_type:
        transactions = transactions.filter(
            transaction_type=transaction_type
        )

    if reference_number:
        transactions = transactions.filter(
            reference_number=reference_number
        )

    if from_date:
        transactions = transactions.filter(
            created_at__date__gte=from_date
        )

    if to_date:
        transactions = transactions.filter(
            created_at__date__lte=to_date
        )

    return transactions



def credit_monthly_interest():
    """
    Credit monthly interest to all eligible savings accounts.
    """

    accounts = Account.objects.filter(
        account_type=Account.SAVINGS,
    )

    for account in accounts:
        current_date = timezone.now()

        already_credited = (
           Transaction.objects.filter(
               account=account,
               transaction_type=Transaction.INTEREST,
               created_at__year=current_date.year,
               created_at__month=current_date.month,
           ).exists()
)

        if already_credited:
          print(
             f"Interest already credited for {account.account_number}"
    )
          continue

        annual_interest_rate = Decimal("4.0")

        monthly_interest = (
            account.balance
            * annual_interest_rate
            / Decimal("100")
            / Decimal("12")
        )

        monthly_interest = monthly_interest.quantize(
            Decimal("0.01")
        )
        account.balance += monthly_interest

        account.save(
              update_fields=["balance"],
        )
        create_transaction(
               account=account,
               transaction_type=Transaction.INTEREST,
               amount=monthly_interest,
               balance_after_transaction=account.balance,
               remarks="Monthly Interest Credit",
)

        print(
            f"Account: {account.account_number}"
        )

        print(
            f"Current Balance: {account.balance}"
        )

        print(
            f"Interest: {monthly_interest}"
        )