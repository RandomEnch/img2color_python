import os

CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() in ['true', '1', 't']
CACHE_EXPIRE = int(os.getenv('CACHE_EXPIRE', 86400))
REDIS_STR = os.getenv('REDIS_HOST', 'redis://default:********@****.upstash.io:6379')
ALLOW_REFERER = os.getenv('ALLOW_REFERER', '').split(',')
