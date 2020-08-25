#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME:  timer.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module defining time-related utility functions"""
import arrow
import time
from datetime import datetime, date
from tools.logger import Logger
from configs.ConfManage import ConfManage

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATA_API_TIME_FORMAT = '%Y%m%d%H%M%S%Z'
DATA_API_ARROW_FORMAT = 'YYYYMMDDHHmmss'
LOGGABLE_ARROW_FORMAT = 'MMM DD HH:mm:ss'

logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))


def compute_time(func):
    """Record starting point and ending point in time and calculate total runtime"""
    record_time = int(time.time())
    logger.info('start ' + '==' * 10 + ' ' + time.strftime(TIME_FORMAT, time.localtime()))
    # Logger.release_instance()
    result = func()
    logger.info('end ' + '==' * 11 + ' ' + time.strftime(TIME_FORMAT, time.localtime()))
    logger.info('total time: %d' % int(time.time() - record_time))
    # Logger.release_instance()
    return lambda: result


def unix_timestamp(timeobj):
    return time.mktime(timeobj.timetuple())


def dataApiTimeFmt(timeobj):
    if isinstance(timeobj, (datetime, date)):
        return timeobj.strftime(DATA_API_TIME_FORMAT)
    elif isinstance(timeobj, arrow.Arrow):
        return timeobj.format(DATA_API_ARROW_FORMAT)
    else:
        return timeobj


def get_run_time(args_date, shift_days=0, floored=True):
    run_time = None
    if args_date is not None and len(args_date) > 0:
        run_time = arrow.get(args_date).replace(
            tzinfo=ConfManage.getString("ARROW_TIMEZONE"))  # .shift(hours=ENV_ARROW_TZSHIFT)
    else:
        run_time = arrow.now(tz=ConfManage.getString("ARROW_TIMEZONE"))  # .shift(hours=ENV_ARROW_TZSHIFT)
    if floored:
        run_time = run_time.floor('day').floor('hour').floor('minute').floor('second')
    run_time = run_time.shift(days=shift_days) if shift_days != 0 else run_time
    return run_time


def get_date(datetime, fmt='%Y-%m-%d'):
    return datetime.strftime(fmt)


def get_hour(datetime, fmt='%H:%M'):
    return datetime.strftime(fmt)


def get_quarter(datetime):
    if not isinstance(datetime, arrow.Arrow):
        raise TypeError("datetime isn't arrow.Arrow")

    quarter = datetime.date().month
    if quarter in (1, 2, 3):
        str_quarter = 1
    elif quarter in (4, 5, 6):
        str_quarter = 2
    elif quarter in (7, 8, 9):
        str_quarter = 3
    else:
        str_quarter = 4
    return str_quarter


# 计时器
timepiece_time = ConfManage.getInt("TIMEPIECE_TIME")
timeout = float(timepiece_time) if timepiece_time else 5


def timepiece(timeout=timeout, run=ConfManage.getBool("TIMEPIECE_RUN"), msg=0):
    def starttest(fun):
        def fun_run(*args, **kwargs):
            if run:
                starttime = time.time()
                res = fun(*args, **kwargs)
                endtime = time.time()
                totaltime = round(endtime - starttime, 4)
                if totaltime >= timeout:
                    logger.warning(
                        "FunTimeout({}s) funtion={}, msg:{}".format(timeout, fun.__name__, kwargs if msg else None))
                else:
                    logger.debug("FunctionTime funtion={}, time: {}s, msg:{}".format(fun.__name__, totaltime,
                                                                                     kwargs if msg else None))
            else:
                res = fun(*args, **kwargs)
            return res

        return fun_run

    return starttest
