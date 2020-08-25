#!/usr/bin/env python
# coding=utf-8
'''
@Description: 单元测试套件总入口
@Author:
@Date: 2020-04-20 16:07:06
'''
from utest.helpers.PredictTest import PredictTest
from utest.CollectTest import CollectTest
import unittest as ut


if __name__ == "__main__":
    # unittest.main()
    suite=ut.TestSuite()
    suite.addTests(ut.makeSuite(CollectTest))
    suite.addTests(ut.makeSuite(PredictTest))
    runner = ut.TextTestRunner(verbosity=1)
    runner.run(suite)