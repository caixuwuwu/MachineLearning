#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 learner.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	caixuwu@outlook.com 
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module for generating needed Machine-Learning Algorithms and 
appropriate field-tested parameters"""
import logging
from sklearn.model_selection import GridSearchCV
from helpers.logger import Logger
from configs.ConfManage import ConfManage
from helpers.pickler import save_pickle, load_pickle
from helpers.cache import Cache
import xgboost as xgb
import tensorflow as tf


def get_estimator(estimator_name):
    if estimator_name == 'ada':
        from sklearn.ensemble import AdaBoostRegressor
        return AdaBoostRegressor
    elif estimator_name == 'ada_classif':
        from sklearn.ensemble import AdaBoostClassifier
        return AdaBoostClassifier
    elif estimator_name == 'decision_tree':
        from sklearn.tree import DecisionTreeClassifier
        return DecisionTreeClassifier
    elif estimator_name == 'extra_trees':
        from sklearn.ensemble import ExtraTreesRegressor
        return ExtraTreesRegressor
    elif estimator_name == 'gradient_boost':
        from sklearn.ensemble import GradientBoostingRegressor
        return GradientBoostingRegressor
    elif estimator_name == 'gradient_classif':
        from sklearn.ensemble import GradientBoostingClassifier
        return GradientBoostingClassifier
    elif estimator_name == 'isolation':
        from sklearn.ensemble import IsolationForest
        return IsolationForest
    elif estimator_name == 'k':
        from sklearn.neighbors import KNeighborsClassifier
        return KNeighborsClassifier
    elif estimator_name == 'logistic':
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression
    elif estimator_name == 'lrg':
        from sklearn.linear_model import LinearRegression
        return LinearRegression
    elif estimator_name == 'mlp':
        from sklearn.neural_network import MLPClassifier
        return MLPClassifier
    elif estimator_name == 'random_forest':
        from sklearn.ensemble import RandomForestRegressor
        return RandomForestRegressor
    elif estimator_name == 'random_classif':
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier
    elif estimator_name == 'sgd':
        from sklearn.linear_model import SGDClassifier
        return SGDClassifier
    elif estimator_name == 'xgb':
        from xgboost import XGBRegressor
        return XGBRegressor
    elif estimator_name == 'svm':
        from sklearn.svm.classes import SVR
        return SVR
    elif estimator_name == 'GaussianNB':
        from sklearn.naive_bayes import GaussianNB
        return GaussianNB
    elif estimator_name == 'gbm':
        from lightgbm import LGBMRegressor
        return LGBMRegressor
    elif estimator_name == "tf":
        from estimator.neural_network import TFModel
        return TFModel


logger = Logger.get_instance(ConfManage.getString("LOG_CRON_NAME"))

# 本框架可调用的算法模型：
estimators = ['ada', 'ada_classif', 'decision_tree', 'extra_trees', 'gradient_boost', 'gradient_classif', 'huber',
              'gbm',
              'isolation', 'k', 'logistic', 'mlp', 'random_forest', 'random_classif', 'sgd', 'theilsen', 'xgb', 'svr',
              'lrg']


class Model:
    """模型调用模块 todo: lsgb未实现"""
    def __init__(self, estimator_name, target, estimator_param):
        if estimator_name not in estimators:
            raise ValueError('Argument `estimator` given does not exist')
        self.estimator_name = estimator_name
        self.estimator = get_estimator(self.estimator_name)
        self.parameters = estimator_param
        self.target = target
        self.model = None
        self.cache = Cache.get_instance()

    def train(self, x_train, y_train, cv_round=5, model=None):
        """
        Args:
            x_train(DataFrame): 训练集
            y_train(DataFrame): 验证集
            model (str): 用于增量训练，原模型路径（数据量不大慎用，注意增加tree的数量对模型的影响）
        :return:
        """
        jobs = ConfManage.getInt("PARALLEL_NUM")

        if self.estimator_name == "xgb":
            self.parameters["n_jobs"] = jobs
            if model is not None:
                self.parameters["n_estimators"] = 50
            self.model = self.estimator(**self.parameters).fit(x_train, y_train, xgb_model=model)
        else:
            self.model = self.estimator(**self.parameters).fit(x_train, y_train)
        # return self.model

    def cv(self, x_train, y_train, model=None, cv_round=5):
        """
        Args:
            x_train(DataFrame): 训练集
            y_train(DataFrame): 验证集
            model (str): 用于增量训练，原模型路径（数据量不大慎用，注意增加tree的数量对模型的影响）
        :return:
        """
        jobs = ConfManage.getInt("PARALLEL_NUM")

        if self.estimator_name == "xgb":
            import xgboost as xgb
            self.parameters["n_jobs"] = jobs
            dtrain = xgb.DMatrix(x_train, y_train)
            history = xgb.cv(self.parameters, dtrain, nfold=cv_round, metrics="rmse")
        else:
            verbose_level = ConfManage.getInt("LOG_LEVEL") if ConfManage.getInt("LOG_LEVEL") == logging.DEBUG else 0
            gsv = GridSearchCV(estimator=self.estimator, param_grid=self.parameters,
                               scoring='neg_mean_squared_error', verbose=verbose_level, n_jobs=jobs,
                               cv=cv_round)  # ‘neg_mean_squared_error’,neg_mean_absolute_error
            gsv.fit(x_train, y_train)
            history = gsv.cv_results_
        return history

    def save_mode(self, realtime=None, postfix=None):
        if self.model is None:
            raise Exception("1602:Not model in Model, please use train member to produce model")
        else:
            if realtime is not None:
                estmator_key = '%s_%s_%s' % (self.estimator_name, realtime, self.target)
            else:
                estmator_key = '%s_%s' % (self.estimator_name, self.target)
            try:
                if self.estimator_name == "tf":
                    self.model.save("pickles/{app_mode}-{zone}-{estmator_key}".format(
                        app_mode=ConfManage.getString("APP_MODE"),
                        zone=ConfManage.getString("ZONE"),
                        estmator_key=estmator_key))
                else:
                    self.model.save_model(
                        "pickles/{app_mode}-{zone}-{estmator_key}".format(app_mode=ConfManage.getString("APP_MODE"),
                                                                      zone=ConfManage.getString("ZONE"),
                                                                      estmator_key=estmator_key))
            except AttributeError:  # 非xgboost保存为pkl文件
                save_pickle(self.model, estmator_key + postfix, using_joblib=True)
            logger.info('Estmator Key: {}'.format(estmator_key))

    def load_model_cache(self, name='undefined', using_joblib=False):

        cache_key = 'pickle_cache_{}'.format(name)
        ret = self.cache.get(cache_key)
        if ret is None:
            logger.debug('load_pickle_cache, fetch from raw pickle')
            path = "pickles/{app_mode}-{zone}-{estmator_key}".format(app_mode=ConfManage.getString("APP_MODE"),
                                                                     zone=ConfManage.getString("ZONE"),
                                                                     estmator_key=name)
            if name[:3] == "xgb":
                ret = xgb.Booster(model_file=path)
            elif name[:2] == "tf":
                ret = tf.keras.models.load_model(path, compile=False)
                ret.compile(optimizer=self.estimator().get_optimizer(), loss=self.estimator().loss_class,  # todo:self.estimator()未初始化设置
                            metrics=['mae', 'mse'])
        else:
            ret = load_pickle(name, using_joblib)
        if ret is not None:
            cached = self.cache.set(cache_key, ret, ConfManage.getInt("PICKLE_CACHE_EXPIRE"))
            logger.debug('load_pickle_cache, set cache, cache_key={}, status={}'.format(cache_key, cached))
        else:
            logger.debug('load_pickle_cache, fetch from cache, cache_key={}'.format(cache_key))
        return ret
