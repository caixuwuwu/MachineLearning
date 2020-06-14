#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 pickler.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module definining useful pickle-related methods"""
import os
import sys
from pickle import dump, load, PicklingError, UnpicklingError, HIGHEST_PROTOCOL
from configs.ConfManage import ConfManage
from helpers.logger import Logger
from helpers.cache import Cache
from sklearn.externals import joblib
from models.po_cache_ret import POCacheRet

logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))
PICKLE_FOLDER = ConfManage.getString("PICKLE_FOLDER")
cache = Cache.get_instance()
pickle_prefix = '%s-%s-' % (ConfManage.getString("APP_MODE"), ConfManage.getString("ZONE"))

if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    # pylint: disable=E0401, E0611, E1101
    import importlib

    importlib.reload(sys)


def delete_pickle(name):
    filepath = '%s/%s%s.pkl' % (PICKLE_FOLDER, pickle_prefix, name)
    try:
        os.remove(filepath)
        return True
    except OSError:  # File Not Found
        return False


def load_pickle(name='undefined', using_joblib=False):
    filename = '%s%s.pkl' % (pickle_prefix, name)
    filepath = '%s/%s' % (PICKLE_FOLDER, filename)
    try:
        if using_joblib:
            return joblib.load(filepath)
        else:
            with open(filepath, 'rb') as file:
                try:
                    return load(file)
                except UnicodeDecodeError:
                    import hashlib
                    return hashlib.sha1(file.read()).hexdigest()
    except (IOError, EOFError):  # File Not Found
        logger.debug('file_not_found: {}'.format(filepath))
        return None
    except UnpicklingError:
        return None


def load_pickle_cache(name='undefined', using_joblib=False):
    cache_key = 'pickle_cache_{}'.format(name)
    ret = cache.get(cache_key)
    if ret is None:
        logger.debug('load_pickle_cache, fetch from raw pickle')
        ret = load_pickle(name, using_joblib)
        if ret is not None:
            cached = cache.set(cache_key, ret, ConfManage.getInt("PICKLE_CACHE_EXPIRE"))
            logger.debug('load_pickle_cache, set cache, cache_key={}, status={}'.format(cache_key, cached))
    else:
        logger.debug('load_pickle_cache, fetch from cache, cache_key={}'.format(cache_key))
    return ret


def reload_pickle_cache(cache_key):
    keys = cache_key.split(',')
    reload_pickle = []
    for key in keys:
        po_cache_ret_obj = POCacheRet(key)
        po_cache_ret_obj.cleared = cache.delete('pickle_cache_{}'.format(key))
        if key.endswith('features') or key.endswith('mae'):
            cache_obj = load_pickle_cache(key)
        else:
            cache_obj = load_pickle_cache(key, True)
        po_cache_ret_obj.reloaded = cache_obj is not None
        reload_pickle.append(po_cache_ret_obj.__dict__)
    return reload_pickle


def init_pickle_cache():
    RELOAD_PICKLE_CACHE_KEY = ConfManage.getString("RELOAD_PICKLE_CACHE_KEY")
    logger.info('start init_pickle_cache RELOAD_PICKLE_CACHE_KEY={}'.format(RELOAD_PICKLE_CACHE_KEY))
    if RELOAD_PICKLE_CACHE_KEY is not None:
        result = reload_pickle_cache(RELOAD_PICKLE_CACHE_KEY)
        logger.info('init_pickle_cache result={}'.format(result))


def save_pickle(obj, name='undefined', using_joblib=False):
    filename = '%s%s.pkl' % (pickle_prefix, name)
    filepath = '%s/%s' % (PICKLE_FOLDER, filename)
    logger.info('save_pickle filepath={}'.format(filepath))
    try:
        if using_joblib:
            joblib.dump(obj, filepath, compress=3)
        else:
            with open(filepath, 'wb') as handle:
                dump(obj, handle, protocol=HIGHEST_PROTOCOL)
        return True
    except PicklingError:
        return False
