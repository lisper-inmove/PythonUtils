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
            for server in self.servers:
                try:
                    flag = server.set(key, value, nx=True, px=ttl)
                    successCount += 1 if flag else 0
                except Exception as ex:
                    logger.info(f"lock exception: {ex}")
            if successCount >= self.quorum:
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
