import time
from app.redis_client import r

def fixed_window(client_id: str, max_requests: int, window_seconds: int) -> dict:
    window_key = int(time.time() // window_seconds)
    key = f"fw:{client_id}:{window_key}"

    count = r.incr(key)
    if count == 1:
        r.expire(key, window_seconds)

    allowed = count <= max_requests
    return {
        "allowed": allowed,
        "count": count,
        "remaining": max(0, max_requests - count),
        "reset_in": window_seconds - (int(time.time()) % window_seconds)
    }