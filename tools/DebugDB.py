"""
    补充数据：通过指定日期范围，补充每日数据到BI数据库
"""
import argparse
import arrow
from configs.ConfManage import ConfManage
from tools.logger import Logger
from core.preprocess import preprocess
from core.process import process

logger = Logger.get_instance(ConfManage.getString("LOG_CRON_NAME"))
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--pickle', type=str, help='数据集', default='data')
parser.add_argument('estimator', help='算法选择', nargs='?', type=str, default='xgb')
parser.add_argument('predict_target', help='目标值', nargs='?', type=str, default='accept')
parser.add_argument('startDate', help='日期: 2020-01-01', type=str)
parser.add_argument("endDate", help="The last days (2020-01-01)", type=str)
parser.add_argument('-w', '--withhold', help='是否保存数据到bi数据库', action='store_false')
args = parser.parse_args()
date = arrow.get(args.startDate)
endDate = arrow.get(args.endDate)
logger.info("Process between %s and %s" % (date, endDate))
while date < endDate:
    dateStr = date.format("YYYY-MM-DD")
    preprocess(dateStr, args.pickle, args.estimator, args.predict_target, False, args.predict_target, -1)
    process(logger, args.pickle, args.estimator, args.predict_target, args.withhold, dateStr, 0)
    date = date.shift(days=1)
