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
    TransferSerializer,
)

from .services import (
    deposit_money,
    withdraw_money,
    transfer_money,
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
        
        
class TransferView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TransferSerializer,
    )
    def post(self, request):

        serializer = TransferSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            result = transfer_money(
                user=request.user,
                from_account_number=serializer.validated_data[
                    "from_account_number"
                ],
                to_account_number=serializer.validated_data[
                    "to_account_number"
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

        sender = result["sender"]
        receiver = result["receiver"]

        return Response(
            {
                "message": "Transfer successful.",
                "from_account": sender.account_number,
                "to_account": receiver.account_number,
                "transferred_amount": serializer.validated_data["amount"],
                "remaining_balance": sender.balance,
            },
            status=status.HTTP_200_OK,
        )