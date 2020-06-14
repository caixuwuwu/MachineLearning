#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME:  __init__.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
import os
import sys

if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    # pylint: disable=E0401, E1101
    import importlib

    importlib.reload(sys)

ENV_APP_MODE = os.environ.get('APP_MODE', 'local')
ENV_ZONE = os.environ.get('ZONE', 'hk')


try:
    from dotenv import load_dotenv
    from os.path import join, dirname

    dotenv_path = join(dirname(__file__), '../{app_mode}-{zone}.env'.format(app_mode=ENV_APP_MODE, zone=ENV_ZONE))
    load_dotenv(dotenv_path)
except ImportError:
    pass
