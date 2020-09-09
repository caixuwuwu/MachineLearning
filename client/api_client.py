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

from client.HBaseClient import HbaseClient
from client.SimpleHttpClient import SimpleHttpClient
from configs.ConfManage import ConfManage
from tools.cache import Cache
from tools.logger import Logger
from pandas import read_json
import time
cache = Cache().client
logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))


class ApiClient(object):
    """
    根据参数决定调用hbase或者url获取数据
    """
    def __init__(self):
        self.conf = ConfManage()
        if self.conf.getString("API_TYPE") == "URL":
            self.client = self.dataapi_client()
        else:
            self.client = self.hbase_client()

    @staticmethod
    def client():
        if ConfManage.getString("API_TYPE") == "URL":
            client = ApiClient.dataapi_client()
        else:
            client = ApiClient.hbase_client()
        return client

    @staticmethod
    def hbase_client():
        return HbaseClient()

    @staticmethod
    def dataapi_client():
        return SimpleHttpClient()

    def set_client(self, client):
        self.client = client
        return self.client

    def get_client(self):
        return self.client

    def get_data(self, **kwargs):
        data = self.client.get_data(**kwargs)
        return data

    def get_cache_data(self, key, **kwargs):
        """
         获取缓存数据
        Args:
            key: cache key
            **kwargs:

        Returns: pd.DataFrame

        """
        update_cache_time = self.conf.getInt("CACHE_UPDATE")
        retry = 3
        while True:
            data = cache.get(key)
            if data is None:
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
                        logger.error("Cache msg: Get cache data fail while retry three times, key: {}".format(key))
                        raise Exception("1302:Get cache data fail while retry three times, key: {}".format(key))
            else:
                extime = cache.ttl(key)
                if extime <= update_cache_time:
                    if cache.set_mutex(key, 2):
                        try:
                            data = self.get_data(**kwargs).to_json()
                            cache.set(key, data)
                            cache.delete(key + "_mutex")
                        except Exception:
                            logger.error("Cache msg:get {} failed, return old date".format(key))
                            cache.delete(key + "_mutex")
                            return data
                        break
                else:
                    break
        return read_json(data)

    def collect_batch_data(self, start_time, end_time, table, topic, columns=None, record_path=None, meta=None):
        st = start_time
        et = end_time
        data_df = pd.DataFrame()
        hours_interval = int(24 / ENV_DATA_API_TIMERANGE) if 24 % ENV_DATA_API_TIMERANGE == 0 else 12
        while st < et:
            snt = st.shift(hours=hours_interval)
            data_df = data_df.append(
                self.get_data(table=table, topic=topic, start_time=st.shift(seconds=1), end_time=snt, columns=columns,
                                record_path=record_path, meta=meta))
            st = snt
        return data_df

    def fetch_data(self, start_time, end_time, table, topic, columns=None, record_path=None, meta=None,
                   save_file_prefix="order_accept_"):
        df = load_pickle(save_file_prefix + topic)
        if df is None:
            df = self.collect_batch_data(start_time=start_time, end_time=end_time, table=table, topic=topic,
                                         columns=columns, record_path=record_path, meta=meta)
            save_pickle(df, save_file_prefix + topic)
        else:
            if len(df) == 0:
                df = self.collect_batch_data(start_time=start_time, end_time=end_time, table=table, topic=topic,
                                        columns=columns, record_path=record_path, meta=meta)
                save_pickle(df, save_file_prefix + topic)
        logger.info('Fetch %s (Count): %d' % (topic, len(df)))
        return df


if __name__ == "__main__":
    print(ApiClient().get_client())
