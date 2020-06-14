# coding: utf-8

from helpers.eta.base import Base
from helpers.pickler import load_pickle
from helpers.logger import Logger
from configs import conf
import pandas as pd

logger = Logger.get_instance(conf.LOG_CRON_NAME)


class XgbModel(Base):
    estimator = 'xgb'

    target = 'model'

    below_loss_margin = 2

    over_loss_margin = 5
    limit_loss_N = float(conf.MODEL_N_PERCENT)

    features = []

    def etl(self, data):
        return data

    def filter_data(self, data, *args, **kwargs):
        return data

    def amend_time(self, test_data=None):
        return test_data

    def features_select(self, *extra_features):
        """split dataset to process"""
        return self.features + list(extra_features)

    def features_savedb(self, *extra_features):
        target_features = self.features + list(extra_features)
        return list(set(target_features))
