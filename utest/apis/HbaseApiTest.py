#!/usr/bin/env python
# coding=utf-8
'''
@Description: 测试osrm客户端请求
@Author: Jack Zhou (jack@km-it.cn)
@LastEditors: Jack Zhou
@Date: 2019-04-09 12:25:44
@LastEditTime: 2019-04-09 16:06:42
'''
import unittest
import pandas as pd

from client.HBaseClient import HbaseClient


class HbaseApiTest(unittest.TestCase):

    def setUp(self):
        self.hbaseClient = HbaseClient()

    def test_getData(self):
        data = self.hbaseClient.get_data( table = "area",
                                          topic = "working_tasker_num",
                                          record_path = 'brand',
                                          meta = ['id', 'time', 'brand',
                                                  'non_brand_schedule_pickup_num',
                                                  'non_brand_schedule_delivery_num',
                                                  'non_brand_schedule_free_tasker_num'] )
        self.assertIsInstance(data, pd.DataFrame)
        self.assertGreaterEqual(len(data.columns.tolist()), 6)




if __name__ == "__main__":
    unittest.main()