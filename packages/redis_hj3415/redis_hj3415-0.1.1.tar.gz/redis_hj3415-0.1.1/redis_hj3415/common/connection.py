import os, redis
from redis.asyncio import Redis as AsyncRedis

# 싱글톤 클라이언트 정의
REDIS_ADDR = os.getenv('REDIS_ADDR')
REDIS_PASS = os.getenv('REDIS_PASS')

client: redis.Redis | None = None
async_client: AsyncRedis | None = None

def get_redis_client(port: int = 6379) -> redis.Redis:
    global client
    if client is None:
        client = redis.Redis(host=REDIS_ADDR,
                             port=port,
                             password=REDIS_PASS,
                             decode_responses=True)
    return client



def get_redis_client_async(port: int = 6379) -> AsyncRedis:
    global async_client
    if async_client is None:
        async_client = AsyncRedis(host=REDIS_ADDR,
                            port=port,
                            password=REDIS_PASS,
                            decode_responses=True)
    return async_client