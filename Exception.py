# /usr/bin/python
# -*- encoding:utf-8 -*-
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME:  Exception.py
# VERSION: 	 1.0
# CREATED: 	 2020-01-25 12:23
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#   project exception
# HISTORY:
# *************************************************************


class APIError(Exception):
    def __init__(self):
        super(APIError, self).__init__("")
