#!/usr/bin/python
# coding:utf-8

"""预测模块"""

import numpy as np
import pandas as pd
import xgboost as xgb

from helpers.learner import Model
from helpers.timer import timepiece
from client.api_client import ApiClient
from client.OsrmApi import OsrmApiClient
from configs.ConfManage import ConfManage
from helpers.parallel import multi_thread
from helpers.pickler import load_pickle_cache
from helpers.logger import Logger
from helpers.utils import *

logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))
client = ApiClient()
osrm_api_client = OsrmApiClient()


def get_pickle(estimator_name, target):
    """
    将preprocess生成的feature.pkl,estimator.pkl和process生成的mae.pkl打开
    :param estimator_name: "random_forest","xgb"
    :param target: "accept","showup",
    :return: feature,estimator,mae
    """
    pickle_prefix = "%s_%s" % (estimator_name, target)
    estimator = Model(estimator_name, target).load_model_cache(pickle_prefix, using_joblib=True)
    features = load_pickle_cache("%s_features" % pickle_prefix)
    return estimator, features


