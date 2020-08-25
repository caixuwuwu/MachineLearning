#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 OsrmApi.py
# VERSION: 	 1.0
# CREATED: 	 2018-08-24 12:58
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Contains HTTP-Client specific to OSRM-Frontend"""
import sys
import pandas as pd

from configs.ConfManage import ConfManage
from client.SimpleHttpClient import SimpleHttpClient
from tools.logger import Logger
from tools.s2 import S2

logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))

if sys.version_info[:2] in [(2, 6), (2, 7)]:  # Python 2.6, 2.7
    reload(sys)
elif sys.version_info[:2] in [(3, 6), (3, 7)]:  # Python 3.6, 3.7
    # pylint: disable=E0401, E0611, E1101
    import importlib
    importlib.reload(sys)


class OsrmApi(object):

    def __init__(self):
        self.client = SimpleHttpClient("http://" + ConfManage.getString("OSRM_API_ENDPOINT"))
        self.S2_cache = S2()

    # When a method is not found, shortcuts it to a SimpleHttpClient instance's Method
    def __getattr__(self, name):
        return getattr(self.client, name)

    def get_distance_df(self, traffic, starting_coordinates, destination_coordinates, timeout=None, zone=""):
        result = self.S2_cache.get_s2_distance(traffic, starting_coordinates, destination_coordinates,
                                               self.get_distance, zone=zone, timeout=timeout)
        return OsrmApi.to_df(result)

    def get_distance(self, traffic, starting_coordinates, destination_coordinates, timeout=None, zone="", **kwargs):
        if self.client is None:
            raise ConnectionNotEstablished('OsrmApiClient is not yet initiated.')
        if not isinstance(starting_coordinates, tuple) or len(starting_coordinates) != 2:
            raise ValueError('Given param: `starting_coordinates` is of wrong type or not paired.')
        if not isinstance(destination_coordinates, tuple) or len(destination_coordinates) != 2:
            raise ValueError('Given param: `destination_coordinates` is of wrong type or not paired.')
        route = zone + ConfManage.getString("OSRM_API_%s_ROUTE" % traffic.upper())
        route += '%.6f,%.6f;%.6f,%.6f' % ( \
            starting_coordinates[0], starting_coordinates[1],
            destination_coordinates[0], destination_coordinates[1]
        )
        if len(kwargs) > 0:
            params = kwargs
        else:
            params = None
        try:
            result = self.client.get(route, params, timeout=timeout)
        except Exception as err:
            logger.error('OsrmapiError link={}, Msg:{}'.format(ConfManage.getString("OSRM_API_ENDPOINT") + route, err))
            result = {"routes": [{"distance": -1}]}
        return result['routes'][0]["distance"]

    @staticmethod
    def to_df(distance):
        return pd.DataFrame({"distance": [float(distance)]})


class OsrmApiException(Exception): pass


class ConnectionNotEstablished(OsrmApiException): pass
