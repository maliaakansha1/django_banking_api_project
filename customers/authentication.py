from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .manage_token import authenticate_token

# This class tells DRF

# This request belongs to this user.

class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "", 1)
        user = authenticate_token(token)
        if user is None:
            raise AuthenticationFailed("Invalid token")

        return user, token
