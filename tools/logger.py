#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 logger.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module defining class Logger"""
import sys
import logging
import threading
import resource
from logging import StreamHandler
from logging.config import dictConfig
from configs.ConfManage import ConfManage

if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    # pylint: disable=E0401, E1101
    import importlib

    importlib.reload(sys)


class Logger(object):
    """Class used to create Log files in logs/ folder"""
    instance = None
    mutex = threading.Lock()

    def __init__(self, log_name):
        dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
            # 格式化日志
            'formatters': {
                'verbose': {
                    'format': "[%(asctime)s][%(filename)s][%(levelname)s]: %(message)s",
                    'datefmt': "%Y-%m-%d %H:%M:%S"
                },
                'simple': {
                    'format': '%(levelname)s %(message)s'
                },
            },

            'handlers': {
                'null': {
                    'level': ConfManage.getInt("LOG_LEVEL"),
                    'class': 'logging.FileHandler',
                    'filename': 'logs/{}.log'.format(log_name),
                },
                'console': {
                    'level': ConfManage.getInt("LOG_LEVEL"),
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose',
                },
                'thread': {
                    'level': ConfManage.getInt("LOG_LEVEL"),
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'when': "D",
                    # 最多保留10份文件
                    'backupCount': 10,
                    # If delay is true,
                    # then file opening is deferred until the first call to emit().
                    'delay': True,
                    'formatter': 'verbose',
                    'filename': 'logs/{}.log'.format(log_name),
                },
                'process': {
                    'level': ConfManage.getInt("LOG_LEVEL"),
                    # 如果没有使用并发的日志处理类，在多实例的情况下日志会出现缺失
                    'class': 'cloghandler.ConcurrentRotatingFileHandler',
                    # 当达到10MB时分割日志
                    'maxBytes': 1024 * 1024 * 1024,
                    # 最多保留50份文件
                    'backupCount': 10,
                    'delay': True,
                    'formatter': 'verbose',
                    'filename': 'logs/{}.log'.format(log_name),
                },
            },

            'loggers': {
                ConfManage.getString("LOG_BASE_NAME"): {
                    'handlers': ['thread'],
                    'level': ConfManage.getInt("LOG_LEVEL"),
                },
                ConfManage.getString("LOG_CRON_NAME"): {
                    'handlers': ['thread'],
                    'level': ConfManage.getInt("LOG_LEVEL"),
                },
                ConfManage.getString("LOG_REQ_NAME"): {
                    'handlers': ['thread'],
                    'level': ConfManage.getInt("LOG_LEVEL"),
                },
            }
        })
        self.logger = logging.getLogger(log_name)
        streamHandler = StreamHandler(sys.stdout)
        self.logger.addHandler(streamHandler)

    # def shutdown(self):
    #     """Place Holder in case of future changes in Shutting down"""
    #     try:
    #         for handler in list(self.logger.handlers):
    #             self.logger.removeHandler(handler)
    #             del handler
    #         if self.logger is not None:
    #             del self.logger
    #     except AttributeError:
    #         pass

    @staticmethod
    def get_instance(log_name):
        # return Logger(log_name).logger
        """Get Singleton instance of Logger"""
        if Logger.instance is None:
            Logger.mutex.acquire()
            if Logger.instance is None:
                Logger.instance = Logger(log_name)
            Logger.mutex.release()
        return Logger.instance.logger

    @staticmethod
    def release_instance():
        """Release Singleton instance of Logger"""
        if Logger.instance is not None:
            Logger.instance.shutdown()
        Logger.instance = None

    @staticmethod
    def resource_checkpoint(label=""):
        usage = resource.getrusage(resource.RUSAGE_SELF)
        try:
            Logger.instance.logger.info(
                '''Resource Checkpoint [%s]: usertime=%s systime=%s mem=%s mb''' %
                (label, usage[0], usage[1], (usage[2] * resource.getpagesize()) / 1000000.0)
            )
        except Exception:
            raise Exception("Logger Not initialized, must by call get_instance first")
