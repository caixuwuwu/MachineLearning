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

import abc


class BaseClient(abc.ABC):

    @abc.abstractmethod
    def get_data(self, *args, **kwargs):
        """
        Returns: pandas DataFrame

        """
        pass

