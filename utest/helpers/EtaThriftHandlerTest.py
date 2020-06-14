#!/usr/bin/env python3
# coding=utf-8
'''
@Description: eta_thrift_heandler单元测试
@Author: Jack Zhou (jack@ks-it.co)
@Date: 2019-08-23 13:51:11
@LastEditors: Jack Zhou
@LastEditTime: 2019-08-23 18:17:03
'''

import unittest
import sys
import random

from helpers.eta_thrift_handler import EstimateTaskDurationsHandler
from models.DbCommon import DbCommon
from configs.conf import ZONE
from utest.config import Config
from utest.config import tasker

sys.path.append('gen-py')
from eta.ttypes import Prediction, Params_quote, Prediction_quote, ParamsQuote, Params_accept, Params_delivery, ParamsDelivery, \
                        Params, Params_showup, PredictionResult, Prediction_delivery, Prediction_showup, Range


area_id = DbCommon().fetch_server_area()  # DataFrame["id", "parent_id", "name"]
config = Config(ZONE)

class EtaThriftHandlerTest(unittest.TestCase):

    def setUp(self):
        self.eta_thrift_handler = EstimateTaskDurationsHandler()

    def test_predictQuote(self):
        queries = []
        for i in list(area_id.id):
            queries.append(Params_quote(area_id = int(i),
                                        user_id = random.choice([100000157, None]),
                                        brand_id = random.choice([1, 8, None]),
                                        receive_coordinate = random.choice(config.config.receive_coordinate),
                                        shop_coordinate = random.choice(config.config.shop_coordinate))
                           )
        results = self.eta_thrift_handler.predictQuote(queries)
        for idx, result in enumerate(results):
            self.assertIsInstance(result, Prediction_quote)
            self.assertIsInstance(result.result, float)
            self.assertGreater(result.result, 0.)
            # self.assertEqual(result.area_id, queries[idx].area_id)

    def test_predictAccept(self):
        queries = []
        for i in list(area_id.id):
            queries.append(Params_accept(area_id=int(i), brand_id=random.choice([1,8]), user_id=100000157))
        results = self.eta_thrift_handler.newpredictAcceptStore(queries)
        for idx, result in enumerate(results):
            self.assertIsInstance(result, Prediction)
            self.assertIsInstance(result.result, Range)
            self.assertGreaterEqual(result.result.shortest.minutes, 0.)
            self.assertGreaterEqual(result.result.longest.minutes, 5.)
            # self.assertEqual(result.area_id, queries[idx].area_id)

    def test_predictShowup(self):
        queries = []
        for i in list(area_id.id):
            queries.append(Params(area_id=int(i), tasker_id=random.choice(tasker), user_id=random.choice([100000157, None]),
                                  shop_coordinate=random.choice(config.config.shop_coordinate),
                                  tasker_coordinate=random.choice(config.config.tasker_coordinate),
                                  showup_distance=456.135
                                  ))
        results = self.eta_thrift_handler.predictShowup(queries)
        for idx, result in enumerate(results):
            self.assertIsInstance(result, Prediction_showup)
            self.assertIsInstance(result.result, float)
            self.assertGreater(result.result, 0.)
            # self.assertEqual(result.area_id, queries[idx].area_id)

    def test_predictDelivery(self):
        queries = []
        for i in list(area_id.id):
            queries.append(Params_delivery(area_id=int(i), tasker_id=random.choice(tasker), user_id=random.choice([100000044,None]),
                                           status=random.choice([0,1]),
                                           receive_coordinate=random.choice(config.config.receive_coordinate),
                                           shop_coordinate=random.choice(config.config.shop_coordinate),
                                           tasker_coordinate=random.choice(config.config.tasker_coordinate),
                                           order_id=2019082721292047
                                           ))
        results = self.eta_thrift_handler.predictDelivery(queries)
        for idx, result in enumerate(results):
            self.assertIsInstance(result, Prediction_delivery)
            self.assertIsInstance(result.result, float)
            self.assertGreater(result.result, 0.)
            # self.assertEqual(result.area_id, queries[idx].area_id)

    def test_predictDeliveryTime(self):
        queries = []
        for i in list(area_id.id):
            queries.append(ParamsDelivery(area_id=int(i), tasker_id=random.choice(tasker), user_id=random.choice([100000044,None]),
                                           status=random.choice([0,1]),
                                           receive_coordinate=random.choice(config.config.receive_coordinate),
                                           shop_coordinate=random.choice(config.config.shop_coordinate),
                                           tasker_coordinate=random.choice(config.config.tasker_coordinate),
                                           order_id=random.choice([2019082721292047, None])
                                           ))
        results = self.eta_thrift_handler.predictDeliveryTime(queries)
        self.assertIsInstance(results, PredictionResult)
        for idx, result in enumerate(results.data):
            self.assertIsInstance(result.result, float)
            self.assertGreater(result.result, 0.)
            # self.assertEqual(int(result.extra_data["area_id"]), queries[idx].area_id)



    def test_predictShowupTime(self):
        queries = []
        for i in list(area_id.id):
            queries.append(Params_showup(area_id=int(i), tasker_id=random.choice(tasker), user_id=random.choice([100000157, None]),
                                  shop_coordinate=random.choice(config.config.shop_coordinate),
                                  tasker_coordinate=random.choice(config.config.tasker_coordinate),
                                  extra_keys=["area_id"]))
        results = self.eta_thrift_handler.predictShowupTime(queries)
        self.assertIsInstance(results, PredictionResult)
        for idx, result in enumerate(results.data):
            self.assertIsInstance(result.result, float)
            self.assertGreater(result.result, 0.)
            # self.assertEqual(int(result.extra_data["area_id"]), queries[idx].area_id)

    def test_predictQuoteTime(self):
        queries = []
        for i in list(area_id.id):
            queries.append(ParamsQuote(area_id=int(i), user_id=random.choice([100000157, None]),
                                       brand_id=random.choice([1,8,None]),
                                       receive_coordinate=random.choice(config.config.receive_coordinate),
                                       shop_coordinate=random.choice(config.config.shop_coordinate),
                                       extra_keys=["area_id"]
                                       )
                           )
        results = self.eta_thrift_handler.predictQuoteTime(queries)
        self.assertIsInstance(results, PredictionResult)
        for idx, result in enumerate(results.data):
            self.assertIsInstance(result.result, float)
            self.assertGreater(result.result, 0.)
            # self.assertEqual(int(result.extra_data["area_id"]), queries[idx].area_id)

    def test_predictAcceptTime(self):
        queries = []
        for i in list(area_id.id):
            queries.append(Params_accept(area_id=int(i), brand_id=random.choice([1,8]), user_id=100000157,
                                         extra_keys=["area_id"]))
        results = self.eta_thrift_handler.predictAcceptTime(queries)
        self.assertIsInstance(results, PredictionResult)
        for idx, result in enumerate(results.data):
            self.assertIsInstance(result.result, float)
            self.assertGreater(result.result, 0.)
            # self.assertEqual(int(result.extra_data["area_id"]), queries[idx].area_id)