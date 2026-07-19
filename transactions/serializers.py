from rest_framework import serializers

class DepositSerializer(serializers.Serializer):

    account_number = serializers.CharField(
        max_length=20,
        help_text="Enter the account number."
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Enter the deposit amount."
    )
class WithdrawalSerializer(serializers.Serializer):

    account_number = serializers.CharField(
        max_length=20,
        help_text="Enter the account number.",
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Enter the withdrawal amount.",
    )

class TransferSerializer(serializers.Serializer):

    from_account_number = serializers.CharField(
        max_length=20,
        help_text="Enter the sender account number.",
    )

    to_account_number = serializers.CharField(
        max_length=20,
        help_text="Enter the receiver account number.",
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Enter the transfer amount.",
    )

from .models import Transaction


class TransactionHistorySerializer(serializers.ModelSerializer):

    account_number = serializers.CharField(
        source="account.account_number",
        read_only=True,
    )

    class Meta:
        model = Transaction

        fields = (
            "reference_number",
            "account_number",
            "transaction_type",
            "amount",
            "balance_after_transaction",
            "remarks",
            "created_at",
        )