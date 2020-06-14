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
import arrow
from configs.ConfManage import ConfManage
from helpers.timer import timepiece
from helpers.logger import Logger
from math import ceil, floor
from helpers.predictor import get_showup_feature_frame, get_quote_dashboard, get_work_dashboard, \
    get_accept_feature_frame, get_CSAccept, get_CSQuote
from helpers.cache import Cache
from helpers.pickler import reload_pickle_cache, init_pickle_cache
from xgboost.core import XGBoostError
from datetime import datetime
import json
from models.po_cache_ret import POCacheRet


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

    def seconds_to_Duration(self, seconds):
        if seconds is None:
            return None
        hours = max(floor(seconds / 3600), 0.)
        remainder = seconds - (hours * 3600)
        minutes = max(floor(remainder / 60), 0.)
        remainder = remainder - (minutes * 60)
        seconds = max(ceil(remainder), 0.)
        return Duration(hours=hours, minutes=minutes, seconds=seconds)

    def dict_to_Range(self, range_dict):
        if range_dict is None:
            return None
        return Range(shortest=self.seconds_to_Duration(range_dict.get('shortest')), \
                     longest=self.seconds_to_Duration(range_dict.get('longest')))

    def __accept(self, args):
        results = []
        N = ConfManage.getFloat("ACCEPT_N_PERCENT")
        try:
            result_list = get_accept_feature_frame(args, 'xgb')
            logger.info("predictAccept features={}".format(result_list))
        except XGBoostError as err:
            logger.error("PredictAccept XGBoostError:{}".format(err))
        except Exception as err:
            logger.error("predictAccept error: {}".format(err))
            raise
        for item in result_list:
            pre_accept = item["pre_accept"]
            if pre_accept <= 5 - N:
                shortest_result, longest_result = 0, 5 * 60
            elif pre_accept < 10 - N:
                shortest_result, longest_result = 5 * 60, 10 * 60
            elif pre_accept < 20 - N:
                shortest_result, longest_result = 10 * 60, 20 * 60
            elif pre_accept < 30 - N:
                shortest_result, longest_result = 20 * 60, 30 * 60
            elif pre_accept < 45 - N:
                shortest_result, longest_result = 30 * 60, 45 * 60
            elif pre_accept < 60 - N:
                shortest_result, longest_result = 45 * 60, 60 * 60
            elif pre_accept < 90 - N:
                shortest_result, longest_result = 60 * 60, 90 * 60
            else:
                shortest_result, longest_result = 90 * 60, 120 * 60
            if ("test_mode" in item) and (item["test_mode"]):
                results.append(Prediction(area_id=int(item['area_id']), tasker_id=None,
                                          result=self.dict_to_Range(
                                              dict(shortest=shortest_result, longest=longest_result)),
                                          features={k: str(v) for k, v in item.items()}))
            else:
                results.append(
                    Prediction(area_id=int(item['area_id']), tasker_id=None,  # original_time=round(pre_accept, 3),
                               result=self.dict_to_Range(dict(shortest=shortest_result, longest=longest_result))))
        logger.info('predictAccept results={}'.format(results))
        return results

    def acceptResult(self, request_id, args):
        results = []
        N = ConfManage.getFloat("ACCEPT_N_PERCENT")
        try:
            result_list = get_accept_feature_frame(args, 'xgb')
            logger.info("{}: predictAccept features={}".format(request_id, result_list))
        except XGBoostError as err:
            logger.error('predictAccept XGBoostError: {}'.format(err))
            res = PredictionResult(request_id=str(request_id), error=1601, err_msg=str(err), data=results)
            return res
        except Exception as err:
            logger.error("predictAccept error: {}".format(err))
            res = PredictionResult(request_id=str(request_id), error=int(str(err)[:4]), err_msg=str(err)[4:], data=results)
            return res
        for item in result_list:
            pre_accept = item["pre_accept"]
            if pre_accept <= 5 - N:
                shortest_result, longest_result = 0, 5
            elif pre_accept < 10 - N:
                shortest_result, longest_result = 5, 10
            elif pre_accept < 20 - N:
                shortest_result, longest_result = 10, 20
            elif pre_accept < 30 - N:
                shortest_result, longest_result = 20, 30
            elif pre_accept < 45 - N:
                shortest_result, longest_result = 30, 45
            elif pre_accept < 60 - N:
                shortest_result, longest_result = 45, 60
            elif pre_accept < 90 - N:
                shortest_result, longest_result = 60, 90
            else:
                shortest_result, longest_result = 90, 120
            fixed_extra_data = {"area_id": str(item["area_id"]), "shortest": str(shortest_result),
                                "longest": str(longest_result)}
            fixed_extra_data.update({i:str(item[i]) if i in item else "" for i in item["extra_keys"]})
            if ("test_mode" in item) and (item["test_mode"]):
                results.append(Data(result=round(pre_accept, 3),
                                    extra_data=fixed_extra_data,
                                    features={k: str(v) for k, v in item.items()})
                               )
            else:
                results.append(Data(result=round(pre_accept, 3),
                                    extra_data=fixed_extra_data
                               ))
        res = PredictionResult(request_id=str(request_id), error=0, data=results)
        logger.info('{}: predictAccept results={}'.format(request_id, results))
        return res

    @timepiece(5)
    def predictAcceptTime(self, queries):
        request_id = sys.maxsize - int(arrow.now().float_timestamp * 100)
        logger.info('{} : predictAccept queries={}'.format(request_id, queries))
        args = []
        for query in queries:
            arg = {}
            arg['area_id'] = query.area_id
            arg['brand_id'] = query.brand_id
            arg['user_id'] = query.user_id
            if query.extra_data:
                arg["extra_data"] = query.extra_data
            if query.extra_keys:
                arg["extra_keys"] = query.extra_keys
            if query.test_mode:
                arg['test_mode'] = query.test_mode
            args.append(arg)
        results = self.acceptResult(request_id, args)
        return results

    @timepiece(5)
    def newpredictAcceptStore(self, queries):
        logger.info('predictAccept queries={}'.format(queries))
        args = []
        for query in queries:
            arg = {}
            arg['area_id'] = query.area_id
            arg['brand_id'] = query.brand_id
            arg['user_id'] = query.user_id
            if query.test_mode:
                arg['test_mode'] = query.test_mode
            args.append(arg)
        results = self.__accept(args)
        return results

    @timepiece(5)
    def newpredictAccept(self, queries):
        return self.newpredictAcceptStore(queries)

    @timepiece(5)
    def predictShowup(self, queries):
        logger.info('predictShowup queries={}'.format(queries))
        args = []
        results = []
        for query in queries:
            __validate_coordinates__(query)
            arg = {}
            arg['area_id'] = query.area_id
            arg['tasker_id'] = query.tasker_id
            if query.user_id:
                arg['user_id'] = query.user_id
            arg['showup_distance'] = query.showup_distance
            arg['tasker_coordinate'] = query.tasker_coordinate  # 车手经纬度
            arg['shop_coordinate'] = query.shop_coordinate  # 商店经纬度
            if query.test_mode:
                arg["test_mode"] = query.test_mode
            args.append(arg)
        try:
            result_list = get_showup_feature_frame(args, 'xgb')
            logger.info("predictShowup features={}".format(result_list))
        except XGBoostError as err:
            logger.error('predictShowup XGBoostError: {}'.format(err))
        for i in result_list:
            predict_showup = i['predict_showup']
            if ("test_mode" in i) and (i["test_mode"]):
                results.append(Prediction_showup(area_id=int(i['area_id']), tasker_id=int(i['tasker_id']),
                                                 user_id=i.get("user_id", None),
                                                 result=float(predict_showup),
                                                 features={k: str(v) for k, v in i.items()}))
            else:
                results.append(Prediction_showup(area_id=int(i['area_id']), tasker_id=int(i['tasker_id']),
                                                 user_id=i.get("user_id", None),
                                                 result=float(predict_showup)))
        logger.info('predictShowup results={}'.format(results))
        return results

    @timepiece(5)
    def predictShowupTime(self, queries):
        request_id = sys.maxsize - int(arrow.now().float_timestamp * 100)
        logger.info('{} : predictShowup queries={}'.format(request_id, queries))
        args = []
        results = []
        for query in queries:
            arg = {}
            arg['area_id'] = query.area_id
            arg['tasker_id'] = query.tasker_id
            arg['tasker_coordinate'] = query.tasker_coordinate  # 车手经纬度
            arg['shop_coordinate'] = query.shop_coordinate  # 商店经纬度
            if query.extra_data:
                arg["extra_data"] = query.extra_data
            if query.extra_keys:
                arg["extra_keys"] = query.extra_keys
            if query.user_id:
                arg['user_id'] = query.user_id
            if query.order_id:
                arg['order_id'] = query.order_id
            if query.test_mode:
                arg['test_mode'] = query.test_mode
            args.append(arg)
        try:
            result_list = get_showup_feature_frame(args, 'xgb')
            logger.info("{}: predictShowup features={}".format(request_id, result_list))
        except XGBoostError as err:
            logger.error('predictShowup XGBoostError: {}'.format(err))
            res = PredictionResult(request_id=str(request_id), error=1601, err_msg=str(err), data=results)
            return res
        except Exception as err:
            logger.error("predictShowup error: {}".format(err))
            res = PredictionResult(request_id=str(request_id), error=int(str(err)[:4]), err_msg=int(str(err)[4:]), data=results)
            return res
        for item in result_list:
            predict_showup = item["predict_showup"]
            if ("test_mode" in item) and (item["test_mode"]):
                results.append(Data(result=round(predict_showup, 3),
                                    extra_data={i:str(item[i]) if i in item else "" for i in item["extra_keys"]},
                                    features={k: str(v) for k, v in item.items()})
                               )
            else:
                results.append(Data(result=round(predict_showup, 3),
                                    extra_data={i:str(item[i]) if i in item else "" for i in item["extra_keys"]},)
                               )
        res = PredictionResult(request_id=str(request_id), error=0, data=results)
        logger.info('{}: predictShowup results={}'.format(request_id, results))
        return res

    @timepiece(5)
    def predictQuote(self, queries):
        logger.info('predictQuote queries={}'.format(queries))
        results = []
        args = []
        for query in queries:
            arg = {}
            arg['area_id'] = query.area_id
            if query.brand_id is not None:
                arg['brand_id'] = query.brand_id
            if query.user_id:
                arg['user_id'] = query.user_id
            if query.receive_coordinate and query.shop_coordinate:
                arg['receive_coordinate'] = query.receive_coordinate
                arg['shop_coordinate'] = query.shop_coordinate  # 商店经纬度
            if query.test_mode:
                arg["test_mode"] = query.test_mode
            args.append(arg)
        try:
            result_list = get_quote_dashboard(args, 'xgb')
            logger.info("predictQuote features={}".format(result_list))
        except XGBoostError as err:
            logger.error('predictQuote XGBoostError: {}'.format(err))
        # except Exception as err:
        #     logger.error("predictQuote error: {}".format(err))
        for item in result_list:
            if ("test_mode" in item) and (item["test_mode"]):
                results.append(Prediction_quote(area_id=int(item['area_id']),
                                                user_id=int(item['user_id']) if 'user_id' in item else None,
                                                result=float(item['predict_value']),
                                                features={k: str(v) for k, v in item.items()}))
            else:
                results.append(Prediction_quote(area_id=int(item['area_id']),
                                                user_id=item.get("user_id", None),
                                                result=float(item['predict_value'])))
        logger.info('predictQuote results={}'.format(results))
        return results

    def predictQuoteTime(self, queries):
        request_id = sys.maxsize - int(arrow.now().float_timestamp * 100)
        logger.info('{} : predictQuote queries={}'.format(request_id, queries))
        args = []
        results = []
        for query in queries:
            arg = {}
            arg['area_id'] = query.area_id
            if query.brand_id is not None:
                arg['brand_id'] = query.brand_id
            if query.user_id:
                arg['user_id'] = query.user_id
            if query.receive_coordinate and query.shop_coordinate:
                arg['receive_coordinate'] = query.receive_coordinate
                arg['shop_coordinate'] = query.shop_coordinate  # 商店经纬度
            if query.test_mode:
                arg["test_mode"] = query.test_mode
            if query.extra_data:
                for k, v in query.extra_data.items():
                    arg[k] = v
            if query.extra_keys:
                arg["extra_keys"] = query.extra_keys
            args.append(arg)
        try:
            result_list = get_quote_dashboard(args, 'xgb')
            logger.info("{}: predictQuote features={}".format(request_id, result_list))
        except XGBoostError as err:
            logger.error('predictQuote XGBoostError: {}'.format(err))
            res = PredictionResult(request_id=str(request_id), error=1601, err_msg=str(err), data=results)
            return res
        except Exception as err:
            logger.error("predictQuote error: {}".format(err))
            PredictionResult(request_id=str(request_id), error=int(str(err)[:4]), err_msg=int(str(err)[4:]), data=results)
            raise
        for item in result_list:
            predict_quote = item["predict_value"]
            if ("test_mode" in item) and (item["test_mode"]):
                results.append(Data(result=round(predict_quote, 3),
                                    extra_data={i:str(item[i]) if i in item else "" for i in item["extra_keys"]},
                                    features={k: str(v) for k, v in item.items()})
                               )
            else:
                results.append(Data(result=round(predict_quote, 3),
                                    extra_data={i:str(item[i]) if i in item else "" for i in item["extra_keys"]})
                               )
        res = PredictionResult(request_id=str(request_id), error=0, data=results)
        logger.info('{}: predictQuote results={}'.format(request_id, results))
        return res


    @timepiece(5)
    def predictDelivery(self, queries):
        logger.info('predictDelivery queries={}'.format(queries))
        results = []
        args = []
        for query in queries:
            arg = {}
            arg['area_id'] = query.area_id
            arg['tasker_id'] = query.tasker_id
            arg['status'] = 0 if query.status in [403, 404, 917] else 1
            arg['order_id'] = query.order_id
            arg['tasker_coordinate'] = query.tasker_coordinate  # 车手经纬度
            if query.user_id:
                arg["user_id"] = query.user_id
            if query.test_mode:
                arg['test_mode'] = query.test_mode
            if query.receive_coordinate:
                arg['receive_coordinate'] = query.receive_coordinate
            if query.shop_coordinate:
                arg['shop_coordinate'] = query.shop_coordinate  # 商店经纬度
            args.append(arg)
        try:
            result_list = get_work_dashboard(args, 'xgb')
            logger.info("predictDelivery features={}".format(result_list))
        except XGBoostError as err:
            logger.error('predictWork XGBoostError: {}'.format(err))
        for i in result_list:
            predict_delivery = i['predict_delivery']
            if ("test_mode" in i) and (i["test_mode"]):
                results.append(Prediction_delivery(area_id=int(i['area_id']), tasker_id=int(i['tasker_id']),
                                                   order_id=int(i['order_id']),
                                                   user_id=i.get("user_id", None),
                                                   result=float(predict_delivery),
                                                   features={k: str(v) for k, v in i.items()}))
            else:
                results.append(Prediction_delivery(area_id=int(i['area_id']), tasker_id=int(i['tasker_id']),
                                                   order_id=int(i['order_id']), result=float(predict_delivery)))
        logger.info('predictDelivery results={}'.format(results))
        return results

    def predictDeliveryTime(self, queries):
        request_id = sys.maxsize - int(arrow.now().float_timestamp * 100)
        logger.info('{} : predictDelivery queries={}'.format(request_id, queries))
        args = []
        results = []
        for query in queries:
            arg = {}
            arg['area_id'] = query.area_id
            arg['tasker_id'] = query.tasker_id
            arg['status'] = 0 if query.status in [403, 404, 917] else 1
            arg['tasker_coordinate'] = query.tasker_coordinate  # 车手经纬度
            if query.order_id:
                arg['order_id'] = query.order_id
            if query.user_id:
                arg["user_id"] = query.user_id
            if query.test_mode:
                arg['test_mode'] = query.test_mode
            if query.receive_coordinate:
                arg['receive_coordinate'] = query.receive_coordinate
            if query.shop_coordinate:
                arg['shop_coordinate'] = query.shop_coordinate  # 商店经纬度
            if query.extra_data:
                arg["extra_data"] = query.extra_data
            if query.extra_keys:
                arg["extra_keys"] = query.extra_keys
            args.append(arg)
        try:
            result_list = get_work_dashboard(args, 'xgb')
            logger.info("{}: predictDelivery features={}".format(request_id, result_list))
        except XGBoostError as err:
            logger.error('predictDelivery XGBoostError: {}'.format(err))
            res = PredictionResult(request_id=str(request_id), error=1601, err_msg=str(err), data=results)
            return res
        except Exception as err:
            logger.error("predictDelivery error: {}".format(err))
            PredictionResult(request_id=str(request_id), error=int(str(err)[:4]), err_msg=int(str(err)[4:]), data=results)
            raise
        for item in result_list:
            predict_delivery = item["predict_delivery"]
            if ("test_mode" in item) and (item["test_mode"]):
                results.append(Data(result=round(predict_delivery, 3),
                                    extra_data={i:str(item[i]) if i in item else "" for i in item["extra_keys"]},
                                    features={k: str(v) for k, v in item.items()})
                               )
            else:
                results.append(Data(result=round(predict_delivery, 3),
                                    extra_data={i:str(item[i]) if i in item else "" for i in item["extra_keys"]})
                               )
        res = PredictionResult(request_id=str(request_id), error=0, data=results)
        logger.info('{}: predictDelivery results={}'.format(request_id, results))
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

    @timepiece(5)
    def CSAccept(self, queries):
        request_id = sys.maxsize - int(arrow.now().float_timestamp * 100)
        logger.info('{} : QSAccept queries={}'.format(request_id, queries))
        args = []
        for query in queries:
            arg = {}
            arg['area_id'] = query.area_id
            arg['brand_id'] = query.brand_id
            arg['user_id'] = query.user_id
            if query.test_mode:
                arg['test_mode'] = query.test_mode
            args.append(arg)
        results = []
        N = ConfManage.getFloat("ACCEPT_N_PERCENT")
        try:
            result_list = get_CSAccept(args)
            logger.info("{}: QSAccept features={}".format(request_id, result_list))
            for item in result_list:
                pre_accept = item["pre_accept"]
                if pre_accept <= 5 - N:
                    shortest_result, longest_result = 0, 5
                elif pre_accept < 10 - N:
                    shortest_result, longest_result = 5, 10
                elif pre_accept < 20 - N:
                    shortest_result, longest_result = 10, 20
                elif pre_accept < 30 - N:
                    shortest_result, longest_result = 20, 30
                elif pre_accept < 45 - N:
                    shortest_result, longest_result = 30, 45
                elif pre_accept < 60 - N:
                    shortest_result, longest_result = 45, 60
                elif pre_accept < 90 - N:
                    shortest_result, longest_result = 60, 90
                else:
                    shortest_result, longest_result = 90, 120
                if ("test_mode" in item) and (item["test_mode"]):
                    results.append(
                        Data(result=round(pre_accept, 3),
                             extra_data={"area_id": str(item["area_id"]), "shortest": str(shortest_result),
                                         "longest": str(longest_result)},
                             features={k: str(v) for k, v in item.items()})
                    )
                else:
                    results.append(
                        Data(result=round(pre_accept, 3),
                             extra_data={"area_id": str(item["area_id"]), "shortest": str(shortest_result),
                                         "longest": str(longest_result)})
                    )
            results = PredictionResult(request_id=str(request_id), error=0, data=results)
        except Exception as err_msg:
            results = PredictionResult(request_id=str(request_id), error=int(err_msg[:4]), err_msg=str(err_msg[4:]), data=results)
        logger.info('{}: QSAccept results={}'.format(request_id, results))
        return results

    @timepiece(5)
    def CSQuote(self, queries):
        request_id = sys.maxsize - int(arrow.now().float_timestamp * 100)
        logger.info('QSQuote queries={}'.format(queries))
        results = []
        args = []
        for query in queries:
            arg = {}
            arg['area_id'] = query.area_id
            if query.brand_id is not None:
                arg['brand_id'] = query.brand_id
            if query.user_id:
                arg['user_id'] = query.user_id
            if query.receive_coordinate and query.shop_coordinate:
                arg['receive_coordinate'] = query.receive_coordinate
                arg['shop_coordinate'] = query.shop_coordinate  # 商店经纬度
            if query.test_mode:
                arg["test_mode"] = query.test_mode
            args.append(arg)

        try:
            result_list = get_CSQuote(args)
            logger.info("{}: QSQuote features={}".format(request_id, result_list))
            for item in result_list:
                if ("test_mode" in item) and (item["test_mode"]):
                    results.append(Data(result=round(item["predict_value"], 3),
                             extra_data={"area_id": str(item["area_id"])},
                             features={k: str(v) for k, v in item.items()}))
                else:
                    results.append(Data(result=round(item["predict_value"], 3),
                             extra_data={"area_id": str(item["area_id"])},))
            res = PredictionResult(request_id=str(request_id), error=0, data=results)
        except Exception as err:
            res = PredictionResult(request_id=str(request_id), error=int(err[:4]), err_msg=str(err[4:]), data=results)
        logger.info('{}: QSQuote results={}'.format(request_id, results))
        return res