#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 base.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:24
# AUTHOR: 	 Aekasitt Guruvanich <sitt@km-it.cn>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
"""Module defining abstract Base class used to connect with MySQL Models"""
from abc import ABCMeta, abstractmethod, abstractproperty
from pandas import read_sql
from sqlalchemy import create_engine, pool
# from sqlalchemy.orm import sessionmaker
from configs import conf
from configs.ConfManage import ConfManage

class Base(object):
    """Abstract Base class used to declare functions in all other model classes"""
    __metaclass__ = ABCMeta
    
    def __init__(self):
        sql_config = {
            'host': conf.MYSQL_HOST, 'port': conf.MYSQL_PORT,
            'user': conf.MYSQL_USER, 'pwd': conf.MYSQL_PASS,
            'dbname': self.__class__.db_name
        }

        self.sql_pool = create_engine("mysql+pymysql://{user}:{pwd}@{host}:{port}/{dbname}?charset=utf8"
            .format(**sql_config), max_overflow=0, pool_size=ConfManage.getInt("MYSQL_DB_CONNECTIONS"),
                                      poolclass=pool.QueuePool, pool_recycle=450)
        # self.engine = create_engine("mysql+pymysql://{user}:{pwd}@{host}:{port}/{dbname}?charset=utf8"
        #     .format(**sql_config), max_overflow=0, pool_size=ConfManage.getInt("MYSQL_DB_CONNECTIONS"),
        #                               poolclass=pool.QueuePool, pool_recycle=450)
        # self.sql_pool = sessionmaker(bind=self.engine)()

    @abstractmethod
    def insert_data(self, data):
        """Insert Data into Table"""
        pass

    @abstractproperty
    def db_name(self):
        """Abstract Property: db_name"""
        pass

    @abstractproperty
    def table_name(self):
        """Abstract Property: table_name"""
        pass

    def list_tables(self):
        sql = 'SELECT `TABLE_NAME` FROM `INFORMATION_SCHEMA`.`TABLES`;'
        return read_sql(sql=sql, con=self.sql_pool.connect()).values.flatten()

    def get_db_name(self):
        """Getter for abstract db_name"""
        return self.__class__.db_name or ''
        
    def get_table_name(self):
        """Getter for abstract table_name"""
        return self.__class__.table_name or ''

    def get_columns(self):
        sql = 'SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` \
                WHERE `TABLE_NAME` = \'{table_name}\';'.format(table_name=self.get_table_name())
        return read_sql(sql=sql, con=self.sql_pool.connect()).values.flatten()

    def fetch_one(self):
        sql = 'SELECT * FROM `{table_name}` LIMIT 1'.format(table_name=self.get_table_name())
        return read_sql(sql=sql, con=self.sql_pool.connect())

    def fetch_latest(self):
        sql = 'SELECT * FROM `{table_name}` ORDER BY addtime DESC LIMIT 1'.format(table_name=self.get_table_name())
        return read_sql(sql=sql, con=self.sql_pool.connect())

    def fetch_in(self, query_lst, col='id'):
        """Fetch All Columns where given `col` (defaults to id if not defined) is
        in list of given values `query_lst`"""
        query_in = ', '.join([str(i) for i in query_lst])
        sql = 'SELECT * FROM `{table_name}` WHERE {col} IN ({query_in});' \
            .format(table_name=self.get_table_name(), col=col, query_in=query_in)
        return read_sql(sql=sql, con=self.sql_pool.connect())