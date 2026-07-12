from decimal import Decimal

from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.ModelSerializer):

    initial_deposit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        write_only=True,
        help_text="Minimum ₹500 for Savings and ₹1000 for Current account.",
    )

    class Meta:
        model = Account

        fields = [
            "account_number",
            "account_type",
            "balance",
            "initial_deposit",
            "created_at",
        ]

        read_only_fields = [
            "account_number",
            "balance",
            "created_at",
        ]
    def validate(self, attrs):

        account_type = attrs["account_type"]
        deposit = attrs["initial_deposit"]

        if (
            account_type == Account.SAVINGS
            and deposit < Decimal("500")
    ):
            raise serializers.ValidationError(
              {
                  "initial_deposit":
                  "Minimum balance for Savings account is ₹500."
              }
        )

        if (
            account_type == Account.CURRENT
            and deposit < Decimal("1000")
       ):
            raise serializers.ValidationError(
               {
                   "initial_deposit":
                    "Minimum balance for Current account is ₹1000."
            }
        )

        return attrs
    def create(self, validated_data):

       deposit = validated_data.pop("initial_deposit")

       user = self.context["request"].user

       account = Account.objects.create(
           user=user,
           balance=deposit,
           **validated_data,
    )

       return account