#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 tree.py
# VERSION: 	 1.0
# CREATED: 	 2020-08-20 09:23
# AUTHOR: 	caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
from itertools import chain


def gen_params(estimator, mode='basic'):
    """Generate lists of parameters for Machine-Learning Algorithms"""
    parameters = {}

    # Ada Regressor
    parameters['ada'] = {
        'basic': dict(learning_rate=[1], loss=['linear'], n_estimators=[50]),
        'everything': dict(
            learning_rate=range(1, 7),
            loss=['linear', 'square', 'exponential'],
            n_estimators=range(50, 201, 50)
        ),
        'trial_and_error': dict(
            learning_rate=[2],
            loss=['linear', 'square', 'exponential'],
            n_estimators=chain([400, 800], range(950, 1201, 50))
        ),
        'optimal': dict(
            learning_rate=[2],
            loss=['square'],
            n_estimators=[150, 400, 800]
        )
    }

    # Decision Tree Regressor
    parameters['decision_tree'] = {
        'basic': dict(
            criterion=['gini'],
            max_features=['sqrt'],
            splitter=['best'],
            min_samples_split=range(2, 6),
            max_depth=range(1, 11)
        ),
        'everything': dict(
            criterion=['gini', 'entropy'],
            max_features=['sqrt', 'log2'],
            splitter=['best', 'random'],
            min_samples_split=range(2, 21),
            max_depth=range(2, 21)
        ),
        'trial_and_error': dict(
            criterion=['gini'],  # gini | entropy
            max_features=['sqrt'],  # sqrt | log2
            splitter=['best'],  # best | random
            min_samples_split=range(101, 120),
            max_depth=range(39, 42)
        ),
        'optimal': dict(
            criterion=['entropy'],
            max_features=['sqrt'],
            splitter=['best'],
            min_samples_split=[16],
            max_depth=[2]
        )
    }

    # Extra Trees Regressor
    parameters['extra_trees'] = {
        'basic': dict(
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[2],
            min_samples_leaf=[1],
            n_estimators=[10],
        ),
        'everything': dict(
            criterion=['mse', 'mae'],
            max_features=['auto', 'sqrt', 'log2'],
            min_samples_split=range(2, 11),
            min_samples_leaf=range(1, 11),
            n_estimators=range(10, 21)
        ),
        'trial_and_error': dict(
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[2],
            min_samples_leaf=[8],
            n_estimators=[26, 31, 48, 56, 64, 89]
        ),
        'optimal': dict(
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[2],
            min_samples_leaf=[8],
            n_estimators=[89]
        )
    }

    # Gradient Boosting Regressor
    parameters['gradient_boost'] = {
        'basic': dict(
            criterion=['friedman_mse', 'mse'],
            loss=['ls', 'lad', 'huber', 'quantile'],
            learning_rate=[0.1, 0.01],
            n_estimators=[100, 200, 300, 400],
            min_samples_split=range(2, 5),
            min_samples_leaf=range(1, 5)
        ),
        'everything': dict(
            criterion=['friedman_mse', 'mse', 'mae'],
            loss=['ls', 'lad', 'huber', 'quantile'],
            learning_rate=[0.1, 0.01, 0.001, 0.0001, 0.00001],
            n_estimators=[100, 150, 200, 250, 300],
            min_samples_split=range(2, 11),
            min_samples_leaf=range(1, 11)
        ),
        'trial_and_error': dict(
            criterion=['friedman_mse'],
            loss=['huber'],
            learning_rate=[0.1],
            n_estimators=[800, 850],
            min_samples_split=range(9, 12),
            min_samples_leaf=range(5, 8)
        ),
        'optimal': dict(
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
        'basic': dict(
            criterion=['friedman_mse', 'mse', 'mae'],
            loss=['deviance', 'exponential'],
            learning_rate=[0.1, 0.01, 0.001],
            max_depth=range(3, 6),
            min_samples_split=range(2, 5),
            min_samples_leaf=range(1, 5),
            n_estimators=[100, 150, 200],
        ),
        'everything': dict(
            criterion=['friedman_mse', 'mse', 'mae'],
            loss=['deviance', 'exponential'],
            learning_rate=[0.1, 0.01, 0.001, 0.0001, 0.00001],
            max_depth=range(3, 6),
            min_samples_split=range(2, 11),
            min_samples_leaf=range(1, 11),
            n_estimators=[100, 150, 200, 250, 300],
        ),
        'trial_and_error': dict(
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
        'basic': dict(
            n_estimators=[100],
            max_samples=['auto'],
            contamination=[0.1],
            max_features=[1.0],
            bootstrap=[False]
        ),
        'everything': dict(
            n_estimators=[100],
            max_samples=['auto'],
            contamination=[0., 0.1, 0.2, 0.3, 0.4, 0.5],
            max_features=[1.0],
            bootstrap=[False, True]
        ),
        'trial_and_error': dict(
            n_estimators=[100, 200, 300, 400, 500],
            max_samples=['auto'],
            contamination=[0.],
            max_features=[1.0],
            bootstrap=[True]
        ),
        'optimal': None  # TODO
    }

    # Random Forest Regressor
    parameters['random_forest'] = {
        'basic': dict(
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[2],
            n_estimators=[10]  # Number of Trees in the forest
        ),
        'everything': dict(
            criterion=['mse', 'mae'],
            max_features=['auto', 'sqrt', 'log2'],
            min_samples_split=range(2, 11),
            n_estimators=range(10, 21)
        ),
        'trial_and_error': dict(
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[16],
            n_estimators=[76, 85, 114, 170, 187, 207, 367, 577]
        ),
        'optimal': dict(
            criterion=['mse'],
            max_features=['auto'],
            min_samples_split=[16],
            n_estimators=[577]
        )
    }

    # Random Forest Classifier
    parameters['random_classif'] = {
        'basic': dict(
            criterion=['gini'],
            max_features=['auto'],
            min_samples_split=[2],
            n_estimators=[10],  # Number of Trees in the forest
            min_samples_leaf=[1, 2]
        ),
        'everything': dict(
            criterion=['gini', 'entropy'],
            max_features=['auto', 'sqrt', 'log2'],
            min_samples_split=range(2, 11),
            n_estimators=range(10, 21),
            min_samples_leaf=range(1, 11)
        ),
        'trial_and_error': dict(
            criterion=['entropy'],
            max_features=['auto'],
            min_samples_split=[16],
            n_estimators=[11, 14, 17, 22],
            min_samples_leaf=[4, 6, 9]
        ),
        'optimal': dict(
            criterion=['entropy'],
            max_features=['auto'],
            min_samples_split=[16],
            n_estimators=[22],
            min_samples_leaf=[4]
        )
    }

    # Extreme Gradient Boosting Regressor (XGBoost)
    parameters['xgb'] = {
        'everything': dict(
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
        'optimal': dict(
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
    }

    parameters['lgbm'] = {
        'basic': dict(
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
        'optimal': dict(
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
        )
    }

    # SGD
    parameters['sgd'] = {
        'basic': dict(
            loss=['log', 'squared_hinge', 'perceptron'],
            alpha=[0.01, 0.001, 0.0001],
            max_iter=range(1, 20)
        ),
        'everything': dict(
            loss=['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'],
            alpha=[0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001],
            max_iter=range(1, 1001)
        ),
        'optimal': None  # TODO
    }
