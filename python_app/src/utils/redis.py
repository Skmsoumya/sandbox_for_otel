import redis
import os

# Cache duration
TTL_SECONDS = 100

# insecure for development app, should be injected from secrets manager
redis_host = os.getenv('REDIS_HOST')
redis_password = os.getenv('REDIS_PASSWORD')
redis_port = os.getenv('REDIS_PASSWORD')

redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True, password=redis_password)