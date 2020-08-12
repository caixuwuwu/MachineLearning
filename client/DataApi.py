#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 DataApi.py
# VERSION: 	 1.0
# CREATED: 	 2018-02-13 15:19
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#   Contains HTTP-Client specific to Data-API
# HISTORY:
# *************************************************************
import sys
import json
from pandas.io.json import json_normalize

from client.BaseClient import BaseClient
from configs.ConfManage import ConfManage
from helpers.caster import remove_none
from client.SimpleHttpClient import SimpleHttpClient
from helpers.timer import dataApiTimeFmt

if sys.version_info[:2] in [(2, 6), (2, 7)]:  # Python 2.7
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:  # Python 3.6
    # pylint: disable=E0401, E0611, E1101
    import importlib
    importlib.reload(sys)


class DataApi(BaseClient):
    """HTTP-Connection with Data-API"""

    def __init__(self):
        self.client = SimpleHttpClient(ConfManage.getString("DATA_API_ENDPOINT"), use_ssl=False)

    def get_data(self, table, topic, start_time=None, end_time=None, columns=None, record_path=None, meta=None,
                 timeout=10., **kwargs):
        """
        调用API,可加table_name值查询,无法用于多条件查询
        :param table
        :param topic: string
        :param time_start: int eg:20190711000000 查询开始时间
        :param time_end: 查询终止时间
        :param kwargs: table_name值
        :return: pd.DataFrame
        """
        if self.client is None: return
        route = ConfManage.getString("DATA_API_PREFIX") + '/' + table + '/' + topic
        for k, v in kwargs.items():
            if isinstance(v, list):
                object_id = ','.join([str(i) for i in v])
                route += '/' + object_id
            elif isinstance(v, int):
                object_id = str(v)
                route += '/' + object_id
        if start_time is not None and end_time is not None:
            params = remove_none(dict(time_start=dataApiTimeFmt(start_time), time_end=dataApiTimeFmt(end_time)))
        else:
            params = None
        response = self.client.get(route=route, queries=params, timeout=timeout)
        response = json.loads(response) if isinstance(response, (str, bytes)) else response
        if response['error'] == 0:
            j2df = json_normalize(response['data'], record_path=record_path, meta=meta)
            if columns:
                try:
                    j2df = j2df.loc[:, columns]
                except KeyError:
                    return j2df
            return j2df
        else:
            raise DataApiException(response['err_msg'])


class DataApiException(Exception): pass


class ConnectionNotEstablished(DataApiException): pass

