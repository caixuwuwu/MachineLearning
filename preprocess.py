#!/usr/bin/env python
# coding: utf-8
# VERSION: 	 1.0
# DESCRIPTION:
#   模型算法训练模块。
# *************************************************************
import argparse
import sys
import traceback
import arrow
from configs.ConfManage import ConfManage
from helpers.logger import Logger
from helpers.pickler import load_pickle
from helpers.timer import LOGGABLE_ARROW_FORMAT as loggable
from helpers.timer import get_run_time
import importlib
importlib.reload(sys)
logger = Logger.get_instance(ConfManage.getString("LOG_CRON_NAME"))

def preprocess(date, pickle, estimator, predict_target, holdout, mode, shift_days):
    data = load_pickle(pickle)
    try:
        run_time = get_run_time(date)
        logger.info('Run-Time: %s' % run_time.format(loggable))
        run_time = run_time.shift(days=shift_days).ceil('day').ceil('hour').ceil('minute').ceil('second')
        start_time = run_time.shift(days=-ConfManage.getInt("TRAINING_INTERVAL")).floor('day').floor('hour').floor('minute').floor('second')
        logger.info('Targeted Training Interval %d [%s - %s]' % \
                    (ConfManage.getInt("TRAINING_INTERVAL"), start_time.format(loggable), run_time.format(loggable)))
        logger.info('Preprocessing with Estimator %s (%s)' % (estimator, mode))
        # 导入eta类：
        module_tmp = importlib.import_module('helpers.eta.{}_{}'.format(estimator, predict_target))
        class_tmp = getattr(module_tmp, '{}{}'.format(estimator.capitalize(), predict_target.capitalize()))
        estimator_obj = class_tmp()

        # 数据处理
        data = estimator_obj.etl(data)
        # 去除异常值
        data = estimator_obj.filter_data(data)
        if data is not None and 'time' in data.columns:
            # 选取某段时间数据
            data = data.loc[(data.order_time > start_time) & (data.order_time < run_time)]
            order_times = data.order_time
            interval_count = len(order_times.apply(lambda order_time: order_time.date()).unique())
            logger.info('Available Training Interval %d/%d [%s - %s]' % (interval_count, ConfManage.getInt("TRAINING_INTERVAL"), \
                         order_times.min().format(loggable), order_times.max().format(loggable)))
            # 模型训练：
            estimator_obj.preprocess(data, mode, holdout)
            Logger.resource_checkpoint('post-preprocess')
        else:
            raise Exception("Data not yet obtained. Please run `python collect.py` first!")
    except (AttributeError, ValueError) as err:
        logger.error(err)
        logger.error('Trace: {}'.format(traceback.format_exc()))
    except KeyboardInterrupt:
        logger.info('Process manually interupted at %s' % arrow.now(tz=ConfManage.getString("ARROW_TIMEZONE")).format(loggable))
    logger.info('Releasing Logger...')
    # Logger.release_instance()
    return 0


if __name__ == '__main__':
    # 读取运行该程序时的参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', help='日期', type=str)
    parser.add_argument('-p', '--pickle', type=str, help='数据集的文件名.', default='data')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-o', '--optimal', help='指定获取算法的参数值', action='store_false', default=True)
    parser.add_argument('estimator', help='选择算法模型', nargs='?', type=str, default='xgb')
    parser.add_argument('predict_target', help='目标值', nargs='?', type=str, default='accept')
    parser.add_argument('--holdout', help='是否拆分3/7数据训练模型', action='store_true')  # True or Flase
    parser.add_argument("-s", "--shift_days", help="The last few days", type=int, default=-1)  # True or Flase
    args = parser.parse_args()
    date = args.date
    pickle = args.pickle
    optimal = args.optimal
    estimator = args.estimator
    predict_target = args.predict_target
    holdout = args.holdout
    shift_days = args.shift_days

    mode = predict_target if optimal else 'optimal'
    logger.info('Arguments: estimator=%s, predict-target=%s, mode=%s' % (estimator, predict_target, mode))
    logger.info('Environment-Configs: training-interval=%d' % (ConfManage.getInt("TRAINING_INTERVAL")))
    Logger.resource_checkpoint('post-argparse')

    preprocess(date, pickle, estimator, predict_target, holdout, mode, shift_days)
