import redis
from app.config import settings

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)