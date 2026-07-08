import jwt
import redis
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model


class InMemoryTokenStore:
    def __init__(self):
        self._store = {}

    def setex(self, key, ttl, value):
        self._store[key] = value
        return True

    def get(self, key):
        return self._store.get(key)

    def delete(self, key):
        self._store.pop(key, None)
        return True

    def exists(self, key):
        return key in self._store


try:
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    redis_client.ping()
except Exception:
    redis_client = InMemoryTokenStore()


def generate_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=10),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


# def store_token(user, token):
#     key = f"user:{user.id}"
#     redis_client.setex(key, settings.JWT_TOKEN_TTL_SECONDS, token)
#     return key
def store_token(user, token):
    key = f"user:{user.id}"
    print("Saving token in Redis:", key)
    redis_client.setex(key, settings.JWT_TOKEN_TTL_SECONDS, token)
    return key

def remove_token(user):
    redis_client.delete(f"user:{user.id}")


def decode_token(token):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


def get_user_from_token(token):
    payload = decode_token(token)
    User = get_user_model()
    return User.objects.get(id=payload["user_id"])


def authenticate_token(token):
    try:
        payload = decode_token(token)
    except Exception:
        return None

    key = f"user:{payload['user_id']}"
    stored_token = redis_client.get(key)
    if stored_token != token:
        return None

    User = get_user_model()
    try:
        return User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return None
