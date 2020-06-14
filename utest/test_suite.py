#!/usr/bin/env python
# coding=utf-8
'''
@Description: 单元测试套件总入口
@Author: Jack Zhou (jack@km-it.cn)
@LastEditors: Jack Zhou
@Date: 2019-04-09 16:07:06
@LastEditTime: 2019-08-23 16:39:45
'''
from utest.apis.OsrmApiTest import OsrmApiClientTest
from utest.apis.HbaseApiTest import HbaseApiTest
from utest.helpers.CacheTest import CacheTest
from utest.helpers.PredictTest import PredictTest
from utest.helpers.EtaThriftHandlerTest import EtaThriftHandlerTest

import unittest as ut


if __name__ == "__main__":
    # unittest.main()
    suite=ut.TestSuite()
    suite.addTests(ut.makeSuite(OsrmApiClientTest))
    suite.addTests(ut.makeSuite(HbaseApiTest))
    suite.addTests(ut.makeSuite(EtaThriftHandlerTest))
    suite.addTests(ut.makeSuite(CacheTest))
    suite.addTests(ut.makeSuite(PredictTest))
    runner = ut.TextTestRunner(verbosity=1)
    runner.run(suite)