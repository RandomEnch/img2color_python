import os
import redis

CACHE_ENABLED = True
CACHE_EXPIRE = int(os.getenv('CACHE_EXPIRE', 86400))
ALLOW_REFERER = os.getenv('ALLOW_REFERER', '').split(',')

if CACHE_ENABLED:
    REDIS_HOST = os.getenv('REDIS_HOST', 'evolving-marmoset-52528.upstash.io')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '****')

    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=6379,
        password=REDIS_PASSWORD,
        ssl=True
    )
