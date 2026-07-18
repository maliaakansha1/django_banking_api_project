from django.db import transaction

from accounts.models import Account
from .models import Beneficiary


def add_beneficiary(
    *,
    user,
    account_number,
):

    with transaction.atomic():

        account = (
            Account.objects
            .filter(
                account_number=account_number,
            )
            .first()
        )

        if account is None:
            raise ValueError(
                "Account not found."
            )

        if account.user == user:
            raise ValueError(
                "You cannot add your own account as beneficiary."
            )

        if Beneficiary.objects.filter(
            user=user,
            beneficiary_account=account,
        ).exists():

            raise ValueError(
                "Beneficiary already added."
            )

        beneficiary = Beneficiary.objects.create(
            user=user,
            beneficiary_account=account,
        )

        return beneficiary


def list_beneficiaries(
    *,
    user,
):

    return (
        Beneficiary.objects
        .filter(
            user=user,
        )
        .select_related(
            "beneficiary_account",
            "beneficiary_account__user",
        )
        .order_by("id")
    )

from django.shortcuts import get_object_or_404


def delete_beneficiary(
    *,
    user,
    beneficiary_id,
):

    beneficiary = get_object_or_404(
        Beneficiary,
        id=beneficiary_id,
        user=user,
    )

    beneficiary.delete()