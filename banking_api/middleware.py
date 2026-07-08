import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse

from customers.manage_token import redis_client


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(("/api/login", "/api/register", "/api/schema", "/api/docs", "/api/refresh")):
            return self.get_response(request)

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({"message": "Missing Token"}, status=401)

        token = auth_header.replace("Bearer ", "", 1)
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token Expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid Token"}, status=401)

        key = f"user:{payload['user_id']}"
        stored_token = redis_client.get(key)
        if stored_token != token:
            return JsonResponse({"message": "Token not found in Redis"}, status=401)

        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            request.user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            request.user = AnonymousUser()
            return JsonResponse({"message": "User not found"}, status=401)

        return self.get_response(request)
