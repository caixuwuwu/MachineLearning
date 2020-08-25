#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 collect.py
# VERSION: 	 1.0
# CREATED: 	 2018-07-23 17:07
# AUTHOR: 	caiwuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Launch main() to obtain OrderTimelines from Data-API and
Prepare it for Preprocess"""
import argparse
import sys
import pandas as pd
import traceback
import arrow

from client.api_client import ApiClient
from configs.ConfManage import ConfManage
from client.OsrmApi import OsrmApi
from tools.logger import Logger
from tools.caster import chunks
from tools.pickler import delete_pickle, load_pickle, save_pickle
from tools.modeler import get_model
from tools.timer import get_run_time, LOGGABLE_ARROW_FORMAT as loggable
from tools.parallel import multi_thread

if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    # pylint: disable=E0401, E0611, E1101
    import importlib

    importlib.reload(sys)

ENV_ARROW_TIMEZONE = ConfManage.getString("ARROW_TIMEZONE")
ENV_ARROW_TZSHIFT = ConfManage.getInt("ARROW_TZSHIFT")
ENV_DATA_API_TIMERANGE = ConfManage.getInt("DATA_API_TIMERANGE")
ENV_ZONE = ConfManage.getString("ZONE")
logger = Logger.get_instance(ConfManage.getString("LOG_CRON_NAME"))
client = ApiClient()
osrm_api_client = OsrmApi()


def fetch_model_info(id_list, model_name='order', col=None, chunk_size=500):
    model = get_model(model_name)
    result = None
    id_chunks = chunks(id_list, chunk_size)
    for id_chunk in id_chunks:
        if result is None:
            result = model.fetch_in(id_chunk) if col is None else model.fetch_in(id_chunk, col=col)
        else:
            result = result.append(model.fetch_in(id_chunk), sort=False) if col is None \
                else result.append(model.fetch_in(id_chunk, col=col), sort=False)
    logger.info('Fetch %s (Count): %d' % (model_name, len(result)))
    return result


def collect_batch_data(start_time, end_time, table, topic, columns=None, record_path=None, meta=None):
    st = start_time
    et = end_time
    data_df = pd.DataFrame()
    hours_interval = int(24 / ENV_DATA_API_TIMERANGE) if 24 % ENV_DATA_API_TIMERANGE == 0 else 12
    while st < et:
        snt = st.shift(hours=hours_interval)
        data_df = data_df.append(
            client.get_data(table=table, topic=topic, start_time=st.shift(seconds=1), end_time=snt, columns=columns,
                            record_path=record_path, meta=meta))
        st = snt
    return data_df


def fetch_data(start_time, end_time, table, topic, columns=None, record_path=None, meta=None, save_file_prefix=""):
    df = load_pickle(save_file_prefix + topic)
    if df is None:
        df = collect_batch_data(start_time=start_time, end_time=end_time, table=table, topic=topic, columns=columns,
                                record_path=record_path, meta=meta)
        save_pickle(df, save_file_prefix + topic)
    else:
        if len(df) == 0:
            df = collect_batch_data(start_time=start_time, end_time=end_time, table=table, topic=topic, columns=columns,
                                    record_path=record_path, meta=meta)
            save_pickle(df, save_file_prefix + topic)
    logger.info('Fetch %s (Count): %d' % (topic, len(df)))
    return df


def collect(logger, start_time, end_time, pickle_name='data'):
    """
    数据收集及清洗
    :param logger:
    :param start_time:<class 'arrow.arrow.Arrow'> eg:2019-07-14T00:00:00+08:00
    :param end_time:
    :param pickle_name:
    :return:
    """
    collecters = []
    collecters_args = [

    ]
    collecters_results = multi_thread(collecters, kwds=collecters_args)
    # data = collecters_results[0].get()

    clear_pickles(logger)


def save_data(df, filename, logger, features=None):
    data = load_pickle(filename)
    if features is not None:
        save_features = df.loc[:, features]
    else:
        save_features = df
    if data is not None:
        if data.time.astype(int).max() < save_features.time.astype(int).min():
            data = data.append(save_features, sort=False)
            logger.info('Successfully appended new data to %s!' % filename)
        else:
            logger.info('%s: Targeted Run-Time already in Collection-Interval!' % filename)
            del data
            return False
    else:
        data = save_features
    isSave = save_pickle(data, filename)
    del data
    return isSave


def clear_pickles(logger):
    """所有收集保存为pickle的数据必须将该文件名加入到该func的register中"""
    register = [

    ]
    for pickled in register:
        if delete_pickle(pickled):
            logger.info('Removed {pickle_name} successfully!'.format(pickle_name=pickled))
        else:
            logger.info('Error removing {pickle_name}.'.format(pickle_name=pickled))


def trim_outdated(logger, run_time, pickle_name):
    pickled = load_pickle(pickle_name)
    if pickled is None: return
    interval_begin = run_time.shift(days=-ConfManage.getInt("COLLECTION_INTERVAL"))
    pickled = pickled.loc[pickled['order_time'] > interval_begin.ceil('day')]
    if save_pickle(pickled, pickle_name):
        logger.info('Successfully Trimmed outdated! [ {} - {} ]'.format(
            interval_begin.shift(days=1).floor('day').format(loggable), run_time.format(loggable)))


def update_data(logger, funtion, data, merge_on, pickle_name):
    """
    增加新的feature到data.pkl。

    :param logger: 日志
    :param funtion: 需要收集特征的对应函数名。
    :param data: 需要更新的数据集，data.pkl
    :param merge_on: label or list, 要连接的字段名。必须在两个数据区域中找到
    """
    times = data['time']
    start_time = times.min()
    end_time = times.max()
    merge_on = merge_on.split(',')
    update_pickle = eval(funtion)(start_time, end_time)
    data = pd.merge(data, update_pickle, how='left', on=merge_on)
    clear_pickles(logger)
    if save_pickle(data, pickle_name):
        logger.info('Successfully update data!')


# @compute_time
def main():
    """Obtain Information from Data-API and MySQL Database"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', \
                        help='Clear previously saved pickles.', action='store_true')
    parser.add_argument('-r', '--reverse', \
                        help='whether clear previously data.', action='store_true')
    parser.add_argument('-d', '--date', \
                        help='Date used for calculation.', type=str)
    parser.add_argument('-p', '--pickle', type=str, \
                        help='Pickle name for saving latest data-collection.', default='data')
    parser.add_argument('-u', '--updata', type=bool, \
                        help='Merge data with new feature to data.pkl.', default=False)
    parser.add_argument('-f', '--funtion', \
                        help='Update new feature from funtion.')
    parser.add_argument('-m', '--merge_on', \
                        help='Field names to join on. Must be found in both DataFrames.')
    args = parser.parse_args()

    # update date
    if args.updata:
        data = load_pickle(args.pickle)
        if args.funtion is not None and args.merge_on is not None:
            update_data(logger, args.funtion, data, args.merge_on, args.pickle)
        else:
            logger.error('Funtion and Merge_on is None, Please provide corresponding parameters')
        return

    # 清除所有子pkl。
    if args.clear:
        clear_pickles(logger)
        return

    is_reverse = False if args.reverse is None else True  # 向前或向后收集数据
    run_time = get_run_time(None, 0, False)
    logger.info('Run-Time: %s' % run_time)
    collect_date = None if args.date is None else get_run_time(args.date)
    logger.info('Collect-Date: %s' % collect_date)
    # 数据最后时间
    end_time = run_time.shift(days=-1).ceil('day')
    logger.info('End-Time: %s' % end_time)

    pickled = load_pickle(args.pickle)
    collected_start_time = None
    collected_count = 0
    if pickled is not None and isinstance(pickled, pd.DataFrame) and 'time' in pickled.columns:
        times = pickled['time']
        del pickled
        collected_count = len(times.apply(lambda order_time: order_time.date()).unique())
        collected_start_time = times.min()
        logger.info('Min collected order_time Date: %s' % collected_start_time.format(loggable))
        collected_end_time = times.max()
        logger.info('Max collected order_time Date: %s' % collected_end_time.format(loggable))

        if collect_date is not None:
            if collect_date > end_time:
                logger.warning(
                    'collect_date can not greater then end_time {} > {}'.format(collect_date.format(loggable),
                                                                                end_time.format(loggable)))
                return
            if collect_date < collected_start_time.floor('day'):
                start_time = collect_date.floor('day')
                end_time = collected_start_time.shift(days=-1).ceil('day')
            elif collect_date > collected_end_time.ceil('day'):
                start_time = collected_end_time.shift(days=1).floor('day')
                end_time = collect_date.ceil('day')
            else:
                logger.warning('collect_data invalid. {}'.format(collect_date))
        else:
            if collected_end_time >= end_time:
                logger.info('Targeted Run-Time already in Collection-Interval')
                return
            else:
                start_time = collected_end_time.shift(days=1).floor('day')

        gap = start_time.shift(days=-1).date() - end_time.date()
        gap_days = gap.days

    else:
        logger.info('Data empty!')
        gap_days = -ConfManage.getInt("COLLECTION_GAP")
        start_time = end_time.shift(days=gap_days + 1).floor('day')

    logger.info('Total Collection Interval: %d/%d [%s - %s]' % (
        collected_count,
        ConfManage.getInt("COLLECTION_INTERVAL"),
        start_time.format(loggable),
        end_time.format(loggable)))

    if gap_days >= 0:
        logger.info('Targeted Run-Time already in Collection-Interval')
        return

    logger.info('Gap: %d' % (gap_days))
    logger.info('Gap Interval: %d [%s - %s]' % (gap_days, start_time.format(loggable), end_time.format(loggable)))
    try:
        # 针对缺失1天以上的数据进行每日收集
        for i in range(-gap_days, 0, -1):
            end_time = start_time.ceil('day')
            logger.info('Collecting data in [{} - {}]'.format(start_time.format(loggable), end_time.format(loggable)))
            collect(logger, start_time, end_time, args.pickle)
            logger.info(
                'Success collect data in [{} - {}] \n\n'.format(start_time.format(loggable), end_time.format(loggable)))
            start_time = start_time.shift(days=1)
        trim_outdated(logger, run_time, args.pickle)  # 没有环境变量下，默认截取最近30天的数据
    except (AttributeError, ValueError) as err:
        logger.error(err)
        logger.error('Trace: {}'.format(traceback.format_exc()))
    except KeyboardInterrupt:
        logger.info('Process manually interupted at {}'.format(arrow.utcnow()))
    logger.info('Releasing Logger...')
    return 0


if __name__ == '__main__':
    main()
