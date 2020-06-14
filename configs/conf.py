# /usr/bin/python
# -*- encoding:utf-8 -*-
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME:  __init__.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
import os
import logging

# 服务器环境与地区配置
APP_MODE = os.environ.get('APP_MODE', 'local')
ZONE = os.environ.get('ZONE', 'gd')

# 缓存配置
CACHE_TYPE = os.environ.get("CACHE_TYPE", 'redis') # redis,local
CACHE_AGE = os.getenv("CACHE_AGE", 30)
PICKLE_CACHE_EXPIRE = os.environ.get('PICKLE_CACHE_EXPIRE', 3600)
AREA_CACHE_EXPIRE = os.environ.get('AREA_CACHE_EXPIRE', 3600) #地区缓存时间

# 数据采集方式
API_TYPE = os.environ.get("API_TYPE", "HBase")

# 模型补时需要的参数
P3 = os.environ.get('P3', 1)
P4 = os.environ.get('P4', 0)
IQRC = os.environ.get('IQRC', 0.3)

# thrift相关配置
THRIFT_THREAD_COUNT = os.environ.get('THRIFT_THREAD_COUNT', 5)
THRIFT_PORT = os.environ.get('THRIFT_PORT', 9090)
THRIFT_HOST = os.environ.get('THRIFT_HOST', '127.0.0.1')
THRIFT_TIMEOUT = os.environ.get('THRIFT_TIMEOUT', 1000*10)    # 超时时间，单位毫秒

# data-api配置
DATA_API_ENDPOINT = os.environ.get('DATA_API_HOST', '0.0.0.0')#''rc-hk-data-api.ks-it.co')
DATA_API_PREFIX = os.environ.get('DATA_API_PREFIX', '/index')
DATA_API_TIMERANGE = os.environ.get('DATA_API_TIMERANGE', 6)

# hbase配置
HBASE_HOST = os.environ.get('HBASE_HOST', '0.0.0.0')
HBASE_PORT = os.environ.get('HBASE_PORT', 9090)
HBASE_CONN_SIZE = os.environ.get('HBASE_CONN_SIZE', 10)
HBASE_PREFIX = os.environ.get('HBASE_PREFIX', 'index')
HBASE_AREA = os.environ.get('HBASE_AREA', 'area')
HBASE_ORDER = os.environ.get('HBASE_ORDER', 'order')
HBASE_TASKER = os.environ.get('HBASE_TASKER', 'tasker')
HBASE_USER = os.environ.get('HBASE_USER', 'user')

# 日志有关配置
LOG_BASE_NAME = APP_MODE + '_' + ZONE
LOG_DAEMON_NAME = LOG_BASE_NAME + '_daemon'
LOG_DATA_FETCH_NAME = LOG_BASE_NAME + '_data_fetch'
LOG_CRON_NAME = LOG_BASE_NAME + '_cron'
LOG_REQ_NAME = LOG_BASE_NAME + '_requirements'
LOG_LEVEL = os.environ.get('LOG_LEVEL', logging.INFO) #此设置可使debug日志打印出来

# 数据库配置
MYSQL_HOST = os.environ.get('MYSQL_HOST', '0.0.0.0')
MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASS = os.environ.get('MYSQL_PASS', '123456')
MYSQL_DB_PREFIX = os.environ.get("MYSQL_DB_PREFIX")
MYSQL_DB_TABLE = os.environ.get('MYSQL_DB_TABLE')
MYSQL_DB_CONNECTIONS = os.environ.get("MYSQL_DB_CONNECTIONS", 30)

# BI数据库配置
BI_MYSQL_HOST = os.environ.get('BI_MYSQL_HOST', 'localhost')
BI_MYSQL_PORT = os.environ.get('BI_MYSQL_PORT', '13306')
BI_MYSQL_USER = os.environ.get('BI_MYSQL_USER', 'root')
BI_MYSQL_PASS = os.environ.get('BI_MYSQL_PASS', 'password')
BI_MYSQL_DBNAME = os.environ.get('BI_MYSQL_DBNAME', 'bi_da')

# BI只读数据库
BI_R_MYSQL_HOST = os.environ.get('BI_R_MYSQL_HOST', '0.0.0.0')
BI_R_MYSQL_PORT = os.environ.get('BI_R_MYSQL_PORT', '3306')
BI_R_MYSQL_USER = os.environ.get('BI_R_MYSQL_USER', 'root')
BI_R_MYSQL_PASS = os.environ.get('BI_R_MYSQL_PASS', '')
BI_R_MYSQL_DBNAME = os.environ.get('BI_R_MYSQL_DBNAME', 'bi_da_r')

# osrm配置
OSRM_API_ENDPOINT = os.environ.get('OSRM_API_HOST', '0.0.0.0')
OSRM_API_PREFIX = os.environ.get('OSRM_API_PREFIX', '/route')
OSRM_API_VERSION = os.environ.get('OSRM_API_VERSION', '/v1')
OSRM_API_PATH = OSRM_API_PREFIX + OSRM_API_VERSION
OSRM_API_DRIVING_ROUTE = OSRM_API_PATH + '/driving/'
OSRM_API_WALKING_ROUTE = OSRM_API_PATH + '/walking/'
OSRM_CACHE_EXPIRE = os.getenv('OSRM_CACHE_EXPIRE', 60*60*24*30)
S2_LEVEL = os.environ.get("S2_LEVEL", 20)

# 各模型N分钟准确率对比值
MODEL_N_PERCENT = os.environ.get('MODEL_N_PERCENT', 1.5)

# ridis配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 0)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
REDIS_MAX_CONNECTIONS = os.getenv("REDIS_MAX_CONNECTIONS", 60)

# 时间配置
ARROW_TIMEZONE = os.environ.get('ARROW_TIMEZONE', 'Asia/Shanghai')
ARROW_TZSHIFT = os.environ.get('ARROW_TZSHIFT', -8)

# 训练周期
TRAINING_INTERVAL = os.environ.get('TRAINING_INTERVAL', 10)
# 数据收集周期
COLLECTION_INTERVAL = os.environ.get('COLLECTION_INTERVAL', 50)
WAITING_DIST_RANGE = os.environ.get('WAITING_DIST_RANGE', 3)
MIN_PREDICTION_RANGE = os.environ.get('MIN_PREDICTION_RANGE', 1.5)
# 收集数据天数
COLLECTION_GAP = os.getenv('COLLECTION_GAP', 30)
RELOAD_PICKLE_CACHE_KEY = os.getenv('RELOAD_PICKLE_CACHE_KEY')

# 线程数
PARALLEL_NUM = os.getenv('PARALLEL_NUM', 8)
# 进程数
PROCESS_NUM = os.getenv("PROCESS_NUM", 2)

# pickle相关配置
PICKLE_FOLDER = os.getenv('PICKLE_FOLDER', 'data') # 存放路径
PICKLE_PREFIX = os.getenv('PICKLE_PREFIX', '') # 文件名前缀

#HTTP连接数
HTTP_MAX_CONNECTIONS = os.getenv("HTTP_MAX_CONNECTIONS", 30)

# 计时器启动
TIMEPIECE_RUN = os.getenv("TIMEPIECE_RUN", True)
TIMEPIECE_TIME = os.getenv("TIMEPIECE_TIME", 0)

#TSP
TSP_HOST = os.getenv("TSP_HOST", '0.0.0.0')
TSP_PORT = os.getenv("TSP_PORT", 9091)