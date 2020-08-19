#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 base.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:24
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
"""Module defining abstract Base class used to connect with MySQL Models"""
from abc import ABC, abstractmethod
from pandas import read_sql
from sqlalchemy import create_engine, exc, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
import warnings
from configs import conf


class Base(ABC):
    """Abstract Base class used to declare functions in all other model classes"""

    def __init__(self, mode='write'):
        if mode == 'write':
            sql_config = {
                'host': conf.BI_MYSQL_HOST, 'port': int(conf.BI_MYSQL_PORT),
                'user': conf.BI_MYSQL_USER, 'pwd': conf.BI_MYSQL_PASS
            }
        else:
            sql_config = {
                'host': conf.BI_R_MYSQL_HOST, 'port': conf.BI_R_MYSQL_PORT,
                'user': conf.BI_R_MYSQL_USER, 'pwd': conf.BI_R_MYSQL_PASS
            }
        
        self.sql_conn = create_engine(
            "mysql+pymysql://{user}:{pwd}@{host}:{port}/{dbname}?charset=utf8"
            .format(**sql_config,dbname=self.__class__.db_name)
        )
        try:
            self.sql_conn.connect()
        except exc.DBAPIError as err:
            raise AttributeError('Cannot retrieve table: {table_name} caused by {err}'.format(
                table_name=self.__class__.table_name, err=err))

    @abstractmethod
    @property
    def db_name(self):
        """Abstract Property: db_name"""
        pass

    @property
    @abstractmethod
    def columns_msg(self):
        return dict()

    @property
    @abstractmethod
    def table_name(self):
        """Abstract Property: table_name"""
        pass

    def create_if_not_exists(self):
        """Create table if not already exists."""
        warnings.filterwarnings('ignore', category=Warning)
        sql = 'CREATE TABLE IF NOT EXISTS {table_name} ('.format(table_name=self.table_name)
        sql += ', '.join(['%s %s' % (column, self.columns_msg[column][0].upper()) +
                          (' %s' % self.columns_msg[column][1].upper()
                           if len(self.columns_msg[column][1]) > 0 else '') for column in self.columns_msg])
        sql += ');'
        if self.sql_conn is not None:
            try:
                self.sql_conn.execute(sql)
                return True
            except Exception as ex:
                print(ex)
                return False

    def insert_data(self, data):
        """
        Insert Data into Table
        Args:
            data: DataFrame

        Returns: len(data)

        """
        if data is not None and self.sql_conn is not None:
            records = data.to_dict(orient='records')
            metadata = MetaData(bind=self.sql_conn, reflect=True)
            table = Table(self.__class__.table_name, metadata, autoload=True)
            # Open the session
            Session = sessionmaker(bind=self.sql_conn)
            session = Session()
            # Inser the dataframe into the database in one bulk
            self.sql_conn.connect().execute(table.insert(), records)
            # Commit the changes
            session.commit()
            return len(records)
        else:
            return -1

    def drop_table(self):
        sql = 'DROP TABLE {table_name};'.format(table_name=self.__class__.table_name)
        try:
            self.sql_conn.execute(sql)
            return True
        except Exception as err:
            print(err)
            return False

    def list_tables(self):
        sql = 'SELECT `TABLE_NAME` FROM `INFORMATION_SCHEMA`.`TABLES`;'
        return read_sql(sql=sql, con=self.sql_conn).values

    @db_name.getter
    def get_db_name(self):
        """Getter for abstract db_name"""
        return self.db_name or ''

    @table_name.getter
    def get_table_name(self):
        """Getter for abstract table_name"""
        return self.table_name or ''

    def get_columns(self):
        sql = 'SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` \
                WHERE `TABLE_NAME` = \'{table_name}\';'.format(table_name=self.get_table_name())
        return read_sql(sql=sql, con=self.sql_conn).values

    def fetch_one(self):
        sql = 'SELECT * FROM `{table_name}` LIMIT 1'.format(table_name=self.get_table_name())
        return read_sql(sql=sql, con=self.sql_conn)

    def fetch_latest(self):
        sql = 'SELECT * FROM `{table_name}` ORDER BY addtime DESC LIMIT 1'.format(table_name=self.get_table_name())
        return read_sql(sql=sql, con=self.sql_conn)

    def fetch_in(self, query_lst, col='id'):
        """Fetch All Columns where given `col` (defaults to id if not defined) is
        in list of given values `query_lst`"""
        query_in = ', '.join([str(i) for i in query_lst])
        sql = 'SELECT * FROM `{table_name}` WHERE {col} IN ({query_in});' \
            .format(table_name=self.get_table_name(), col=col, query_in=query_in)
        return read_sql(sql=sql, con=self.sql_conn)
