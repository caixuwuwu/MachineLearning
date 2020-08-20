#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 thrift.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	 <caixuwu@outlook.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module defining class ETAThriftServer & EstimateTaskDurationsHandler"""
import glob
import sys
import json
from datetime import datetime
import uuid

from helpers.predictor import *
from helpers.cache import Cache
from helpers.pickler import reload_pickle_cache, init_pickle_cache
from helpers.po_cache_ret import POCacheRet


if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    # pylint: disable=E0401, E0611, E1101
    import importlib
    importlib.reload(sys)

logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))
# Import Thrift generated classes
sys.path.append('gen-py')
sys.path.insert(0, glob.glob('../../lib/py/build/lib*'[0]))
try:
    from eta import EstimateTaskDurations
    from eta.ttypes import Duration, Range, InvalidInput, ModelMissing, Prediction, Params, \
        Prediction_showup, Prediction_quote, Prediction_delivery, PredictionResult, Data
except ImportError:
    logger.error('Cannot find thrift classes.')
    logger.error('Have (you run `thrift --gen py eta.thrift`?')
    raise


def __validate_coordinates__(query):
    if query.showup_distance is None:
        raise InvalidInput(error_code=422, error_message='Input tuple `showup_distance` is nil.')
    elif not isinstance(query.showup_distance, float):
        raise InvalidInput(error_code=422, error_message= 'Each coordinate in `showup_distance` must be represented '
                                                          'by type `float`.')
    # Validates Starting Coordinates
    tasker_coordinate_list = query.tasker_coordinate.split(',')
    if query.tasker_coordinate is None:
        raise InvalidInput(error_code=422, error_message= 'Input tuple `tasker_coordinate` is nil.')
    elif ',' not in query.tasker_coordinate and len(tasker_coordinate_list) != 2:
        raise InvalidInput(error_code=422, error_message=
        'Input string `tasker_coordinate` must have length of two and use "," to split them.')
    elif not (isinstance(eval(tasker_coordinate_list[0]), float) and isinstance(eval(tasker_coordinate_list[1]), float)):
        raise InvalidInput(error_code=422, error_message=
            'Each coordinate in `tasker_coordinate` must be represented by type `float`.')
    # Validates Destination Coordinates
    shop_coordinate_list = query.shop_coordinate.split(',')
    if query.shop_coordinate is None:
        raise InvalidInput(error_code=422, error_message= 'Input tuple `shop_coordinate` is nil.')
    elif ',' not in query.shop_coordinate and len(shop_coordinate_list) != 2:
        raise InvalidInput(error_code=422, error_message=
            'Input string `shop_coordinate` must have length of two and use "," to split them.')
    elif not (isinstance(eval(shop_coordinate_list[0]), float) and isinstance(eval(shop_coordinate_list[1]), float)):
        raise InvalidInput(error_code=422, error_message= 'Each coordinate in `shop_coordinate` must be represented by '
                                                          'type `float`.')


class EstimateTaskDurationsHandler(object):
    def __init__(self):
        self.cache = Cache.get_instance()
        init_pickle_cache()

    def predictTime(self):
        request_id = uuid.uuid1().int
        results = []
        res = PredictionResult(request_id=str(request_id), error=1, err_msg="please code it", data=results)
        return res


    def listKeys(self):
        logger.info('listKeys')
        keys = []
        for key in self.cache.mem.keys():
            keys.append(POCacheRet(key, expired=datetime.fromtimestamp(self.cache.time[key]).strftime(
                '%Y-%m-%d %H:%M:%S')).__dict__)
        result = json.dumps(keys)
        logger.info('listKeys results={}'.format(result))
        return result

    def clearCache(self):
        logger.info('clearCache')
        result = self.cache.clear()
        logger.info('clearCache results={}'.format(result))
        return result

    def clearCacheByKey(self, cache_key):
        logger.info('clearCacheByKey cache_key={}'.format(cache_key))
        keys = cache_key.split(',')
        cleared = []
        for key in keys:
            cleared.append(POCacheRet(key, cleared=self.cache.delete(key)).__dict__)
        result = json.dumps(cleared)
        logger.info('clearCacheByKey results={}'.format(result))
        return result

    def reloadPickleCache(self, cache_key):
        logger.info('reloadPickleCache cache_key={}'.format(cache_key))
        reload_pickle = reload_pickle_cache(cache_key)
        result = json.dumps(reload_pickle)
        logger.info('reloadPickleCache results={}'.format(result))
        return result

