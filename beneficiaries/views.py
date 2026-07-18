from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BeneficiarySerializer,BeneficiaryListSerializer
from drf_spectacular.utils import extend_schema
from .services import add_beneficiary,list_beneficiaries,delete_beneficiary


class BeneficiaryListCreateView(APIView):
    @extend_schema(
        request=BeneficiarySerializer,
        responses={201: BeneficiarySerializer},
    )
    def post(self, request):

        serializer = BeneficiarySerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            beneficiary = add_beneficiary(
                user=request.user,
                account_number=serializer.validated_data[
                    "account_number"
                ],
            )

        except ValueError as e:
            return Response(
                {
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Beneficiary added successfully.",
                "beneficiary_account": (
                    beneficiary.beneficiary_account.account_number
                ),
            },
            status=status.HTTP_201_CREATED,
        )
    def get(self, request):

        beneficiaries = list_beneficiaries(
              user=request.user,
    )

        serializer = BeneficiaryListSerializer(
                 beneficiaries,
                 many=True,
    )

        return Response(
              serializer.data,
              status=status.HTTP_200_OK,
    )
        
class BeneficiaryDeleteView(APIView):

    def delete(self, request, beneficiary_id):

        delete_beneficiary(
            user=request.user,
            beneficiary_id=beneficiary_id,
        )

        return Response(
            {
                "message": "Beneficiary deleted successfully."
            },
            status=status.HTTP_200_OK,
        )