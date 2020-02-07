import redis


class RedisEntity:
    REDIS_PORT = 6379
    REDIS_HOST = "localhost"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.redis = redis.StrictRedis(host=self.REDIS_HOST, port=self.REDIS_PORT, db=0)
