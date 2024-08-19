import os

DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']

CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() in ['true', '1', 't']
CACHE_EXPIRE = int(os.getenv('CACHE_EXPIRE', 3600 * 24))

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

ALLOW_REFERER = os.getenv('ALLOW_REFERER', 'http://localhost:4000').split(',')
