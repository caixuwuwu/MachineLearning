#!/usr/bin/python
# coding:utf-8
"""eat base"""
import importlib
from abc import ABC, abstractmethod
from sklearn.model_selection import train_test_split
from sklearn import metrics
import pandas as pd
import numpy as np

from helpers.learner import Model
from configs import conf
from helpers.logger import Logger
from helpers.pickler import save_pickle, load_pickle


class Base(ABC):
    """Abstract Base class used to declare functions in all other model classes"""

    def __init__(self, estimator, target, below_loss_margin, over_loss_margin, limit_loss_N):
        self.estimator = estimator
        self.target = target
        self.below_loss_margin = below_loss_margin
        self.over_loss_margin = over_loss_margin
        self.limit_loss_N = limit_loss_N
        self.logger = Logger.get_instance(conf.LOG_BASE_NAME)

    @abstractmethod
    def amend_time(self, test_data):
        """补时"""
        pass

    @abstractmethod
    def features(self):
        """预测特征"""
        pass

    @abstractmethod
    def features_savedb(self):
        pass

    @abstractmethod
    def filter_data(self, data, **kwargs):
        """数据过滤"""
        pass

    @abstractmethod
    def etl(self, data):
        """数据处理"""
        return data

    def preprocess(self, training_data, mode='optimal', holdout=False):
        """数据训练"""
        predict_target = self.target
        estimator_name = self.estimator
        ## 对特征进行排序，确保数据一一对应
        features = sorted(self.features)
        actual_value = training_data[predict_target]
        training_data = training_data[features]
        training_data.sort_index(axis=1, inplace=True)
        ## 保存feature为pkl文件
        features_pickle_key = '%s_%s_features' % (estimator_name, predict_target)
        self.logger.info('Features Pickle Key: {}'.format(features_pickle_key))
        save_pickle(features, features_pickle_key)
        self.logger.info('Features: {}'.format(features))
        self.logger.info('Timelines Count: %d' % len(training_data))

        ## Split Data into Training and Testing portions
        if holdout:
            x_train, x_test, y_train, y_test = train_test_split(training_data, actual_value,
                                                                test_size=0.3, random_state=42)
        else:
            x_train, x_test, y_train, y_test = training_data, None, actual_value, None
        ## Release training_data DataFrame
        training_data = None
        # 模型训练
        try:
            model = Model(estimator_name, predict_target, mode)
            model.train(x_train, y_train)
            model.save_mode()
        except Exception as err:
            self.logger.error('TerminatedWorkerError: {}'.format(err))
            raise

    def test_results(self, x_test, y_test, y_predict):
        """
        获取相关测试结果
        x_test 测试数据特征 Dataframe
        y_test 实际值 Series
        y_predict 预测值 Series
        """
        y_predict = np.array(y_predict)
        y_test = np.array(y_test)
        self.logger.info('x_test={}, y_test={}, y_predict={}'.format(type(x_test), type(y_test), type(y_predict)))

        test_results = {}

        test_results_count = len(x_test)
        test_results['count'] = test_results_count

        test_results['mae'] = metrics.mean_absolute_error(y_test, y_predict)
        self.logger.info('Mean Absolute Error: %.4f' % test_results['mae'])

        test_results['mse'] = metrics.mean_squared_error(y_test, y_predict)
        self.logger.info('Mean Squared Error: %.4f' % test_results['mse'])

        test_results['r2'] = metrics.r2_score(y_test, y_predict)
        self.logger.info('R² Score: %.4f' % test_results['r2'])

        loss = abs(y_test - y_predict)
        test_results['min_loss'] = float(min(loss))
        test_results['max_loss'] = float(max(loss))

        # loss<below_loss_margin占比
        below_loss = loss[loss < self.below_loss_margin]
        # self.logger.info('below_loss={}'.format((y_test.to_frame().sub(y_predict))))
        below_loss_count = len(below_loss)
        test_results['below_loss_count'] = below_loss_count
        below_loss_percent = float(below_loss_count) / test_results_count
        test_results['below_loss_percent'] = below_loss_percent
        self.logger.info('Error Count Below %.1f Loss(%%): %d (%.2f%%)' % (
            self.below_loss_margin, below_loss_count, below_loss_percent * 100.))

        # loss>over_loss_margin占比
        over_loss = loss[loss > self.over_loss_margin]
        over_loss_count = len(over_loss)
        test_results['over_loss_count'] = over_loss_count
        over_loss_percent = float(over_loss_count) / test_results_count
        test_results['over_loss_percent'] = over_loss_percent
        self.logger.info('Error Count Over %.1f Loss(%%): %d (%.2f%%)' % (
            self.over_loss_margin, over_loss_count, over_loss_percent * 100.))

        # N分钟准确率
        actual_loss = (np.array(y_test) - np.array(y_predict))
        limit_N = actual_loss[actual_loss <= self.limit_loss_N]
        limit_N_count = len(limit_N)
        test_results['limit_N_count'] = limit_N_count
        limit_N_percent = float(limit_N_count) / test_results_count
        test_results['limit_N_percent'] = limit_N_percent

        # 数据量
        valid_count = len(x_test)
        test_results['valid_count'] = valid_count

        return test_results

    def predict(self, x_test):
        """数据预测"""
        estmator_key = '%s_%s' % (self.estimator, self.target)
        if self.estimator == "xgb":
            import xgboost as xgb
            path = "pickles/{app_mode}-{zone}-{estmator_key}".format(app_mode=conf.APP_MODE, zone=conf.ZONE,
                                                                     estmator_key=estmator_key)
            estimator = xgb.Booster(model_file=path)
            dtest = xgb.DMatrix(x_test)
            pre_data = estimator.predict(dtest)
        else:
            estimator = load_pickle(estmator_key, using_joblib=True)
            pre_data = estimator.predict(x_test)
        return pre_data

    def real_loss_below_n(self, arr):
        df = pd.DataFrame(arr)
        return len(df[df['real_loss'] <= self.limit_loss_N]) / len(df)

    def group_metric(self, total_data, valid_data, cols, model, prediction_date):
        """

        Args:
            total_data: 测试总数据
            valid_data: 有效数据
            cols: 聚合特征
            model: 模型名
            prediction_date: 日期

        Returns:

        """
        df_total = total_data.groupby(cols)['id'].count().reset_index()
        df_total = df_total.rename(columns={'id': 'total_count'})
        df_valid = valid_data.groupby(cols).agg(
            {'order_id': 'count', 'abs_loss': 'mean', 'real_loss': self.real_loss_below_n}).reset_index()
        df_valid = df_valid.rename(
            columns={'order_id': 'valid_count', 'abs_loss': 'mae', 'real_loss': 'limit_N_percent'})
        df_valid[cols] = df_valid[cols].astype(int)
        df_metrics = pd.merge(df_valid, df_total, how='left', on=cols)
        df_metrics['prediction_date'] = prediction_date
        df_metrics['model'] = model
        df_metrics.fillna(0, inplace=True)

        return df_metrics

    def save_DB(self, data, indicators):
        """
            将数据保存到指定数据库。
        :param data: DataFrame  所有测试数据，包含已补时后预测值和原始预测值，且标记是否有效
        :param indicators: Dict  self.test_results返回的结果，补时后的各项指标(有效数据)
        :return: True
        """
        actual_value = 'actual_%s' % self.target
        predict_value = 'predict_%s' % self.target

        # 导入对象对应的模块
        module_raw = importlib.import_module('models_bi.{}_raw'.format(self.target))
        module_metric_all = importlib.import_module('models_bi.eta_metric_all')

        class_raw = getattr(module_raw, '{}Raw'.format(self.target.capitalize()))
        class_metric_all = getattr(module_metric_all, 'EtaMetricAll')

        # 处理raw表数据
        raw_feture_list = self.features_savedb()

        raw_records = data[raw_feture_list]
        raw_records.fillna("null", inplace=True)
        raw_records = raw_records.astype({actual_value: float, predict_value: float})

        valid_data = raw_records.loc[raw_records.isvalid == 1]
        valid_data['abs_loss'] = (valid_data[actual_value] - valid_data[predict_value]).apply(abs)  # 已补时后的损失的绝对值
        valid_data['real_loss'] = valid_data[actual_value] - valid_data[predict_value]  # 已补时后的损失

        # 处理metric表数据
        model = self.estimator + '_' + self.target
        prediction_date = data['order_time'].min().date()
        test_mae = indicators['mae']
        test_mse = indicators['mse']
        test_rsquared = indicators['r2']
        limit_N_percent = indicators['limit_N_percent']
        valid_count = indicators['valid_count']  # 等于 len(valid_data)
        total_count = len(data)
        metric_dict = {
            'prediction_date': prediction_date,
            'model': model,
            'mae': str(test_mae),
            'mse': str(test_mse),
            'r2': str(test_rsquared),
            'limit_N_percent': str(limit_N_percent),
            'valid_count': str(valid_count),
            'total_count': str(total_count)
        }
        metric_all = pd.DataFrame([metric_dict])

        ## Insert Data to BI Tables
        module_name = '%s_raw' % self.target
        self.logger.info('Created %s Table: %r' % (module_name, class_raw().create_if_not_exists()))
        self.logger.info('Inserted Data into %s: %d' % (module_name, class_raw().insert_data(raw_records)))

        # module_name = '%s_metric' % self.target
        # self.logger.info('Created %s Table: %r' % (module_name, class_metric().create_if_not_exists()))
        # self.logger.info('Inserted Data into %s: %d' % (module_name, class_metric().insert_data(metric_record)))

        # 所有模型的指标统计表
        module_name = 'eta_metrics_all'
        self.logger.info('Created %s Table: %r' % (module_name, class_metric_all().create_if_not_exists()))
        self.logger.info('Inserted Data into %s: %d' % (module_name, class_metric_all().insert_data(metric_all)))

        return True
