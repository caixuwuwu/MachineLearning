#!/usr/bin/python
# coding:utf-8

"""预测模块"""

from estimator.learner import Model
from client.api_client import ApiClient
from client.OsrmApi import OsrmApi
from configs.ConfManage import ConfManage
from tools.pickler import load_pickle_cache
from tools.logger import Logger

logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))
client = ApiClient()
osrm_api_client = OsrmApi()


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


