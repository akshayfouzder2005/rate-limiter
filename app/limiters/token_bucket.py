import time
from app.redis_client import r

SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1]) or capacity
local last_refill = tonumber(bucket[2]) or now

local elapsed = now - last_refill
local new_tokens = math.min(capacity, tokens + (elapsed * refill_rate))

if new_tokens >= 1 then
    redis.call('HMSET', key, 'tokens', new_tokens - 1, 'last_refill', now)
    redis.call('EXPIRE', key, 3600)
    return {1, math.floor(new_tokens - 1)}
else
    redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
    return {0, 0}
end
"""

_lua = r.register_script(SCRIPT)

def token_bucket(client_id: str, capacity: int, refill_rate: float) -> dict:
    result = _lua(
        keys=[f"tb:{client_id}"],
        args=[capacity, refill_rate, time.time()]
    )
    allowed = result[0] == 1
    remaining = int(result[1])
    return {
        "allowed": allowed,
        "remaining": remaining,
        "capacity": capacity
    }