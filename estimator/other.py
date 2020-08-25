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


def gen_params(estimator, mode='basic'):
    """Generate lists of parameters for Machine-Learning Algorithms"""
    parameters = {}

    # K Neighbours Regressor
    parameters['k'] = {
        'basic': dict(
            n_neighbors=[5],
            weights=['uniform'],
            algorithm=['auto'],
            leaf_size=[30],
            p=[2],
            metric=['minkowski']
        ),
        'everything': dict(
            n_neighbors=range(3, 8),
            weights=['uniform', 'distance'],
            algorithm=['auto', 'ball_tree', 'kd_tree', 'brute'],
            leaf_size=range(30, 35),
            p=range(2, 6),
            metric=['minkowski']
        ),
        'trial_and_error': dict(
            n_neighbors=range(3, 8),
            weights=['uniform', 'distance'],
            algorithm=['auto', 'ball_tree', 'kd_tree', 'brute'],
            leaf_size=range(30, 35),
            p=range(2, 6),
            metric=['minkowski']
        ),
        'optimal': dict(
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
        'basic': dict(
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
        'everything': dict(
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

    """line regress"""
    parameters['lrg'] = {
        'accept': dict(),
        'quote': dict()
    }

    """SVN"""
    parameters['SVR'] = {
        'optimal': dict(
            kernel=['rbf'],
            C=1.0,
            gamma=0.1
        )
    }
    return parameters[estimator][mode]
