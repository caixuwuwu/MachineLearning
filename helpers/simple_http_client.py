#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 simple_http_client.py
# VERSION: 	 1.0
# CREATED: 	 2018-02-13 15:19
# AUTHOR: 	 Aekasitt Guruvanich <aekazitt@gmail.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
"""Module defining SimpleHttpClient class"""
import json
import sys
from socket import timeout
from helpers.timer import timepiece
import requests
from requests.adapters import HTTPAdapter
from configs.ConfManage import ConfManage
from helpers.logger import Logger
if sys.version_info[:2] in [(2, 6), (2, 7)]:      # Python 2.6, 2.7
    import httplib
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:    # Python 3.6, 3.7
    # pylint: disable=E0401, E0611, E1101
    import importlib
    import http.client as httplib
    importlib.reload(sys)
logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))

class SimpleHttpClient(object):
    """Simple Client defined used to get standardised
    response of HTTP requests (GET & POST only)"""

    def __init__(self, end_point, use_ssl=False):
        self.end_point = end_point
        self.use_ssl = use_ssl
        self.initiate_conn()

    def initiate_conn(self):
        if self.use_ssl:
            self.conn = requests.Session()
            self.conn.mount("https://", HTTPAdapter(pool_connections=4,
                                                    pool_maxsize=ConfManage.getInt("HTTP_MAX_CONNECTIONS"),
                                                    max_retries=3))
        else:
            self.conn = requests.Session()
            self.conn.mount("http://", HTTPAdapter(pool_connections=4,
                                                   pool_maxsize=ConfManage.getInt("HTTP_MAX_CONNECTIONS"),
                                                   max_retries=3))

    def close(self):
        self.conn.close()

    def __del__(self):
        self.close()

    @timepiece(msg=1)
    def get(self, route='/', queries=None, timeout=None):
        """
        Create a GET Request with given route and queries, return response
        :param route:
        :param queries:
        :param timeout: float or tuple
        :return:
        """
        url = self.end_point + route
        res = None
        try:
            res = self.conn.get(url, params=queries, headers={'Accept-encoding':'gzip'},timeout=timeout)
        except (requests.Timeout, requests.ConnectTimeout) as err:
            logger.error('HTTPTimeout link= {} msg:{}'.format(url, err))
            raise TimeoutError("1402:HTTP Timeout, link:{}".format(url))
        except requests.ConnectionError as err:
            logger.warning("HTTPConnect link={}  msg:{},please check network and try again".format(url, err))
            raise ConnectionError("1401:HTTPConnect Error, link:{}".format(url))
        except requests.HTTPError as err:
            logger.warning("HTTPError link={} msg: {}".format(url, err))
        except requests.TooManyRedirects as err:
            logger.warning("HTTPTooManyRedirects link={}, msg:{}".format(url, err))
        if res.status_code == 200:
            if res.headers['content-type'] == 'application/json':
                jData = res.json()
                res.close()
                return jData #dict
            return json.loads(res.text)
        else:
            logger.error("HttpStatus link= {}, response status is not 200".format(url))
            raise Exception("1405:response status code is not 200, link:{}".format(url))

    def post(self, route='/', queries=None, payload=None):
        """Create a POST Request with given route and queries, return response
        :param route:
        :param queries:
        :param timeout: float or tuple
        :return:
        """
        url = self.end_point + route
        res = None
        try:
            res = self.conn.post(url, params=queries, headers={'Accept-encoding':'gzip'},timeout=timeout)
        except (requests.Timeout, requests.ConnectTimeout):
            logger.warning('The link with {route} data-api timeout'.format(route=route))
        except requests.ConnectionError as err:
            logger.warning("Connect api Error {},please check network and try again".format(err))
        except requests.HTTPError as err:
            logger.warning("msg: {}".format(err))
        except requests.TooManyRedirects as err:
            logger.warning("msg:{}".format(err))
        if res.status_code == 200:
            if res.headers['content-type'] == 'application/json':
                return res.json()
            return json.loads(res.text)
        else:
            raise Exception("response status code is not 200")


class SimpleHttpException(httplib.HTTPException): pass
class Unauthorized(SimpleHttpException): pass
class BadRequest(SimpleHttpException): pass
class InternalServerError(SimpleHttpException): pass
