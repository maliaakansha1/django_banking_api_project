from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .manage_token import generate_token, remove_token, store_token
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
)
from .serializers import KYCSerializer
from .services import submit_kyc

from django.shortcuts import get_object_or_404
from .models import KYC
from .services import verify_kyc, reject_kyc
from utils.responses import success_response, error_response

@extend_schema(
    auth=[],
    request=RegisterSerializer,
    responses={201: RegisterSerializer},
)
class RegisterView(APIView):
    serializer_class = RegisterSerializer
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return success_response(
                data={"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )

        return error_response(error=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    auth=[],
    request=LoginSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "token": {"type": "string"}
            }
        }
    }
)

class LoginView(APIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return error_response(
                error={"message": "Invalid Credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = generate_token(user)
        store_token(user, token)

        return success_response(
            data={"token": token},
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UpdateProfileSerializer
    @extend_schema(
        responses=ProfileSerializer
    )

    def get(self, request):

        serializer = ProfileSerializer(request.user)

        return success_response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )
    @extend_schema(
        request=UpdateProfileSerializer,
        responses=ProfileSerializer
    )
    def patch(self, request):

        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return success_response(
                data=ProfileSerializer(request.user).data,
                status=status.HTTP_200_OK,
            )

        return error_response(
            error=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    }
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        remove_token(request.user)
        return success_response(
            data={"message": "Logout successful"},
            status=status.HTTP_200_OK
        )



@extend_schema(
    tags=["KYC"],
)

class SubmitKYCView(APIView):

    permission_classes = [IsAuthenticated]
    @extend_schema(
    summary="Submit KYC",
    description=(
        "Allows an authenticated customer "
        "to submit KYC details. "
        "The submitted KYC will remain "
        "in PENDING status until "
        "verified by an administrator."
    ),
    request=KYCSerializer,
    responses={
        201: KYCSerializer,
        400: None,
    },
)
    def post(self, request):

        serializer = KYCSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            kyc = submit_kyc(
                user=request.user,
                aadhaar_number=serializer.validated_data[
                    "aadhaar_number"
                ],
                pan_number=serializer.validated_data[
                    "pan_number"
                ],
                address=serializer.validated_data[
                    "address"
                ],
            )

        except ValueError as e:

            return error_response(
                error={
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(
            data={
                "message": "KYC submitted successfully.",
                "kyc": KYCSerializer(kyc).data,
            },
            status=status.HTTP_201_CREATED,
        )
        
        
@extend_schema(
    tags=["KYC"],
)
class VerifyKYCView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]
    @extend_schema(
    summary="Verify Customer KYC",
    description=(
        "Allows an administrator "
        "to verify a customer's KYC."
    ),
    responses={
        200: KYCSerializer,
        403: None,
        404: None,
    },
)
    def patch(
        self,
        request,
        kyc_id,
    ):

        if not request.user.is_staff:

            return error_response(
                error="Only admin can verify KYC.",
                status=status.HTTP_403_FORBIDDEN,
            )

        kyc = get_object_or_404(
            KYC,
            id=kyc_id,
        )

        verify_kyc(
            kyc=kyc,
            admin_user=request.user,
        )

        return success_response(
            data={
                "message":
                "KYC verified successfully.",
                "kyc":
                KYCSerializer(kyc).data,
            }
        )
        
        
@extend_schema(
    tags=["KYC"],
)
class RejectKYCView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]
    @extend_schema(
    summary="Reject Customer KYC",
    description=(
        "Allows an administrator "
        "to reject a customer's KYC."
    ),
    responses={
        200: KYCSerializer,
        403: None,
        404: None,
    },
)
    def patch(
        self,
        request,
        kyc_id,
    ):

        if not request.user.is_staff:

            return error_response(
                error="Only admin can reject KYC.",
                status=status.HTTP_403_FORBIDDEN,
            )

        kyc = get_object_or_404(
            KYC,
            id=kyc_id,
        )

        reject_kyc(
            kyc=kyc,
        )

        return success_response(
            data={
                "message":
                "KYC rejected successfully.",
                "kyc":
                KYCSerializer(kyc).data,
            }
        )