from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DepositSerializer
from .services import deposit_money
from drf_spectacular.utils import extend_schema
from .serializers import (
    DepositSerializer,
    WithdrawalSerializer,
)

from .services import (
    deposit_money,
    withdraw_money,
)

class DepositView(APIView):

    permission_classes = [IsAuthenticated]
    @extend_schema(
    request=DepositSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "account_number": {"type": "string"},
                "account_type": {"type": "string"},
                "current_balance": {"type": "string"},
            },
        }
    },
)
    def post(self, request):

        serializer = DepositSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            account = deposit_money(
                user=request.user,
                account_number=serializer.validated_data["account_number"],
                amount=serializer.validated_data["amount"],
            )

        except ValueError as e:
            return Response(
                {
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Deposit successful.",
                "account_number": account.account_number,
                "account_type": account.account_type,
                "current_balance": account.balance,
            },
            status=status.HTTP_200_OK,
        )



class WithdrawalView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=WithdrawalSerializer,
    )
    def post(self, request):

        serializer = WithdrawalSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            account = withdraw_money(
                user=request.user,
                account_number=serializer.validated_data[
                    "account_number"
                ],
                amount=serializer.validated_data[
                    "amount"
                ],
            )

        except ValueError as e:

            return Response(
                {
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Withdrawal successful.",
                "account_number": account.account_number,
                "account_type": account.account_type,
                "current_balance": account.balance,
            },
            status=status.HTTP_200_OK,
        )