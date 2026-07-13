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

