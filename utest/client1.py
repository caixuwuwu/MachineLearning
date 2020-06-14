#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 client.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	 caixuwu <caixuwu@km-it.cn>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module containing ETA Client-Launch Script to ThriftService"""
import unittest
import glob
import sys
from configs.ConfManage import ConfManage
from helpers.logger import Logger
from helpers.thrift_client import ThriftClient
from helpers.parallel import multi_process

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
    from eta import EstimateTaskDurations
    from eta.ttypes import Params, InvalidInput, ModelMissing, Params_quote, Params_delivery, Params_accept, \
        Params_showup, \
        ParamsDelivery, ParamsQuote
except ImportError:
    requirements_logger.error('Cannot find thrift classes.')
    requirements_logger.error('Have you run `thrift --gen py eta.thrift`?')
    raise


def main():
    # Create a client
    endpoint = "47.56.204.88"  # release
    # endpoint = "47.56.90.144" # rc
    # endpoint = "ap2-eta.ks-it.co" # sg release
    # endpoint = "localhost"
    # port = 19090
    port = 9090
    client = ThriftClient(EstimateTaskDurations, host=endpoint, port=port, timeout=60000)
    # area_ids = [334, 362]  # 362
    area_ids = [17, 161]  # 362
    brand_ids = [17, 8]
    user_ids = [100000034, 100000669]
    order_ids = [2019112207245298, 2019082530249852]
    status = [405, 405]
    receive_coordinate = ["114.1978517700,22.3366929672", "114.34,22.40"]
    tasker_coordinate = ["114.43,22.4506", "114.54,22.5403"]
    shop_coordinate = ["114.1741625,22.3267688", "114.1590247,22.2832107"]
    tasker_ids = [7444, 10086]
    showup_distances = [10.21, 10.21]
    extra_data = [{"service_type": "2"}, {"box_size": "UNKNOW", "order_value": "120", "product": "FDP-LONG"}]
    extra_keys = [["order_id"], ["area_id"]]
    test_mode = [True, False]
    params = []
    result = None
    # 'accept_dashboard':
    for i in range(len(area_ids)):
        params.append(Params_accept(area_id=int(area_ids[i]),
                                    brand_id=int(brand_ids[i]),
                                    user_id=int(user_ids[i]) if user_ids != None else None,
                                    test_mode=test_mode[i] if test_mode else None))
    result = client.invoke('newpredictAccept', params)
    print("accept_dashboard：", result, "\n")
    params = []

    # 'accept_store':
    for i in range(len(area_ids)):
        params.append(Params_accept(area_id=int(area_ids[i]),
                                    brand_id=int(brand_ids[i]),
                                    user_id=None, # int(user_ids[i]) if user_ids != None else None,
                                    test_mode=test_mode[i] if test_mode else None))
    # ----------------------------并发请求------------------------------------
    function = [ThriftClient(EstimateTaskDurations, host=endpoint, port=port).invoke] * 1
    args = [("newpredictAcceptStore", params)] * 1
    results = multi_process(function, args, processnum=1)
    for i in range(len(results)):
        print("accept_store：", results[i].get(), "\n")
    params = []

    # 'showup':
    for i in range(len(area_ids)):
        params.append(Params(area_id=int(area_ids[i]),
                             tasker_id=int(tasker_ids[i]),
                             user_id=int(user_ids[i]) if user_ids != None else None,
                             showup_distance=float(showup_distances[i]),
                             tasker_coordinate=str(tasker_coordinate[i]),
                             shop_coordinate=str(shop_coordinate[i]),
                             test_mode=test_mode[i] if test_mode else None))
    result = client.invoke('predictShowup', params)
    print("predictShowup：", result, "\n")
    params = []

    # 'delivery':
    for i in range(len(area_ids)):
        params.append(Params_delivery(area_id=int(area_ids[i]),
                                      tasker_id=int(tasker_ids[i]),
                                      user_id=int(user_ids[i]) if user_ids != None else None,
                                      receive_coordinate=receive_coordinate[i],
                                      tasker_coordinate=tasker_coordinate[i],
                                      shop_coordinate=shop_coordinate[
                                          i] if shop_coordinate is not None else None,
                                      order_id=int(order_ids[i]),
                                      status=int(status[i]),
                                      test_mode=test_mode[i] if test_mode else None))
    result = client.invoke('predictDelivery', params)
    print("predictDelivery：", result, "\n")
    params = []

    # 'quote':
    for i in range(len(area_ids)):
        params.append(Params_quote(area_id=int(area_ids[i]),
                                   brand_id=int(brand_ids[i]) if brand_ids else None,
                                   user_id=int(user_ids[i]) if user_ids else None,
                                   receive_coordinate=receive_coordinate[i] if receive_coordinate else None,
                                   shop_coordinate=shop_coordinate[i] if shop_coordinate else None,
                                   test_mode=test_mode[i] if test_mode else None))
    result = client.invoke('predictQuote', params)
    print("predictQuote：", result, "\n")
    params = []

    # 'predictAcceptTime':
    for i in range(len(area_ids)):
        params.append(Params_accept(area_id=int(area_ids[i]),
                                    brand_id=int(brand_ids[i]),
                                    user_id=int(user_ids[i]) if user_ids != None else None,
                                    extra_data=extra_data[i] if extra_data != None else None,
                                    extra_keys=extra_keys[i] if extra_keys != None else None,
                                    test_mode=test_mode[i] if test_mode else None))
        function = [ThriftClient(EstimateTaskDurations, host=endpoint, port=port).invoke] * 1
        args = [("predictAcceptTime", params)] * 1
        results = multi_process(function, args, processnum=1)
        for i in range(len(results)):
            print("predictAcceptTime：", results[i].get(), "\n")
    params = []

    # 'predictDeliveryTime':
    for i in range(len(area_ids)):
        params.append(ParamsDelivery(area_id=int(area_ids[i]),
                                     tasker_id=int(tasker_ids[i]),
                                     order_id=int(order_ids[i]) if order_ids else None,
                                     user_id=int(user_ids[i]) if user_ids else None,
                                     tasker_coordinate=tasker_coordinate[i],
                                     receive_coordinate=str(receive_coordinate[i]) if receive_coordinate else None,
                                     shop_coordinate=str(shop_coordinate[i]) if shop_coordinate else None,
                                     status=int(status[i]),
                                     extra_data=extra_data[i] if extra_data else None,
                                     extra_keys=extra_keys[i] if extra_keys else None,
                                     test_mode=test_mode[i] if test_mode else None, ))
    result = client.invoke('predictDeliveryTime', params)
    print("predictDeliveryTime：", result, "\n")
    params = []

    # 'predictShowupTime':
    for i in range(len(area_ids)):
        params.append(Params_showup(area_id=int(area_ids[i]), tasker_id=int(tasker_ids[i]),
                                    tasker_coordinate=str(tasker_coordinate[i]),
                                    shop_coordinate=str(shop_coordinate[i]),
                                    extra_data=extra_data[i] if extra_data else None,
                                    extra_keys=extra_keys[i] if extra_keys else None,
                                    order_id=int(order_ids[i]) if order_ids else None,
                                    user_id=int(user_ids[i]) if user_ids else None,
                                    test_mode=test_mode[i] if test_mode else None, ))
    result = client.invoke('predictShowupTime', params)
    print("predictShowupTime：", result, "\n")
    params = []

    # 'predictQuoteTime':
    for i in range(len(area_ids)):
        params.append(ParamsQuote(area_id=int(area_ids[i]),
                                  user_id=int(user_ids[i]) if user_ids else None,
                                  receive_coordinate=str(receive_coordinate[i]) if receive_coordinate else None,
                                  shop_coordinate=str(shop_coordinate[i]) if shop_coordinate else None,
                                  extra_data=extra_data[i] if extra_data else None,
                                  extra_keys=extra_keys[i] if extra_keys else None,
                                  test_mode=test_mode[i] if test_mode else None, ))
    result = client.invoke('predictQuoteTime', params)
    print("predictQuoteTime：", result, "\n")
    params = []

    # # 'CSQuote':
    # for i in range(len(area_ids)):
    #     params.append(Params_quote(area_id=int(area_ids[i]),
    #                                brand_id=int(brand_ids[i]) if brand_ids else None,
    #                                user_id=int(user_ids[i]) if user_ids else None,
    #                                receive_coordinate=receive_coordinate[i] if receive_coordinate else None,
    #                                shop_coordinate=shop_coordinate[i] if shop_coordinate else None,
    #                                test_mode=test_mode[i] if test_mode else None))
    # result = client.invoke('CSQuote', params)
    # print("CSQuote：", result, "\n")
    # params = []
    #
    # # 'CSAccept':
    # for i in range(len(area_ids)):
    #     params.append(Params_accept(area_id=int(area_ids[i]), brand_id=int(brand_ids[i]),
    #                                 user_id=int(user_ids[i]) if user_ids != None else None,
    #                                 test_mode=test_mode[i] if test_mode else None,))
    # result = client.invoke('CSAccept', params)
    # print("CSAccept：", result, "\n")
    # params = []


if __name__ == '__main__':
    main()
