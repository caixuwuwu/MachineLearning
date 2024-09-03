# /usr/bin/python
# -*- encoding:utf-8 -*-
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME:  BaseClient.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#       abstract class for client
# HISTORY:
# *************************************************************

from abc import ABCMeta, abstractmethod
from pandas import DataFrame


class BaseClient(ABCMeta):
    @abstractmethod
    def conn(cls): raise NotImplementedError

    @abstractmethod
    def get_data(cls, *args, **kwargs):
        """
        Returns: pandas DataFrame
        """
        raise NotImplementedError

    def to_df(cls, data):
        return DataFrame({"distance": [float(data)]})

    @abstractmethod
    def close(cls):
        raise NotImplementedError

    def __del__(self):
        """
        基类私有方法，所有实例删除自动处理API链接IO的关闭
        """
        self.close()
        del self.conn
