import time
import json
from contextlib import contextmanager

import redis

from .sys_env import SysEnv
from .logger import Logger
from .idate import IDate

logger = Logger()


@contextmanager
def redislock(key, value=None, ttl=None, retryCount=None, retryDelay=None):
    """
    ttl: 秒
    retryDelay: 秒
    retryCount: 尝试次数
    """
    if ttl is None:
        ttl = 5
    configs = SysEnv.get("REDIS_LOCK_CONFIG", "")
    configs = configs.split(":")
    redisServer = []
    for config in configs:
        config = config.split(",")
        password = None
        if len(config) == 3:
            password = config[2]
        redisServer.append({
            "host": config[0],
            "port": int(config[1]),
            "password": password,
            "db": 0
        })
    ttl = ttl * 1000
    rlk = MyRedlock(
        redisServer,
        retryCount=retryCount,
        retryDelay=retryDelay
    )
    if not isinstance(value, dict):
        value = {"data": value}
    value.update({"start": IDate.now_milliseconds()})
    value = json.dumps(value)
    lock = rlk.lock(key, value, ttl)
    yield lock
    if lock:
        rlk.unlock(lock)


class Lock:

    def __init__(self, key, value, ttl):
        self.key = key
        self.value = value
        self.ttl = ttl
        self.startTime = IDate.now_milliseconds()


class MyRedlock:

    unlock_script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end"""

    renewal_script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("ttl", ARGV[2])
    else
        return 0
    end
    """

    """
    `CLOCK_DRIFT_FACTOR`在分布式锁算法中用于考虑可能的时钟漂移。在分布式系统中，各个节点的时钟可能不完全同步。这种时钟漂移可能会影响锁的正确性和可靠性。
    在这个RedLock实现中，`CLOCK_DRIFT_FACTOR`被设置为0.01，意味着算法允许1%的时钟漂移。这个值是一个折衷，用于在可靠性和性能之间平衡。
    - 如果你设置一个较小的值，例如0.001，那么算法将对时钟漂移更为敏感。这可能会增加锁获取失败的概率，特别是在时钟同步不精确的环境中。
    - 如果你设置一个较大的值，那么算法将更宽容于时钟漂移。这可能会增加锁的可用性，但也可能降低锁的可靠性，因为时钟漂移可能会导致锁被意外释放或延长。
    1%的时钟漂移因子是一个合理的默认值，适用于许多常见的使用场景。然而，在具体的应用中，你可能需要根据你的系统的特点和需求来调整这个值。
    如果你的系统的时钟同步非常精确，你可能可以使用一个较小的值。如果时钟同步不精确，或者你更关心锁的可用性而不是严格的一致性，你可能需要使用一个较大的值。
    """
    CLOCK_DRIFT_FACTOR = 0.01

    def __init__(self, connectionList, retryCount=None, retryDelay=None):
        self.__init_servers(connectionList)
        self.retryCount = retryCount
        self.retryDelay = retryDelay

    def __init_servers(self, connectionList):
        self.servers = []
        for connection in connectionList:
            try:
                server = redis.StrictRedis(**connection)
                server._release_script = server.register_script(self.unlock_script)
                server._renewal_script = server.register_script(self.renewal_script)
                self.servers.append(server)
            except Exception as ex:
                logger.info(f"connect {connection} error {ex}")

        self.quorum = (len(connectionList) // 2) + 1
        if len(self.servers) < self.quorum:
            raise Exception("Failed to connect to the majority of redis servers")

    def lock(self, key, value, ttl):
        retry = 0
        lock = Lock(key, value, ttl)
        while retry < self.retryCount:
            successCount = 0
            startTime = time.monotonic()
            for server in self.servers:
                try:
                    flag = server.set(key, value, nx=True, px=ttl)
                    successCount += 1 if flag else 0
                except Exception as ex:
                    logger.info(f"lock exception: {ex}")
            endTime = time.monotonic()
            elapsedMilliseconds = (endTime - startTime) * 10**3
            drift = (ttl * self.CLOCK_DRIFT_FACTOR) + 2
            validity = ttl - (elapsedMilliseconds + drift)
            if validity > 0 and successCount >= self.quorum:
                return lock
            else:
                self.__unlock(lock)
                retry += 1
                time.sleep(self.retryDelay)
        return None

    def unlock(self, lock):
        self.__unlock(lock)

    def __unlock(self, lock):
        for server in self.servers:
            try:
                server._release_script(keys=[lock.key], args=[lock.value])
            except Exception as ex:
                logger.info(f"__unlock exception: {ex}")

    def query_lock(self, lock):
        for server in self.servers:
            return server.get(lock.key)

    def renewal(self, lock):
        if IDate.now_milliseconds() - lock.startTime < lock.ttl / 2:
            return
        for server in self.servers:
            server._renewal_script(keys=[lock.key], args=[lock.value, lock.ttl])
