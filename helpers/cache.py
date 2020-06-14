#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 cache.py
# VERSION: 	 1.0
# CREATED: 	 2018-08-27 17:06
# AUTHOR: 	 caixuwu <caixuwu@km-it.cn>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
import time
import threading
import pandas
from configs.ConfManage import ConfManage
import redis
from helpers.logger import Logger
from redis.exceptions import ConnectionError, TimeoutError
from random import randrange

logger = Logger.get_instance(ConfManage.getString("LOG_REQ_NAME"))


class KVCache:
    """缓存系统抽象类。所有缓存类继承此类必须实现指定功能，否则报错"""

    def set(self, key, data, age):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def set_mutex(self, key):
        raise NotImplementedError


class RedisCache(KVCache):
    def __init__(self):
        self.pool = redis.ConnectionPool(host=ConfManage.getString("REDIS_HOST"),
                                         port=ConfManage.getInt("REDIS_PORT"),
                                         db=ConfManage.getInt("REDIS_DB"),
                                         password=ConfManage.getString("REDIS_PASSWORD"),
                                         max_connections=ConfManage.getInt("REDIS_MAX_CONNECTIONS"),
                                         decode_responses=True,
                                         socket_keepalive=True
                                         )

        self.conn = redis.StrictRedis(connection_pool=self.pool, socket_connect_timeout=5)
        self.logger = Logger.get_instance(ConfManage.getString("LOG_REQ_NAME"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == TimeoutError:
            self.logger.error("RedisConnTimeout msg=connect timeout")
            return True
        elif exc_type == ConnectionError:
            self.logger.error("RedisConnection msg=Too many connections")
            return True
        self.close()

    def set_mutex(self, key, ex=4):
        with self.conn as conn:
            boolenresult = conn.setnx("{}_mutex".format(key), "1")
            conn.expire("{}_mutex".format(key), ex)
        return boolenresult

    def set(self, key, data, age=ConfManage.getInt("CACHE_AGE")):
        ex = age + randrange(start=0, stop=10, step=1) if age > 0 else None
        with self.conn as conn:
            result = conn.set(key, data, ex)
        return result

    def get(self, key):
        with self.conn as conn:
            data = conn.get(key)
        return data

    def delete(self, key):
        with self.conn as conn:
            result = conn.delete(key)
        return result

    def clear(self):
        keys = self.conn.keys()
        return self.conn.delete(*keys)

    def ttl(self, key):
        return self.conn.ttl(key)

    def keys(self):
        return self.conn.keys()

    def close(self):
        return self.conn.close()


class LocalCache(KVCache):
    def __init__(self):
        """初始化"""
        self.mem = {}
        self.time = {}
        self.lock = threading.Lock()

    def setnx(self, key, extime):
        key_mutex = "{}_mutex".format(key)
        if key_mutex in self.mem:
            return False
        else:
            self.mem["{}_mutex".format(key)] = "1"
            self.time["{}_mutex".format(key)] = time.time() + extime
            return True

    def set_mutex(self, key, ex=4):
        with self.lock:
            boolenresult = self.setnx(key, ex)
        return boolenresult

    def set(self, key, data, age=ConfManage.getInt("CACHE_AGE")):
        """保存键为key的值，时间位age"""
        with self.lock:
            self.mem[key] = data
            if age == -1:
                self.time[key] = -1
            else:
                self.time[key] = time.time() + age + randrange(start=0, stop=10, step=1)
            return True

    def get(self, key):
        """获取键key对应的值"""
        if key in self.mem.keys():
            if self.time[key] == -1 or self.time[key] > time.time():
                return self.mem[key]
            else:
                self.delete(key)
                return None
        else:
            return None

    def delete(self, key):
        """删除键为key的条目"""
        with self.lock:
            if key in self.mem:
                del self.mem[key]
                del self.time[key]
                return True
            else:
                return False

    def clear(self):
        """清空所有缓存"""
        with self.lock:
            self.mem.clear()
            self.time.clear()
            return True

    def ttl(self, key):
        if key in self.time:
            return int(self.time[key] - time.time())
        else:
            return None

    def keys(self):
        return self.mem.keys()


class Cache:
    """缓存系统工厂类，根据环境变量CACHE_TYPE指定使用哪种缓存方式"""
    cache_type = ConfManage.getString("CACHE_TYPE")
    _instance = {}

    CACHE_TYPE_LOCAL = 'Local'

    CACHE_TYPE_REDIS = 'Redis'

    def __init__(self):
        if Cache.cache_type == "redis":
            self.client = RedisCache()
        elif Cache.cache_type == "local":
            self.client = LocalCache()
        else:
            raise Exception('1303:CACHE_TYPE set error, must be "local" or "redis".')

    @staticmethod
    def get_instance(cache_type=None):
        cache_type = cache_type if cache_type is not None else Cache.CACHE_TYPE_LOCAL
        """Get Singleton instance of Cache"""
        if cache_type not in Cache._instance:
            if cache_type.capitalize() == Cache.CACHE_TYPE_LOCAL:
                instance = LocalCache()
            elif cache_type.capitalize() == Cache.CACHE_TYPE_REDIS:
                instance = RedisCache()
            else:
                raise Exception('1303:cache type error.')
            Cache._instance[cache_type] = instance
        return Cache._instance[cache_type]

    def toCache(self, cacheKey, age=ConfManage.getInt("CACHE_AGE")):
        def getData(func):
            def save(*args, **kwargs):
                retry = 4
                while True:
                    data = self.client.get(cacheKey)
                    if data is None:
                        if self.client.set_mutex(cacheKey, 2):
                            try:
                                data = func(*args, **kwargs).to_json()
                                self.client.set(cacheKey, data, age)
                                self.client.delete(cacheKey + "_mutex")
                            except Exception:
                                self.client.delete(cacheKey + "_mutex")
                                raise
                            break
                        else:
                            time.sleep(0.5)
                            retry -= 1
                            if retry == 0:
                                logger.error("Cache msg: Get cache data fail while retry 4 times")
                                raise Exception("1302:Get cache data fail while retry 4 times")
                    else:
                        extime = self.client.ttl(cacheKey)
                        if extime <= 8:
                            if self.client.set_mutex(cacheKey, 2):
                                try:
                                    data = func(*args, **kwargs).to_json()
                                    self.client.set(cacheKey, data, age)
                                    self.client.delete(cacheKey + "_mutex")
                                except Exception:
                                    logger.error("Cache msg:get {} failed, return old date".format(kwargs["topic"]))
                                    self.client.delete(cacheKey + "_mutex")
                                    return data
                                break
                        else:
                            break
                return pandas.read_json(data)

            return save

        return getData


if __name__ == '__main__':
    from helpers.parallel import multi_thread

    client = RedisCache()


    # with client as conn:
    # conn.set("area","{'A':'cai'}")
    def set(key):
        with client.conn as conn:
            data = conn.set(key, '111')
            return data


    def set2(key):
        with client.conn as conn:
            data = conn.get(key)
            return data


    function = [set2, set2, set2]
    agrs = [{"key": "area"}, {"key": "task"}, {"key": "area"}]
    th = multi_thread(function, kwds=agrs)
    data = th[0].get()
    data1 = th[1].get()
    data2 = th[2].get()
    print(data)
    print(data1)
    print(data2)
