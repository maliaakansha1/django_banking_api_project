from django.db import transaction

from accounts.models import Account
from .models import Beneficiary
from datetime import timedelta

from django.utils import timezone

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
                status=Beneficiary.PENDING,
                cooling_ends_at=(
                timezone.now() + timedelta(minutes=2)
    ),
)

        return beneficiary


def list_beneficiaries(
    *,
    user,
):

    beneficiaries = (
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

    for beneficiary in beneficiaries:
        activate_beneficiary_if_ready(
            beneficiary
        )

    return beneficiaries

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
    
    
from django.utils import timezone


def activate_beneficiary_if_ready(
    beneficiary,
):

    if (
        beneficiary.status == Beneficiary.PENDING
        and timezone.now() >= beneficiary.cooling_ends_at
    ):

        beneficiary.status = Beneficiary.ACTIVE

        beneficiary.save(
            update_fields=["status"]
        )

    return beneficiary