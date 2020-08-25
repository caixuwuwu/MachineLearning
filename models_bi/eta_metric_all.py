#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2016 All rights reserved.
# FILENAME: 	 accept_metric.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:24
# AUTHOR: 	 Aekasitt Guruvanich <sitt@km-it.cn>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module defining Object Relational Model for AcceptMetric using MySQL"""
from configs.ConfManage import ConfManage
from models_bi.base import Base
from pandas import read_sql


# AcceptMetric Model Columns: id, prediction_date, mae, mse, r2, below_two_margin, over_five_margin
class EtaMetricAll(Base):
    """Object Relational Model class used to establish connection to eta_accept_metrics table"""
    db_name = ConfManage.getString("BI_MYSQL_DBNAME")
    table_name = 'eta_metrics_all'
    columns_msg = {
        'id': ['integer unsigned', 'auto_increment primary key'],
        'prediction_date': ['date', 'not null'],
        'model': ['varchar(30)', 'not null'],
        'mae': ['float unsigned', 'not null'],
        'mse': ['float unsigned', 'not null'],
        'r2': ['float unsigned', 'not null'],
        'limit_N_percent': ['float unsigned', 'not null'],
        'valid_count': ['integer unsigned', 'not null'],
        'total_count': ['integer unsigned', 'not null']
    }

    def checkBidata(self, model, prediction_date):
        sql = "SELECT * FROM {table_name} WHERE prediction_date='{prediction_date}' AND model='{model}'" \
            .format(table_name=EtaMetricAll.table_name, prediction_date=prediction_date, model=model)
        df = read_sql(sql=sql, con=self.sql_conn)
        return True if len(df) != 0 else False


if __name__ == '__main__':
    from pandas import set_option
    import arrow

    # set_option('display.max_columns', None)
    # set_option('max_colwidth', 1000)
    now = arrow.now().ceil('day').ceil('hour').ceil('minute').ceil('second')
    day = now.shift(days=-1).date()
    df = EtaMetricAll().checkBidata('xgb_showup', str(day))
    print(df)
