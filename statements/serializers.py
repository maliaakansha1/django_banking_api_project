from rest_framework import serializers

from accounts.models import Account
from .models import StatementRequest
from django.utils import timezone

class StatementRequestSerializer(
    serializers.ModelSerializer
):

    account_number = serializers.CharField(
        write_only=True,
    )

    class Meta:

        model = StatementRequest

        fields = (
            "account_number",
            "from_date",
            "to_date",
        )
    def validate(self, attrs):

          if attrs["from_date"] > attrs["to_date"]:

            raise serializers.ValidationError(
                "From date cannot be greater than To date."
            )
          if attrs["to_date"] > timezone.now().date():
            raise serializers.ValidationError(
               "Future dates are not allowed."
        )


          return attrs
        
    def validate_account_number(
        self,
        value,
    ):

        user = self.context["request"].user

        account = (
            Account.objects
            .filter(
                account_number=value,
                user=user,
            )
            .first()
        )

        if account is None:

            raise serializers.ValidationError(
                "Account not found."
            )

        return account
    def create(self, validated_data):

        account = validated_data.pop(
            "account_number"
        )

        return StatementRequest.objects.create(
            user=self.context["request"].user,
            account=account,
            **validated_data,
        )
        
        
        
        
class StatementStatusSerializer(
    serializers.ModelSerializer
):

    download_url = serializers.SerializerMethodField()

    class Meta:

        model = StatementRequest

        fields = (
            "id",
            "status",
            "created_at",
            "completed_at",
            "download_url",
        )

    def get_download_url(
        self,
        obj,
    ):

        request = self.context.get(
            "request"
        )

        if obj.statement_file:

            return request.build_absolute_uri(
                obj.statement_file.url
            )

        return None