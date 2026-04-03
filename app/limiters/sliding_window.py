import time
from app.redis_client import r

def sliding_window_log(client_id: str, max_requests: int, window_seconds: int) -> dict:
    now = time.time()
    window_start = now - window_seconds
    key = f"sw:{client_id}"

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_seconds)
    results = pipe.execute()

    count = results[2]
    allowed = count <= max_requests
    return {
        "allowed": allowed,
        "count": count,
        "remaining": max(0, max_requests - count),
        "reset_in": window_seconds
    }