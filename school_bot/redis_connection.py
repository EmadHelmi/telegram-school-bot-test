import redis

from settings import REDIS

redis_conn = redis.Redis(
    host=REDIS["HOST"],
    port=REDIS["PORT"],
    password=REDIS["PASSWORD"],
    decode_responses=True,
)
