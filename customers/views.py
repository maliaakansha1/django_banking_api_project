from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .manage_token import generate_token, remove_token, store_token
from .serializers import LoginSerializer, RegisterSerializer


@extend_schema(
    request=RegisterSerializer,
    responses={201: RegisterSerializer},
)
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
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
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"message": "Invalid Credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = generate_token(user)
        store_token(user, token)

        return Response({"token": token}, status=status.HTTP_200_OK)

@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "email": {"type": "string"}
            }
        }
    }
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {"username": request.user.username, "email": request.user.email},
            status=status.HTTP_200_OK,
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

    def post(self, request):
        remove_token(request.user)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
