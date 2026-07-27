from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from accounts.models import Account

from .serializers import CardSerializer, IssueCardSerializer
from .services import issue_card



class IssueCardView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Cards"],
        summary="Issue Debit Card",
        description=(
            "Issues a debit card for the authenticated user's account."
        ),
        request=IssueCardSerializer,
        responses={
            201: CardSerializer,
        },
    )
    def post(self, request):

        serializer = IssueCardSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            account = Account.objects.get(
                account_number=serializer.validated_data[
                    "account_number"
                ],
                user=request.user,
            )

        except Account.DoesNotExist:

            return Response(
                {
                    "message": "Account not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            
            card = issue_card(
            account=account,
        )
        except ValueError as e:

            return Response(
                {
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            CardSerializer(card).data,
            status=status.HTTP_201_CREATED,
        )