import redis
from .log import log


class ConnectRedis(object):
    def __init__(self, host='localhost', port=6379, db=0, password=None, decode_responses=True):
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses
            )
            # 测试连接是否成功
            self.redis.ping()
            log.debug(f"Redis connect success to {host}:{port}/{db}!")
        except Exception as msg:
            self.redis = None
            log.error(f"Redis connect error to {host}:{port}/{db}: {msg}")

    def get(self, key):
        """获取key的值"""
        if not self.redis:
            log.error("Redis connection is not initialized")
            return None
        try:
            value = self.redis.get(key)
            log.debug(f"Redis get {key}: {value}")
            return value
        except Exception as msg:
            log.error(f"Redis get error: {msg}")
            return None

    def set(self, key, value, ex=None):
        """设置key的值"""
        if not self.redis:
            log.error("Redis connection is not initialized")
            return False
        try:
            result = self.redis.set(key, value, ex=ex)
            log.debug(f"Redis set {key}: {value}, expire: {ex}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis set error: {msg}")
            return False

    def delete(self, key):
        """删除key"""
        if not self.redis:
            log.error("Redis connection is not initialized")
            return False
        try:
            result = self.redis.delete(key)
            log.debug(f"Redis delete {key}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis delete error: {msg}")
            return False

    def exists(self, key):
        if not self.redis:
            log.error("Redis connection is not initialized")
            return False
        try:
            result = self.redis.exists(key)
            log.debug(f"Redis exists {key}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis exists error: {msg}")
            return False

    def keys(self, pattern='*'):
        if not self.redis:
            log.error("Redis connection is not initialized")
            return []
        try:
            result = self.redis.keys(pattern)
            log.debug(f"Redis keys {pattern}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis keys error: {msg}")
            return []

    def flushall(self):
        if not self.redis:
            log.error("Redis connection is not initialized")
            return False
        try:
            result = self.redis.flushall()
            log.debug(f"Redis flushall, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis flushall error: {msg}")
            return False

    def ttl(self, key):
        if not self.redis:
            log.error("Redis connection is not initialized")
            return -2
        try:
            result = self.redis.ttl(key)
            log.debug(f"Redis ttl {key}, result: {result}")
            return result
        except Exception as msg:
            log.error(f"Redis ttl error: {msg}")
            return -2
