# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 api_client.py
# VERSION: 	 1.0
# CREATED: 	 2018-02-13 15:19
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
#*************************************************************

from apis.hbase_client import HbaseClient
from apis.data_api_client import DataApiClient
from configs.ConfManage import ConfManage
from helpers.cache import Cache
from helpers.timer import timepiece
from helpers.logger import Logger
from pandas import read_json
import time
cache = Cache().client
logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))

class ApiClient(object):
    """
    根据参数决定调用hbase或者http获取数据
    """
    def __init__(self):
        if ConfManage.getString("API_TYPE") == "dataApi":
            self.client = self.dataapi_client()
        else:
            self.client = self.hbase_client()

    @staticmethod
    def client():
        if ConfManage.getString("API_TYPE") == "dataApi":
            client = ApiClient.dataapi_client()
        else:
            client = ApiClient.hbase_client()
        return client

    @staticmethod
    def hbase_client():
        return HbaseClient()

    @staticmethod
    def dataapi_client():
        return DataApiClient()

    def get_client(self):
        return self.client

    def get_data(self, **kwargs):
        data = self.client.get_data(**kwargs)
        return data

    def get_cache_data(self, **kwargs):
        retry = 4
        key = kwargs["topic"]
        while True:
            data = cache.get(key)
            if data == None:
                if cache.set_mutex(key, 2):
                    try:
                        data = self.get_data(**kwargs).to_json()
                        cache.set(key, data)
                        cache.delete(key + "_mutex")
                    except Exception:
                        cache.delete(key + "_mutex")
                        raise
                    break
                else:
                    time.sleep(1)
                    retry -= 1
                    if retry == 0:
                        logger.error("Cache msg: Get cache data fail while retry 4 times")
                        raise Exception("1302:Get cache data fail while retry 4 times")
            else:
                extime = cache.ttl(key)
                if extime <= 8:
                    if cache.set_mutex(key, 2):
                        try:
                            data = self.get_data(**kwargs).to_json()
                            cache.set(key, data)
                            cache.delete(key + "_mutex")
                        except Exception:
                            logger.error("Cache msg:get {} failed, return old date".format(kwargs["topic"]))
                            cache.delete(key + "_mutex")
                            return data
                        break
                else:
                    break
        return read_json(data)

    def get_cache_df_data(self, **kwargs):
        retry = 4
        key = kwargs["topic"] + "_df"
        while True:
            data = cache.get(key)
            if data == None:
                if cache.set_mutex(key, 2):
                    try:
                        data = self.client.get_df_data(**kwargs).to_json()
                        cache.set(key, data)
                        cache.delete(key + "_mutex")
                    except Exception:
                        cache.delete(key + "_mutex")
                        raise
                    break
                else:
                    time.sleep(1)
                    retry -= 1
                    if retry == 0:
                        logger.error("Cache msg: Get cache data fail while retry 4 times")
                        raise Exception("1302:Get cache data fail while retry 4 times")
            else:
                extime = cache.ttl(key)
                if extime <= 8:
                    if cache.set_mutex(key, 2):
                        try:
                            data = self.client.get_df_data(**kwargs).to_json()
                            cache.set(key, data)
                            cache.delete(key + "_mutex")
                        except Exception:
                            logger.error("Cache msg:get {} failed, return old date".format(kwargs["topic"]))
                            cache.delete(key + "_mutex")
                            return data
                        break
                else:
                    break
        return read_json(data)

    def set_client(self,client):
        self.client = client
        return self.client


if __name__ == "__main__":
    print(ApiClient().get_client())
