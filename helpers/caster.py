#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 caster.py
# VERSION: 	 1.0
# CREATED: 	 2018-08-27 17:06
# AUTHOR: 	 <caixuwu@outlook.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Turn data into different shapes and sizes"""
import sys

if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    # pylint: disable=E0401, E0611, E1101
    import importlib

    importlib.reload(sys)


def chunks(lst, chunk_size):
    """Returns a list of smaller chunks of 
    original given list `lst` with defined `chunk_size`"""
    chunk_size = max(1, chunk_size)
    if sys.version_info[:2] in [(2, 6), (2, 7)]:
        return (lst[index:index + chunk_size] for index in xrange(0, len(lst), chunk_size))
    elif sys.version_info[:2] in [(3, 6), (3, 7)]:
        return (lst[index:index + chunk_size] for index in range(0, len(lst), chunk_size))


def camel(string):
    """Turn snake_cases or sentences into camelCase string"""
    return ''.join(_ for _ in string.title() if not _.isspace() and not _ == '_')


def remove_none(kwargs):
    """Returns a copy of dictionary keys with nil-value"""
    if not kwargs or type(kwargs) != dict:
        raise IOError('remove_none: wrong type param ({})'.format(kwargs))
    elif sys.version_info[:2] in [(2, 6), (2, 7)]:
        return dict((k, v) for k, v in kwargs.iteritems() if v is not None)
    elif sys.version_info[:2] in [(3, 6), (3, 7)]:
        return {k: v for k, v in kwargs.items() if v is not None}
