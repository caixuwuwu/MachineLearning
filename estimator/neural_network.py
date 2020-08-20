#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 neural.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	caixuwu@outlook.com
# DESCRIPTION:
#   neural network by tensorflow and sklearn, only regression
# HISTORY:
# *************************************************************

import tensorflow as tf
from tensorflow.python.ops import math_ops
from tensorflow.python.keras.utils import losses_utils
from tensorflow.python.keras.losses import LossFunctionWrapper
from tensorflow.python.keras import backend as K
from tensorflow.python.keras import regularizers


class PrintDot(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs):
        print('.', end='')


class DMaeLoss(LossFunctionWrapper):

    def __init__(self, reduction=losses_utils.ReductionV2.AUTO, name='dmae_loss'):
        super(DMaeLoss, self).__init__(self.dmae_loss, name=name, reduction=reduction)

    def dmae_loss(self, y_true, y_pred, delta=1.5, slope=2.5):
        y_pred = math_ops.cast(y_pred, dtype=K.floatx())
        y_true = math_ops.cast(y_true, dtype=K.floatx())
        error = math_ops.subtract(y_true, y_pred)
        return math_ops.abs(
            math_ops.maximum(error, math_ops.subtract(math_ops.multiply(error, slope), delta * (slope - 1))))


class TFModel(object):

    def __init__(self, batch_size=1000, steps_per_epoch=None, shuffle_size=1000, epochs=100,
                 loss_class=tf.keras.losses.Hinge, activation="relu", dense_num_list=[10, 10]):
        self.BATCH_SIZE = batch_size
        self.EPOCHS = epochs
        self.STEPS_PER_EPOCH = steps_per_epoch
        self.SHUFFLE_SIZE = shuffle_size
        self.loss_class = loss_class
        self.ACTIVATION = activation
        self.dense_num_list = dense_num_list

    def get_optimizer(self, rate=0.003, decay_rate=1):
        lr_schedule = tf.keras.optimizers.schedules.InverseTimeDecay(
            rate,
            decay_steps=self.STEPS_PER_EPOCH * 100,
            decay_rate=decay_rate,
            staircase=False)

        return tf.keras.optimizers.Adam(lr_schedule)

    def kernel(self, train_columns_count):
        regression = tf.keras.Sequential([
            tf.keras.layers.Dense(self.dense_num_list[0], activation=self.ACTIVATION,
                                  input_shape=[train_columns_count, ]),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(self.dense_num_list[1],
                                  activation=self.ACTIVATION,
                                  regularizers=regularizers.L1L2(0.1, 0.1)),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(1, activation="linear")
        ])
        optimizer = self.get_optimizer()
        regression.compile(loss=self.loss_class(), optimizer=optimizer, metrics=['mae', 'mse'])
        return regression

    def fix(self, X, Y):
        self.STEPS_PER_EPOCH = len(X) // self.BATCH_SIZE if self.STEPS_PER_EPOCH is None else self.STEPS_PER_EPOCH
        dataset = tf.data.Dataset.from_tensor_slices((X, Y))
        dataset = dataset.shuffle(self.SHUFFLE_SIZE).repeat().batch(self.BATCH_SIZE)
        return self.kernel(len(X.columns)).fit(dataset, epochs=self.EPOCHS, steps_per_epoch=self.STEPS_PER_EPOCH,
                                               verbose=1, callbacks=[PrintDot()])


def gen_params(estimator, mode='optimal'):
    """Generate lists of parameters for Machine-Learning Algorithms"""
    parameters = {}
    parameters['mlp'] = {
        'basic': dict(
            activation=['relu'],
            solver=['adam'],
            alpha=[0.0001],
            batch_size=['auto'],
            learning_rate=['constant'],
            learning_rate_init=[0.001],
            power_t=[0.5],
            max_iter=[200]
        ),
        'everything': dict(
            activation=['identity', 'logistic', 'tanh', 'relu'],
            solver=['lbfgs', 'sgd', 'adam'],
            alpha=[0.1, 0.001, 0.0001, 0.00001],
            batch_size=['auto'],
            learning_rate=['constant', 'invscaling', 'adaptive'],
            learning_rate_init=[0.1, 0.001, 0.0001, 0.00001],
            power_t=[0.5],
            max_iter=[200]
        ),
        'trial_and_error': dict(
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
    return parameters[estimator][mode]
