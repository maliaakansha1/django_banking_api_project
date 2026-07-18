from rest_framework import serializers

from beneficiaries.models import Beneficiary


class BeneficiarySerializer(serializers.Serializer):

    account_number = serializers.CharField(
        max_length=20,
    )
    
class BeneficiaryListSerializer(serializers.ModelSerializer):

    account_number = serializers.CharField(
        source="beneficiary_account.account_number"
    )

    account_type = serializers.CharField(
        source="beneficiary_account.account_type"
    )

    account_holder = serializers.CharField(
        source="beneficiary_account.user.username"
    )

    class Meta:
        model = Beneficiary

        fields = [
            "id",
            "account_number",
            "account_type",
            "account_holder",
        ]