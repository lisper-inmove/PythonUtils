import time
import json
import asyncio

from redis import asyncio as aioredis

from .sys_env import SysEnv
from .logger import Logger
from .idate import IDate

logger = Logger()


class Redislock:

    def __init__(self, key, value=None, ttl=None, retryCount=None, retryDelay=None):
        """
        ttl: 秒
        retryDelay: 秒
        retryCount: 尝试次数

        >>> async with Redislock("my-test-lock", ttl=30, retryCount=10, retryDelay=0.2) as lock:
        >>>     if not lock:
        >>>         raise Exception("acquire lock failed")
        >>>     dosomething()
        """
        if ttl is None:
            ttl = 5
        self.key = key
        self.value = value
        self.ttl = ttl * 1000
        if retryCount is None:
            retryCount = 5
        self.retryCount = retryCount
        if retryDelay is None:
            retryDelay = 0.2
        self.retryDelay = retryDelay

    async def __aenter__(self):
        configs = SysEnv.get("REDIS_LOCK_CONFIG", "")
        password = SysEnv.get("REDIS_LOCK_PASSWORD")
        configs = configs.split(":")
        redisServer = []
        for config in configs:
            config = config.split(",")
            redisServer.append({
                "host": config[0],
                "port": int(config[1]),
                "password": password,
                "db": 0
            })
        self.rlk = await MyRedlock(
            retryCount=self.retryCount,
            retryDelay=self.retryDelay
        ).create(redisServer)
        self.lock = await self.rlk.lock(self.key, self.value, self.ttl)
        return self.lock

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.lock:
            await self.rlk.unlock(self.lock)


class Lock:

    def __init__(self, key, data, ttl, startTime=None):
        self.key = key
        self.data = data
        self.ttl = ttl
        if startTime is None:
            startTime = IDate.now_milliseconds()
        self.startTime = startTime

    @property
    def value(self):
        value = {
            "key": self.key,
            "data": self.data,
            "ttl": self.ttl,
            "startTime": self.startTime
        }
        return json.dumps(value)

    @classmethod
    def from_json(cls, data):
        json_data = json.loads(data)
        return cls(
            json_data.get("key"),
            json_data.get("data"),
            json_data.get("ttl"),
            json_data.get("startTime")
        )


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

    def __init__(self, retryCount=None, retryDelay=None):
        self.retryCount = retryCount
        self.retryDelay = retryDelay

    async def create(self, connectionList):
        await self.__init_servers(connectionList)
        return self

    async def __init_servers(self, connectionList):
        self.servers = []
        for connection in connectionList:
            try:
                server = await aioredis.StrictRedis(**connection)
                server._release_script = server.register_script(self.unlock_script)
                server._renewal_script = server.register_script(self.renewal_script)
                self.servers.append(server)
            except Exception as ex:
                logger.info(f"connect {connection} error {ex}")

        self.quorum = (len(connectionList) // 2) + 1
        if len(self.servers) < self.quorum:
            raise Exception("Failed to connect to the majority of redis servers")

    async def lock(self, key, value, ttl):
        retry = 0
        lock = Lock(key, value, ttl)
        while retry < self.retryCount:
            successCount = 0
            startTime = time.monotonic()
            for server in self.servers:
                try:
                    flag = await server.set(lock.key, lock.value, nx=True, px=ttl)
                    successCount += 1 if flag else 0
                except asyncio.CancelledError as ex:
                    logger.info(f"operation cancelled: {ex}")
                except Exception as ex:
                    logger.info(f"lock exception: {ex}")
            endTime = time.monotonic()
            elapsedMilliseconds = (endTime - startTime) * (10 ** 3)
            drift = (ttl * self.CLOCK_DRIFT_FACTOR) + 2
            validity = ttl - (elapsedMilliseconds + drift)
            if validity > 0 and successCount >= self.quorum:
                return lock
            else:
                await self.__unlock(lock)
                retry += 1
                await asyncio.sleep(self.retryDelay)
        return None

    async def unlock(self, lock):
        await self.__unlock(lock)

    async def __unlock(self, lock):
        for server in self.servers:
            try:
                await server._release_script(keys=[lock.key], args=[lock.value])
            except Exception as ex:
                logger.info(f"__unlock exception: {ex}")

    async def query_lock(self, key):
        for server in self.servers:
            value = await server.get(key)
            if value:
                return Lock.from_json(value)

    async def renewal(self, lock):
        if IDate.now_milliseconds() - lock.startTime < lock.ttl / 2:
            return
        for server in self.servers:
            await server._renewal_script(keys=[lock.key], args=[lock.value, lock.ttl])
