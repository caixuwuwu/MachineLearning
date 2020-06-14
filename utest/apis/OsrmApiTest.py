#!/usr/bin/env python
# coding=utf-8
'''
@Description: 测试osrm客户端请求
@Author: Jack Zhou (jack@km-it.cn)
@LastEditors: Jack Zhou
@Date: 2019-04-09 12:25:44
@LastEditTime: 2019-04-09 16:06:42
'''

import json
import unittest

from apis.osrm_api_client import OsrmApiClient
from configs.conf import OSRM_API_DRIVING_ROUTE, OSRM_API_WALKING_ROUTE, ZONE


class OsrmApiClientTest(unittest.TestCase):

    def setUp(self):
        self.osrmClient = OsrmApiClient()
        self.DRIVING = "driving"
        self.WALKING = "walking"
        self.ZONE = ZONE

    # def test_get_driving_distance(self):
    #     result = self.osrmClient.get_distance(self.DRIVING, (114.1489332,22.3329575), (114.1418850000,22.3364740000), steps='true', geometries='geojson')
    #     result = json.loads(result)
    #
    #     geometry_points_count = len(result[0]['geometry']['coordinates'])
    #     self.assertEqual(geometry_points_count, 16)
    #
    #     legs_steps_count = len(result[0]['legs'][0]['steps'])
    #     self.assertEqual(legs_steps_count, 7)

    def test_check_zone(self):
        """测试地区osrm的可用性"""
        if self.ZONE == "hk":
            distance = self.osrmClient.get_distance(self.DRIVING, (114.1489332,22.3329575), (114.1418850000,22.3364740000), zone="/hk")
        elif self.ZONE == "sg":
            distance = self.osrmClient.get_distance(self.DRIVING, (103.8489532471,1.3801956299), (103.8563776016,1.3776643578),
                                         zone="/sg")
            self.assertGreaterEqual(distance, 0)
            distance = self.osrmClient.get_distance(self.DRIVING, (100.539574,13.724451), (100.530001,13.723246), zone="/th")
        else:
            distance = self.osrmClient.get_distance(self.DRIVING, (114.1489332,22.3329575), (114.1418850000,22.3364740000))
        self.assertIsInstance(distance, float)
        self.assertGreaterEqual(distance, 0)



if __name__ == "__main__":
    unittest.main()
