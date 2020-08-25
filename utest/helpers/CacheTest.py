#!/usr/bin/env python
# coding=utf-8
'''
@Description: 测试cache内存功能
@Author: Cai
@LastEditors: Cai
@Date: 2020-03-23 12:25:44
@LastEditTime:
'''
import unittest
import time
import pandas as pd
from tools.cache import Cache, RedisCache

cache = Cache()


class CacheTest(unittest.TestCase):


    @cache.toCache("cachetest", 1)
    def cachetest(self):
        return pd.DataFrame({"A":[1,2,3], "B":[4,5,6]})

    def test_cache(self):
        cache.get_instance("Redis")
        self.assertEqual(type(cache.get_instance("Redis")), RedisCache)

        str_data = self.cachetest()
        self.assertIsInstance(str_data, pd.DataFrame)
        data = cache.client.get("cachetest")
        self.assertEqual(data, '''{"A":{"0":1,"1":2,"2":3},"B":{"0":4,"1":5,"2":6}}''')
        time.sleep(10)
        datacache = Cache().client.get("cachetest")
        self.assertEqual(datacache, None)

if __name__ == "__main__":
    unittest.main()