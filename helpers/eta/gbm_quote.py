# coding: utf-8

from helpers.eta.base import Base
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd


class GbmQuote(Base):
    estimator = "gbm"

    target = "model"

    below_loss_margin = 7.5

    over_loss_margin = 10

    limit_loss_N = 10

    features = []

    @staticmethod
    def clear_outliers(data, column, n):
        """
        用于计算IQR值，用于过滤异常值
        :param data: 数据集
        :param column: target值
        :param n: 权重
        :return: 最低，最高值
        """
        up_25 = round(data[column].quantile(.25), 2)
        up_50 = round(data[column].quantile(.50), 2)
        up_75 = round(data[column].quantile(.75), 2)
        IQR = up_75 - up_25
        upper = round(up_50 + n * IQR, 0)
        lower = round(up_50 - n * IQR, 0)
        return lower, upper

    def filter_data(self, data, **kwargs):
        return data
