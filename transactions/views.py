from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DepositSerializer, TransactionHistorySerializer
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
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)

class DepositView(APIView):

    permission_classes = [IsAuthenticated]
    @extend_schema(
        tags=["Transaction Management"],
        summary="Deposit Money",
        description=(
        "Deposits money into the authenticated user's account.\n\n"
        "After a successful deposit:\n"
        "- Account balance is updated.\n"
        "- Transaction history is created.\n"
        "- An email notification is sent asynchronously using Celery."
    ),
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
    tags=["Transactions"],
    summary="Withdraw Money",
    description=(
        "Withdraws money from the authenticated user's account. "
        "After a successful withdrawal, an email notification is "
        "sent asynchronously using Celery."
    ),
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
    tags=["Transaction Management"],
    summary="Transfer Money",
    description=(
        "Transfers funds between two bank accounts.\n\n"
        "After a successful transfer:\n"
        "- Sender balance is updated.\n"
        "- Receiver balance is updated.\n"
        "- Transaction records are created.\n"
        "- Email notifications are sent asynchronously using Celery."
    ),
    request=TransferSerializer,
    responses={
        200: OpenApiResponse(
            description="Transfer completed successfully."
        ),
        400: OpenApiResponse(
            description="Transfer failed."
        ),
    },
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
        
from .serializers import TransactionHistorySerializer
from .services import list_transactions

@extend_schema(
    tags=["Transaction Management"],
    summary="View Transaction History",
    description=(
        "Returns the transaction history of the authenticated user's bank accounts.\n\n"
    "If no query parameters are supplied, all transactions are returned.\n\n"
    "All query parameters are optional and can be combined to filter the results."
    ),
    parameters=[
        OpenApiParameter(
            name="account_number",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter transactions by account number.",
            examples=[
                OpenApiExample(
                    "Savings Account",
                    value="100000001",
                )
            ],
        ),
        OpenApiParameter(
            name="transaction_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Filter by transaction type. "
                "Allowed values: DEPOSIT, WITHDRAW, "
                "TRANSFER_IN, TRANSFER_OUT."
            ),
            examples=[
                OpenApiExample(
                    "Deposit",
                    value="DEPOSIT",
                )
            ],
        ),
        OpenApiParameter(
            name="from_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Start date (YYYY-MM-DD).",
            examples=[
                OpenApiExample(
                    "From Date",
                    value="2026-07-01",
                )
            ],
        ),
        OpenApiParameter(
            name="to_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="End date (YYYY-MM-DD).",
            examples=[
                OpenApiExample(
                    "To Date",
                    value="2026-07-31",
                )
            ],
        ),
        OpenApiParameter(
            name="reference_number",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Search using transaction reference number.",
            examples=[
                OpenApiExample(
                    "Reference Number",
                    value="TXN-AB12CD34EF56",
                )
            ],
        ),
    ],
    responses={
         200: TransactionHistorySerializer(many=True),
            
        
    },
)

class TransactionHistoryView(APIView):

    def get(self, request):

        transactions = list_transactions(
            user=request.user,
            account_number=request.query_params.get(
                "account_number"
            ),
            transaction_type=request.query_params.get(
                "transaction_type"
            ),
            from_date=request.query_params.get(
                "from_date"
            ),
            to_date=request.query_params.get(
                "to_date"
            ),
            reference_number=request.query_params.get(
                "reference_number"
            ),
        )

        serializer = TransactionHistorySerializer(
            transactions,
            many=True,
        )

        return Response(serializer.data)