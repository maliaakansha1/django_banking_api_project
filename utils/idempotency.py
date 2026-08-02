from banking_api.settings import redis_client

IDEMPOTENCY_TIMEOUT = 600   # 10 minutes


def acquire_idempotency_key(key):

    cache_key = f"idempotency:{key}"

    return redis_client.set(
        cache_key,
        "processed",
        ex=IDEMPOTENCY_TIMEOUT,
        nx=True,
    )