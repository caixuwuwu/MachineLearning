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
from itertools import chain
import logging
from sklearn.model_selection import GridSearchCV
from helpers.logger import Logger
from configs.ConfManage import ConfManage
from helpers.pickler import save_pickle, load_pickle
from helpers.cache import Cache
import xgboost as xgb


def gen_params(estimator, mode='basic'):
    """Generate lists of parameters for Machine-Learning Algorithms"""
    parameters = {}

    # Ada Regressor
    parameters['ada'] = {
        'basic': dict(learning_rate=[1], loss=['linear'], n_estimators=[50]),
        'everything': dict( \
            learning_rate=range(1, 7),
            loss=['linear', 'square', 'exponential'],
            n_estimators=range(50, 201, 50)
        ),
        'trial_and_error': dict( \
            learning_rate=[2],
            loss=['linear', 'square', 'exponential'],
            n_estimators=chain([400, 800], range(950, 1201, 50))
        ),
        'optimal': dict( \
            learning_rate=[2],
            loss=['square'],
            n_estimators=[150, 400, 800]
        )
    }

    # Decision Tree Regressor
    parameters['decision_tree'] = {
        'basic': dict( \
            criterion=['gini'],
            max_features=['sqrt'],
            splitter=['best'],
            min_samples_split=range(2, 6),
            max_depth=range(1, 11)
        ),
        'everything': dict( \
            criterion=['gini', 'entropy'],
            max_features=['sqrt', 'log2'],
            splitter=['best', 'random'],
            min_samples_split=range(2, 21),
            max_depth=range(2, 21)
        ),
        'trial_and_error': dict( \
            criterion=['gini'],  # gini | entropy
            max_features=['sqrt'],  # sqrt | log2
            splitter=['best'],  # best | random
            min_samples_split=range(101, 120),
            max_depth=range(39, 42)
        ),
        'optimal': dict( \
            criterion=['entropy'],
            max_features=['sqrt'],
            splitter=['best'],
            min_samples_split=[16],
            max_depth=[2]
        )
    }

    # Extra Trees Regressor
    parameters['extra_trees'] = {
        'basic': dict( \
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[2],
            min_samples_leaf=[1],
            n_estimators=[10],
        ),
        'everything': dict( \
            criterion=['mse', 'mae'],
            max_features=['auto', 'sqrt', 'log2'],
            min_samples_split=range(2, 11),
            min_samples_leaf=range(1, 11),
            n_estimators=range(10, 21)
        ),
        'trial_and_error': dict( \
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[2],
            min_samples_leaf=[8],
            n_estimators=[26, 31, 48, 56, 64, 89]
        ),
        'optimal': dict( \
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[2],
            min_samples_leaf=[8],
            n_estimators=[89]
        )
    }

    # Gradient Boosting Regressor
    parameters['gradient_boost'] = {
        'basic': dict( \
            criterion=['friedman_mse', 'mse'],
            loss=['ls', 'lad', 'huber', 'quantile'],
            learning_rate=[0.1, 0.01],
            n_estimators=[100, 200, 300, 400],
            min_samples_split=range(2, 5),
            min_samples_leaf=range(1, 5)
        ),
        'everything': dict( \
            criterion=['friedman_mse', 'mse', 'mae'],
            loss=['ls', 'lad', 'huber', 'quantile'],
            learning_rate=[0.1, 0.01, 0.001, 0.0001, 0.00001],
            n_estimators=[100, 150, 200, 250, 300],
            min_samples_split=range(2, 11),
            min_samples_leaf=range(1, 11)
        ),
        'trial_and_error': dict( \
            criterion=['friedman_mse'],
            loss=['huber'],
            learning_rate=[0.1],
            n_estimators=[800, 850],
            min_samples_split=range(9, 12),
            min_samples_leaf=range(5, 8)
        ),
        'optimal': dict( \
            criterion=['friedman_mse'],
            loss=['huber'],
            learning_rate=[0.1],
            n_estimators=[800],
            min_samples_split=[9],
            min_samples_leaf=[5]
        )
    }

    # Gradient Boosting Classifications
    parameters['gradient_classif'] = {
        'basic': dict( \
            criterion=['friedman_mse', 'mse', 'mae'],
            loss=['deviance', 'exponential'],
            learning_rate=[0.1, 0.01, 0.001],
            max_depth=range(3, 6),
            min_samples_split=range(2, 5),
            min_samples_leaf=range(1, 5),
            n_estimators=[100, 150, 200],
        ),
        'everything': dict( \
            criterion=['friedman_mse', 'mse', 'mae'],
            loss=['deviance', 'exponential'],
            learning_rate=[0.1, 0.01, 0.001, 0.0001, 0.00001],
            max_depth=range(3, 6),
            min_samples_split=range(2, 11),
            min_samples_leaf=range(1, 11),
            n_estimators=[100, 150, 200, 250, 300],
        ),
        'trial_and_error': dict( \
            criterion=['friedman_mse', 'mse', 'mae'],
            loss=['deviance', 'exponential'],
            learning_rate=[0.1, 0.01, 0.001, 0.0001, 0.00001],
            max_depth=range(3, 6),
            min_samples_split=range(2, 11),
            min_samples_leaf=range(1, 11),
            n_estimators=[100, 150, 200, 250, 300]
        ),
        'optimal': None  # TODO
    }

    # Isolation Forest Regressor
    parameters['isolation'] = {
        'basic': dict( \
            n_estimators=[100],
            max_samples=['auto'],
            contamination=[0.1],
            max_features=[1.0],
            bootstrap=[False]
        ),
        'everything': dict( \
            n_estimators=[100],
            max_samples=['auto'],
            contamination=[0., 0.1, 0.2, 0.3, 0.4, 0.5],
            max_features=[1.0],
            bootstrap=[False, True]
        ),
        'trial_and_error': dict( \
            n_estimators=[100, 200, 300, 400, 500],
            max_samples=['auto'],
            contamination=[0.],
            max_features=[1.0],
            bootstrap=[True]
        ),
        'optimal': None  # TODO
    }

    # K Neighbours Regressor
    parameters['k'] = {
        'basic': dict( \
            n_neighbors=[5],
            weights=['uniform'],
            algorithm=['auto'],
            leaf_size=[30],
            p=[2],
            metric=['minkowski']
        ),
        'everything': dict( \
            n_neighbors=range(3, 8),
            weights=['uniform', 'distance'],
            algorithm=['auto', 'ball_tree', 'kd_tree', 'brute'],
            leaf_size=range(30, 35),
            p=range(2, 6),
            metric=['minkowski']
        ),
        'trial_and_error': dict( \
            n_neighbors=range(3, 8),
            weights=['uniform', 'distance'],
            algorithm=['auto', 'ball_tree', 'kd_tree', 'brute'],
            leaf_size=range(30, 35),
            p=range(2, 6),
            metric=['minkowski']
        ),
        'optimal': dict( \
            n_neighbors=[3],
            weights=['uniform'],
            algorithm=['auto'],
            leaf_size=[30],
            p=[2],
            metric=['minkowski']
        )
    }

    # Logistic Regression
    parameters['logistic'] = {
        'basic': dict( \
            penalty=['l2'],
            dual=[False],
            tol=[0.0001],
            C=[1.0],
            fit_intercept=[True],
            intercept_scaling=[1.],
            class_weight=['balanced'],
            solver=['liblinear'],
            max_iter=[100],
            multi_class=['ovr', 'multinomial']
        ),
        'everything': dict( \
            penalty=['l1', 'l2'],
            dual=[True, False],
            tol=[0.01, 0.001, 0.0001],
            C=[1.0, 1.1, 1.2],
            fit_intercept=[True, False],
            intercept_scaling=[1., 1.1, 1.2, 1.3],
            class_weight=['balanced'],
            solver=['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
            max_iter=range(100, 700, 100),
            multi_class=['ovr', 'multinomial']
        ),
        'trial_and_error': None,  # TODO
        'optimal': None,  # TODO
    }
    parameters['lrg'] = {
        'accept': dict(),
        'quote': dict()
    }
    parameters['mlp'] = {
        'basic': dict( \
            activation=['relu'],
            solver=['adam'],
            alpha=[0.0001],
            batch_size=['auto'],
            learning_rate=['constant'],
            learning_rate_init=[0.001],
            power_t=[0.5],
            max_iter=[200]
        ),
        'everything': dict( \
            activation=['identity', 'logistic', 'tanh', 'relu'],
            solver=['lbfgs', 'sgd', 'adam'],
            alpha=[0.1, 0.001, 0.0001, 0.00001],
            batch_size=['auto'],
            learning_rate=['constant', 'invscaling', 'adaptive'],
            learning_rate_init=[0.1, 0.001, 0.0001, 0.00001],
            power_t=[0.5],
            max_iter=[200]
        ),
        'trial_and_error': dict( \
            activation=['logistic'],
            solver=['adam'],
            alpha=[0.0001],
            batch_size=['auto'],
            learning_rate=['adaptive'],
            learning_rate_init=[0.001],
            power_t=[0.5],
            max_iter=[200]
        ),
        'optimal': None  # TODO
    }

    # Random Forest Regressor
    parameters['random_forest'] = {
        'basic': dict( \
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[2],
            n_estimators=[10]  # Number of Trees in the forest
        ),
        'everything': dict( \
            criterion=['mse', 'mae'],
            max_features=['auto', 'sqrt', 'log2'],
            min_samples_split=range(2, 11),
            n_estimators=range(10, 21)
        ),
        'trial_and_error': dict( \
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[16],
            n_estimators=[76, 85, 114, 170, 187, 207, 367, 577]
        ),
        'optimal': dict( \
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[16],
            n_estimators=[577]
        )
    }

    # Random Forest Classifier
    parameters['random_classif'] = {
        'basic': dict( \
            criterion=['gini'],
            max_features=['auto'],
            min_samples_split=[2],
            n_estimators=[10],  # Number of Trees in the forest
            min_samples_leaf=[1, 2]
        ),
        'everything': dict( \
            criterion=['gini', 'entropy'],
            max_features=['auto', 'sqrt', 'log2'],
            min_samples_split=range(2, 11),
            n_estimators=range(10, 21),
            min_samples_leaf=range(1, 11)
        ),
        'trial_and_error': dict( \
            criterion=['entropy'],
            max_features=['auto'],
            min_samples_split=[16],
            n_estimators=[11, 14, 17, 22],
            min_samples_leaf=[4, 6, 9]
        ),
        'optimal': dict( \
            criterion=['entropy'],
            max_features=['auto'],
            min_samples_split=[16],
            n_estimators=[22],
            min_samples_leaf=[4]
        )
    }

    parameters['SVR'] = {
        'optimal': dict( \
            kernel=['rbf'],
            C=1.0,
            gamma=0.1
        )
    }
    # SGD
    parameters['sgd'] = {
        'basic': dict( \
            loss=['log', 'squared_hinge', 'perceptron'],
            alpha=[0.01, 0.001, 0.0001],
            max_iter=range(1, 20)
        ),
        'everything': dict( \
            loss=['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'],
            alpha=[0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001],
            max_iter=range(1, 1001)
        ),
        'optimal': None  # TODO
    }

    # Extreme Gradient Boosting Regressor (XGBoost)
    parameters['xgb'] = {
        'everything': dict( \
            booster=['gbtree', 'gblinear', 'dart'],
            colsample_bytree=[0.9, 1, 1.1, 1.2],
            gamma=[0, 10, 100],  # range: (0, infinity)
            learning_rate=[0.03, 0.05],  # range: (0, 1)
            n_estimators=range(0, 2001, 50),
            max_delta_step=[0, 0.5],
            max_depth=[6, 8, 10],
            min_child_weight=[1, 5, 10],
            silent=[True],
            subsample=[0.7, 1],  # range: (0, 1)
            reg_alpha=[_ / 10. for _ in range(1, 30)],  # L1 regularization term on weights
            reg_lambda=[_ / 10. for _ in range(1, 30)],  # L2 regularization term on weights
            tree_method=['auto', 'exact', 'approx', 'hist', 'gpu_exact', 'gpu_hist']
        ),
        'optimal': dict( \
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[0.8],
            gamma=[0.7],
            learning_rate=[0.03],
            n_estimators=[450],
            max_delta_step=[0],
            max_depth=[11],
            min_child_weight=[9],
            silent=[True],
            subsample=[0.9],
            reg_alpha=[2.1],
            reg_lambda=[10]
        ),
        'showup': dict( \
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[0.8],
            gamma=[0.7],
            learning_rate=[0.03],
            n_estimators=[450],
            max_delta_step=[0],
            max_depth=[11],
            min_child_weight=[9],
            silent=[True],
            subsample=[0.9],
            reg_alpha=[2.1],
            reg_lambda=[10]
        ),
        'realtime_showup': dict( \
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[0.8],
            gamma=[0.6],
            learning_rate=[0.03],
            n_estimators=[450],
            max_delta_step=[0],
            max_depth=[14],
            min_child_weight=[12],
            silent=[True],
            subsample=[1.0],
            reg_alpha=[3.9],
            reg_lambda=[9.3]
        ),
        'accept': dict(
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[.9],
            gamma=[1],
            learning_rate=[0.03],
            n_estimators=[150],
            max_delta_step=[0],
            max_depth=[11],
            min_child_weight=[5],
            silent=[True],
            subsample=[.7],
            reg_alpha=[2.1],
            reg_lambda=[60],
        ),
        'work': dict(
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[.8],
            gamma=[.8],
            learning_rate=[0.08],
            n_estimators=[500],
            max_delta_step=[0],
            max_depth=[6],
            min_child_weight=[5],
            silent=[True],
            subsample=[.8],
            reg_alpha=[10],
            reg_lambda=[12],
        ),
        'realtime_work': dict(
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[.8],
            gamma=[0],
            learning_rate=[0.075],
            n_estimators=[500],
            max_delta_step=[0],
            max_depth=[8],
            min_child_weight=[3],
            silent=[True],
            subsample=[.7],
            reg_alpha=[10],
            reg_lambda=[12],
        ),
        'quote': dict(
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[.9],
            gamma=[.8],
            learning_rate=[0.03],
            n_estimators=[250],
            max_delta_step=[0],
            max_depth=[5],
            min_child_weight=[5],
            silent=[True],
            subsample=[.9],
            reg_alpha=[6],
            reg_lambda=[90],
        ),
        'delivery': dict(
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[.9],
            gamma=[.8],
            learning_rate=[0.05],
            n_estimators=[400],
            max_delta_step=[0],
            max_depth=[8],
            min_child_weight=[8],
            silent=[True],
            subsample=[.9],
            reg_alpha=[15],
            reg_lambda=[6],
        ),
    }
    parameters['gbm'] = {
        'basic': dict( \
            booster=['gbtree'],
            colsample_bytree=[0.9],
            learning_rate=[0.01, 0.05],
            n_estimators=[100, 300],
            max_delta_step=[0],  # range: (0, infinity), defaults: 0
            max_depth=[6],  # range: (0, infinity), defaults: 6
            min_child_weight=[1, 5, 10],
            silent=[True],
            subsample=[0.7],  # range: (0, 1)
            reg_alpha=[0],  # L1 regularization term on weights
            reg_lambda=[1]  # L2 regularization term on weights
        ),
        'optimal': dict( \
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[0.8],
            gamma=[0.7],
            learning_rate=[0.03],
            n_estimators=[450],
            max_delta_step=[0],
            max_depth=[11],
            min_child_weight=[9],
            silent=[True],
            subsample=[0.9],
            reg_alpha=[2.1],
            reg_lambda=[10]
        ),
        'showup': dict( \
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[0.8],
            gamma=[0.7],
            learning_rate=[0.03],
            n_estimators=[450],
            max_delta_step=[0],
            max_depth=[11],
            min_child_weight=[9],
            silent=[True],
            subsample=[0.9],
            reg_alpha=[2.1],
            reg_lambda=[10]
        ),
        'accept': dict(
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[.9],
            gamma=[.3],
            learning_rate=[0.03],
            n_estimators=[150],
            max_delta_step=[0],
            max_depth=[8],
            min_child_weight=[7],
            silent=[True],
            subsample=[.9],
            reg_alpha=[8],
            reg_lambda=[30],
        ),
        'work': dict(
            booster=['gbtree'],
            colsample_bylevel=[0.8],
            colsample_bytree=[.8],
            gamma=[.8],
            learning_rate=[0.08],
            n_estimators=[500],
            max_delta_step=[0],
            max_depth=[6],
            min_child_weight=[5],
            silent=[True],
            subsample=[.8],
            reg_alpha=[10],
            reg_lambda=[12],
        ),
        'quote': dict(
            boosting_type=['gbdt'],
            num_leaves=[50],
            max_depth=[6],
            learning_rate=[0.03],
            n_estimators=[250],
            min_split_gain=[0.],
            min_child_weight=[5],
            min_child_samples=[6],
            subsample=[.9],
            # subsample_freq = [],
            colsample_bytree=[0.9],
            reg_alpha=[6],
            reg_lambda=[90],
            silent=[True]
        ),
        'delivery': dict(
            boosting_type=['gbtree'],
            num_leaves=[8],
            max_depth=[5],
            learning_rate=[0.03],
            n_estimators=[250],
            min_split_gain=[0.],
            min_child_weight=[5],
            min_child_samples=[6],
            subsample=[.9],
            colsample_bytree=[0.9],
            reg_alpha=[6],
            reg_lambda=[90],
            silent=[True]
        ),
    }
    return parameters[estimator][mode]


def get_estimator(estimator_name):
    if estimator_name == 'ada':
        from sklearn.ensemble import AdaBoostRegressor
        return AdaBoostRegressor()
    elif estimator_name == 'ada_classif':
        from sklearn.ensemble import AdaBoostClassifier
        return AdaBoostClassifier()
    elif estimator_name == 'decision_tree':
        from sklearn.tree import DecisionTreeClassifier
        return DecisionTreeClassifier()
    elif estimator_name == 'extra_trees':
        from sklearn.ensemble import ExtraTreesRegressor
        return ExtraTreesRegressor()
    elif estimator_name == 'gradient_boost':
        from sklearn.ensemble import GradientBoostingRegressor
        return GradientBoostingRegressor()
    elif estimator_name == 'gradient_classif':
        from sklearn.ensemble import GradientBoostingClassifier
        return GradientBoostingClassifier()
    elif estimator_name == 'isolation':
        from sklearn.ensemble import IsolationForest
        return IsolationForest()
    elif estimator_name == 'k':
        from sklearn.neighbors import KNeighborsClassifier
        return KNeighborsClassifier()
    elif estimator_name == 'logistic':
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression()
    elif estimator_name == 'lrg':
        from sklearn.linear_model import LinearRegression
        return LinearRegression()
    elif estimator_name == 'mlp':
        from sklearn.neural_network import MLPClassifier
        return MLPClassifier()
    elif estimator_name == 'random_forest':
        from sklearn.ensemble import RandomForestRegressor
        return RandomForestRegressor()
    elif estimator_name == 'random_classif':
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier()
    elif estimator_name == 'sgd':
        from sklearn.linear_model import SGDClassifier
        return SGDClassifier()
    elif estimator_name == 'xgb':
        from xgboost import XGBRegressor
        return XGBRegressor()
    elif estimator_name == 'svm':
        from sklearn.svm.classes import SVR
        return SVR()
    elif estimator_name == 'GaussianNB':
        from sklearn.naive_bayes import GaussianNB
        return GaussianNB()
    elif estimator_name == 'gbm':
        from lightgbm import LGBMRegressor
        return LGBMRegressor()


logger = Logger.get_instance(ConfManage.getString("LOG_CRON_NAME"))

# 本框架可调用的算法模型：
estimators = ['ada', 'ada_classif', 'decision_tree', 'extra_trees', 'gradient_boost', 'gradient_classif', 'huber',
              'gbm',
              'isolation', 'k', 'logistic', 'mlp', 'random_forest', 'random_classif', 'sgd', 'theilsen', 'xgb', 'svr',
              'lrg']


class Model:
    def __init__(self, estimator_name, target, mode="optimal"):
        if estimator_name not in estimators:
            raise ValueError('Argument `estimator` given does not exist')
        self.cv_round = 5 if mode == 'optimal' else 3
        self.estimator_name = estimator_name
        self.estimator = get_estimator(self.estimator_name)
        self.parameters = gen_params(estimator=self.estimator_name, mode=mode)
        self.target = target
        self.model = None

        self.cache = Cache.get_instance()

    def train(self, x_train, y_train, model=None):
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
            if model is not None:
                self.parameters["n_estimators"] = 50

            self.model = xgb.XGBRegressor(kwargs=self.parameters).fit(x_train, y_train, xgb_model=model)
        else:
            verbose_level = ConfManage.getInt("LOG_LEVEL") if ConfManage.getInt("LOG_LEVEL") == logging.DEBUG else 0
            gsv = GridSearchCV(estimator=self.estimator, param_grid=self.parameters, \
                               scoring='neg_mean_squared_error', verbose=verbose_level, n_jobs=jobs,
                               cv=self.cv_round)  # ‘neg_mean_squared_error’,neg_mean_absolute_error
            gsv.fit(x_train, y_train)
            self.model = gsv.best_estimator_
        # return self.model

    def cv(self, x_train, y_train, model=None):
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
            bst = xgb.cv(self.parameters, dtrain, nfold=self.cv_round, metrics="rmse")
        else:

            verbose_level = ConfManage.getInt("LOG_LEVEL") if ConfManage.getInt("LOG_LEVEL") == logging.DEBUG else 0
            gsv = GridSearchCV(estimator=self.estimator, param_grid=self.parameters, \
                               scoring='neg_mean_squared_error', verbose=verbose_level, n_jobs=jobs,
                               cv=self.cv_round)  # ‘neg_mean_squared_error’,neg_mean_absolute_error
            gsv.fit(x_train, y_train)
            best_model = gsv.best_estimator_

    def save_mode(self, realtime=None, postfix=None):
        if self.model is None:
            raise Exception("1602:Not model in Model, please use train member to produce model")
        else:
            if realtime is not None:
                estmator_key = '%s_%s_%s' % (self.estimator_name, realtime, self.target)
            else:
                estmator_key = '%s_%s' % (self.estimator_name, self.target)
            try:
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
            if name[:3] == "xgb":
                path = "pickles/{app_mode}-{zone}-{estmator_key}".format(app_mode=ConfManage.getString("APP_MODE"),
                                                                         zone=ConfManage.getString("ZONE"),
                                                                         estmator_key=name)
                ret = xgb.Booster(model_file=path)
        else:
            ret = load_pickle(name, using_joblib)
        if ret is not None:
            cached = self.cache.set(cache_key, ret, ConfManage.getInt("PICKLE_CACHE_EXPIRE"))
            logger.debug('load_pickle_cache, set cache, cache_key={}, status={}'.format(cache_key, cached))
        else:
            logger.debug('load_pickle_cache, fetch from cache, cache_key={}'.format(cache_key))
        return ret
