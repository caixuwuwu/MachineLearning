#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 client.py
# VERSION: 	 1.0
# CREATED: 	 2020-01-09 12:00
# AUTHOR:    caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module containing ETA Client-Launch Script to ThriftService"""
import argparse
import glob
import sys
from configs.ConfManage import ConfManage
from helpers.logger import Logger
from helpers.thrift_client import ThriftClient

if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    # pylint: disable=E0401, E0611, E1101
    import importlib

    importlib.reload(sys)

requirements_logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))
try:
    sys.path.append('gen-py')
    sys.path.insert(0, glob.glob('../../lib/py/build/lib*'[0]))
    from SFOrderRouter import SFOrderRouter
except ImportError:
    requirements_logger.error('Cannot find thrift classes.')
    requirements_logger.error('Have you run `thrift --gen py SFOrderRouter.thrift`?')
    raise


class TSPClient:

    def __init__(self):
        self.host = ConfManage.getString("TSP_HOST")
        self.port = ConfManage.getInt("TSP_PORT")
        self.client = ThriftClient(SFOrderRouter, host=self.host, port=self.port, timeout=60000)

    def get_tsp(self, coordinate, distance_type="straight"):
        if not isinstance(coordinate, list):
            raise ValueError("coordinate must be a list")
        else:
            try:
                result = self.client.invoke('tsp_route', coordinate, distance_type)
                return result
            except Exception as exc:
                requirements_logger.error(f'Error {exc}')
                raise


if __name__ == '__main__':
    result = TSPClient().get_tsp(
        ["114.267056,22.320218", "114.257139,22.322381", "114.267056,22.320218", "114.2581589,22.3246785"])
    print(result)
