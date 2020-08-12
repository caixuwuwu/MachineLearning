#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 SimpleHttpClient.py
# VERSION: 	 1.0
# CREATED: 	 2018-02-13 15:19
# AUTHOR: 	 Aekasitt Guruvanich <aekazitt@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module defining SimpleHttpClient class"""
import json
import sys
import os
import requests
from requests.adapters import HTTPAdapter

from client.BaseClient import BaseClient
from helpers.timer import timepiece
from configs.ConfManage import ConfManage
from helpers.logger import Logger

if sys.version_info[:2] in [(2, 6), (2, 7)]:  # Python 2.6, 2.7
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:  # Python 3.6, 3.7
    # pylint: disable=E0401, E0611, E1101
    import importlib

    importlib.reload(sys)
logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))


class SimpleHttpClient(BaseClient):
    """Simple Client defined used to get standardised
    response of HTTP requests"""

    def __init__(self, end_point, use_ssl=False):
        self.end_point = end_point
        self.conn = requests.Session()
        if use_ssl:
            self.conn.mount("https://", HTTPAdapter(pool_connections=os.cpu_count() - 1,
                                                    pool_maxsize=ConfManage.getInt("HTTP_MAX_CONNECTIONS"),
                                                    max_retries=3))
        else:
            self.conn.mount("http://", HTTPAdapter(pool_connections=os.cpu_count() - 1,
                                                   pool_maxsize=ConfManage.getInt("HTTP_MAX_CONNECTIONS"),
                                                   max_retries=3))

    def close(self):
        self.conn.close()

    def __del__(self):
        self.close()

    def get_data(self, method="get", route='/', queries=None, timeout=None, **kwargs):
        url = self.end_point + route
        res = None
        for i in range(3):
            try:
                res = getattr(self, method)(url, queries=queries, timeout=timeout, **kwargs)
                break
            except (requests.Timeout, requests.exceptions.ConnectTimeout) as err:
                logger.error('HTTPTimeout link= {} msg:{}'.format(url, err))
                raise TimeoutError("1402:HTTP Timeout, link:{}".format(url))
            except requests.ConnectionError as err:
                logger.warning("HTTPConnect link={}  msg:{},please check network and try again".format(url, err))
                if i >= 3:
                    raise ConnectionError("1401:HTTPConnect Error, link:{}".format(url))
            except requests.HTTPError as err:
                logger.warning("HTTPError link={} msg: {}".format(url, err))
                if i >= 3:
                    raise err
            except requests.TooManyRedirects as err:
                logger.warning("HTTPTooManyRedirects link={}, msg:{}".format(url, err))
                if i >= 3:
                    raise err
            except Exception as err:
                if i >= 3:
                    raise err
        if res.status_code == 200:
            if res.headers['content-type'] == 'application/json':
                jd = res.json()
            else:
                jd = json.loads(res.text)
            res.close()
            return jd  # dict
        else:
            logger.error("HttpStatus link= {}, response status is not 200".format(url))
            raise Exception("1405:response status code is not 200, link:{}".format(url))

    @timepiece(msg=True)
    def get(self, url, queries=None, timeout=None):
        """
            Create a GET Request with given route and queries, return response
        :param url:
        :param queries:
        :param timeout: float or tuple
        :return:
        """
        res = self.conn.get(url, params=queries, headers={'Accept-encoding': 'gzip'}, timeout=timeout)
        return res

    def post(self, url, queries=None, timeout=None, data=None, json=None):
        """
            Create a POST Request with given route and queries, return response
        """
        res = self.conn.post(url, data=data, json=json, params=queries, headers={'Accept-encoding': 'gzip'},
                             timeout=timeout)
        return res
