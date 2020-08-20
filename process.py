#!/usr/bin/env python
# coding: utf-8
# VERSION: 	 1.0
# DESCRIPTION:
#Launch main() to use parse arguments and use Trained Model to predict results on given date or current date then upload
# such results to BI Database
# HISTORY:
# *************************************************************
import argparse
import arrow
import sys
import traceback
import pandas as pd
from configs.ConfManage import ConfManage
from helpers.logger import Logger
from helpers.pickler import load_pickle, save_pickle

try:
    from xgboost.core import XGBoostError
except ModuleNotFoundError as e:
    print(e)
from helpers.timer import get_run_time, LOGGABLE_ARROW_FORMAT as loggable

if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    import importlib
    importlib.reload(sys)


class TestDataEmpty(Exception):
    """Exception Thrown when Data on specified date is missing."""
    pass


def process(logger, pickle, estimator, predict_target, withhold, date=None, shift_days=-1):
    run_time = get_run_time(date, shift_days=shift_days)
    logger.info('Run-Time: %s' % run_time.format(loggable))
    end_time = run_time.ceil('day').ceil('hour').ceil('minute').ceil('second')
    logger.info('Targeted Processing Interval [%s - %s]' % (run_time.format(loggable), end_time.format(loggable)))
    estimator_name = estimator
    predict_target = predict_target

    # 导入对应的类
    module_tmp = importlib.import_module('helpers.eta.{}_{}'.format(estimator_name, predict_target))
    class_tmp = getattr(module_tmp, '{}{}'.format(estimator_name.capitalize(), predict_target.capitalize()))
    estimator = class_tmp()
    features = sorted(estimator.features)
    # 导入数据
    data = load_pickle(pickle)
    data = data.loc[data.order_time < end_time]
    # 抽取一天数据
    original_test_data = data.loc[(data['time'] > run_time) & (data['time'] < end_time)]
    # 数据处理
    original_test_data = estimator.etl(original_test_data)

    predict_data = original_test_data.loc[:, features]
    # 模型预测：
    try:
        predict_value = estimator.predict(predict_data)
    except XGBoostError as err:
        logger.error('predict XGBoostError: {}'.format(err))
        raise err
    except Exception as err:
        logger.error('Other error: %s' % err)
        raise err

    original_test_data["original_predict_value"] = predict_value
    del predict_value
    original_test_data_with_pre = original_test_data
    del original_test_data
    # 剔除不合理数据(data变成已经去掉异常数据)：
    data = estimator.filter_data(data, run_time, end_time)
    if data is not None and 'order_time' in data.columns:
        filter_data = data.loc[(data['order_time'] > run_time) & (data['order_time'] < end_time)]
        del data
        filter_data['isvalid'] = 1
        logger.info('Test-Data already in Collection. Test-Data after filter Count: %d' % len(filter_data))

        # 单天所有数据，包含已补时后预测值和原始预测值，且标记是否有效
        original_amend_test_data_with_pre = estimator.amend_time(original_test_data_with_pre) # todo:补时
        original_amend_test_data_with_pre = pd.merge(original_amend_test_data_with_pre,
                                                     filter_data.loc[:, ["id", "isvalid", "time"]], how="left",
                                                     on=["id", "time"])
        # 已补时的有效数据且包含未补时值：
        valid_amend_test_data_with_pre = original_amend_test_data_with_pre.loc[original_amend_test_data_with_pre.isvalid == 1]

        # 补时前测试集数据统计指标：mae，mse，r2，N分钟准确率等
        original_valid_test_results = estimator.test_results(valid_amend_test_data_with_pre,
                                                             pd.Series(valid_amend_test_data_with_pre.loc[:, predict_target]),
                                                             pd.Series(valid_amend_test_data_with_pre.original_predict_value)
                                                             )
        logger.info('test_results={}'.format(original_valid_test_results))
        save_pickle(original_valid_test_results, '%s_%s_original_test_results' % (estimator_name, predict_target))
        # 补时后测试集数据统计指标：mae，mse，r2，N分钟准确率等
        valid_test_results = estimator.test_results(valid_amend_test_data_with_pre,
                                              pd.Series(valid_amend_test_data_with_pre.loc[:, predict_target]),
                                              pd.Series(valid_amend_test_data_with_pre.predict_value)
                                              )
        logger.info('test_results={}'.format(valid_test_results))
        save_pickle(valid_test_results, '%s_%s_test_results' % (estimator_name, predict_target))
        if withhold:
            logger.info('withhold={}'.format(withhold))
            estimator.save_DB(original_amend_test_data_with_pre, valid_test_results)
        Logger.resource_checkpoint('after-process')


def main():
    logger = Logger.get_instance(ConfManage.getString("LOG_CRON_NAME"))
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', help='日期', type=str)
    parser.add_argument('-p', '--pickle', type=str, help='数据集', default='data')
    parser.add_argument('estimator', help='算法选择', nargs='?', type=str, default='xgb')
    parser.add_argument('predict_target', help='目标值', nargs='?', type=str, default='accept')
    parser.add_argument('-f', '--feature-selected', help='特征值选择', action='store_true')
    parser.add_argument('-w', '--withhold', help='是否保存数据到bi数据库', action='store_true')
    parser.add_argument("-s", "--shift_days", help="The last few days", type=int, default=-1)
    args = parser.parse_args()
    logger.info('Arguments: estimator=%s, predict-target=%s, feature-selected=%r, withhold-bi-insertion=%r' % \
                (args.estimator, args.predict_target, args.feature_selected, args.withhold))
    try:
        process(logger, args.pickle, args.estimator, args.predict_target, args.withhold, args.date, args.shift_days)
    except TestDataEmpty:
        logger.error('Test Data Empty!')
    except (AttributeError, ValueError) as err:
        logger.error(err)
        logger.error('Trace: {}'.format(traceback.format_exc()))
    except KeyboardInterrupt:
        logger.info('Process manually interupted at %s' % arrow.now(tz=ConfManage.getString("ARROW_TIMEZONE")).format(loggable))
    logger.info('Releasing Logger...')
    # Logger.release_instance()


if __name__ == '__main__':
    main()
