#!/usr/bin/python
import sys
from happybase.pool import ConnectionPool
import happybase as hb
import hashlib
import json
import re
from pandas import DataFrame
from helpers.timer import dataApiTimeFmt, timepiece
from helpers.logger import Logger
from configs.ConfManage import ConfManage
from pandas.io.json import json_normalize
import pkg_resources as _pkg_resources
import thriftpy2 as _thriftpy
import threading
from six.moves import queue

_thriftpy.load(
    _pkg_resources.resource_filename('happybase', 'Hbase.thrift'),
    'Hbase_thrift')
from Hbase_thrift import Hbase
from thriftpy2.transport import TSocket
from thriftpy2.thrift import TClient

if sys.version_info[:2] in [(2, 6), (2, 7)]:  # Python 2.6, 2.7
    from urllib import urlencode

    reload(sys)
elif sys.version_info[:2] in [(3, 6), (3, 7)]:  # Python 3.6, 3.7
    # pylint: disable=E0401, E0611, E1101
    import importlib
    from urllib.parse import urlencode

    importlib.reload(sys)

ROWKEY_FMT = '{}|{}|{}'
PREFIX_FILTER_REGEX = re.compile(r"PrefixFilter \(\'(.*?)\'\)")
ID_FILL_SIZE = {'area': 4, 'tasker': 12, 'order': 16, 'user': 12}
HBASE_PREFIX_FILTER = "PrefixFilter ('{}')"
HBASE_ROW_SUBSTR_FILTER = "RowFilter (=, 'substring:|{}')"
logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))


class RConnection(hb.Connection):
    def _refresh_thrift_client(self):
        """Refresh the Thrift socket, transport, and client."""
        socket = TSocket(host=self.host, port=self.port, socket_timeout=self.timeout)
        self.transport = self._transport_class(socket)
        protocol = self._protocol_class(self.transport, decode_response=False, strict_read=False)
        self.client = TClient(Hbase, protocol)


class RConnectionPool(ConnectionPool):
    def __init__(self, size, **kwargs):
        if not isinstance(size, int):
            raise TypeError("Pool 'size' arg must be an integer")

        if not size > 0:
            raise ValueError("Pool 'size' arg must be greater than zero")

        logger.debug(
            "Initializing connection pool with %d connections", size)

        self._lock = threading.Lock()
        self._queue = queue.LifoQueue(maxsize=size)
        self._thread_connections = threading.local()

        connection_kwargs = kwargs
        connection_kwargs['autoconnect'] = False

        for i in range(size):
            connection = RConnection(**connection_kwargs)
            self._queue.put(connection)

        # The first connection is made immediately so that trivial
        # mistakes like unresolvable host names are raised immediately.
        # Subsequent connections are connected lazily.
        with self.connection():
            pass


class HbaseClient(object):

    def __init__(self, host=ConfManage.getString("HBASE_HOST"), port=ConfManage.getInt("HBASE_PORT")):
        self.host = host
        self.port = port
        # self.connection = Connection(host=self.host,port=self.port,table_prefix=ConfManage.getString("HBASE_PREFIX"))
        self.connPool = RConnectionPool(size=ConfManage.getInt("HBASE_CONN_SIZE"), host=self.host, port=self.port,
                                        # timeout=10,
                                        table_prefix=ConfManage.getString("HBASE_PREFIX"))

    def get_area_rowkey(self, prefix, date, index_id=None):
        """
            area
        :param prefix: "indexindex_area"+str(tablename)
        :param index_id: area_id
        :param date: 20190101000000
        :return: str
        """
        prefix = hashlib.sha256(prefix.encode('utf-8')).hexdigest()[:16]
        rowkey = prefix + '|' + str(sys.maxsize - date) + '|' + (str(index_id).zfill(4) if index_id is not None else '')
        return rowkey

    def get_row_key(self, prefix, date, index_id=None, fill=0):
        """
            生成HBase row key.
            Args:
                prefix (str): row key前綴, 'index' + table + topic.
                date (int): 時間 example: 20180419000000.
                index_id (str or int): row key ID.
                fill (int): row key要填充0的個數, 默認為0.
            Returns:
                str: 生成的row key.
        """
        hash_prefix = hashlib.sha256(prefix.encode('utf-8')).hexdigest()[:16]
        return '{}|{}|{}'.format(
            hash_prefix,
            str(sys.maxsize - int(date)),
            str(index_id).zfill(fill) if index_id != None else '')

    def get_data_from_hbase(self, table, query_params):
        results = []
        try:
            scan_result = table.scan(**query_params)
        except Exception as err:
            logger.error("HBaseError, Msg:{}".format(err))
            raise Exception("1199:Can't collect hbase data, provenance: get_data_from_hbase")
        for row_key, data in scan_result:
            # 返回結果全部從byte string轉換成unicode或者float類型
            item = {'id': self.get_row_id(row_key.decode('utf-8')),  # index_id
                    'time': self.get_time(row_key.decode('utf-8'))}  # date
            for key, value in data.items():
                decoded_key = key.decode('utf-8').replace('info:', '')
                try:
                    item[decoded_key] = json.loads(value)
                except ValueError:
                    item[decoded_key] = value.replace(b'?', b'').decode('utf-8')
            results.append(item)
        return results

    def get_row_id(self, row_key):
        """
            获取Hbase row key中的ID.
            Args:
                row_key (str): Hbase row key.
            Returns:
                int: row id.
        """
        return int(row_key.split('|')[-1])

    def get_time(self, row_key):
        """
            获取Hbase row key中的时间.
            Args:
                row_key (str): Hbase row key.
            Returns:
                str: row key的时间. 例如: '20180101090500'.
        """
        return str(sys.maxsize - int(row_key.split('|')[1]))

    def get_rowkey_prefix(self, table, topic):
        """
            生成Hbase row key的前缀prefix.
            Args:
                table (str): 要查询的表.
                topic (str): 要查询的主题.
            Returns:
                str: 生成的前缀.
        """
        prefix = 'indexindex_' + table + topic
        return prefix

    def get_data(self, table, topic, row_id=None, start_time=None, end_time=None, columns=None, record_path=None,
                 meta=None, timeout=None):
        data_json = self.get_json_data(table=table, topic=topic, row_id=row_id, start_time=start_time,
                                       end_time=end_time, columns=columns, timeout=timeout)
        return json_normalize(data_json, record_path=record_path, meta=meta, errors="ignore")

    def get_df_data(self, table, topic, row_id=None, start_time=None, end_time=None, columns=None, timeout=None):
        data_json = self.get_json_data(table=table, topic=topic, row_id=row_id, start_time=start_time,
                                       end_time=end_time, columns=columns, timeout=timeout)
        return pd.DataFrame(data_json)

    @timepiece(msg=1)
    def get_json_data(self, table, topic, row_id=None, start_time=None, end_time=None, columns=None, timeout=None):
        """
        该方法适用于所有的topic获取数据
        :param timeout:
        :param row_id:
        :param table: string
        :param topic: string
        :param start_time: arrow.Arrow eg:2020-02-18T00:00:00+08:00
        :param end_time: arrow.Arrow   eg:2020-02-18T00:00:00+08:00
        :param columns: list
        :return:DataFrame
        """
        if start_time:  # TODO:后续完善这方面代码为一个功能， 冷热表切换（如果有定义时间获取数据，时间大于1年，则切换到冷表获取）
            cold_time = arrow.now(tz=ConfManage.getString("ARROW_TIMEZONE")).shift(years=-1).format("YYYYMMDD000000")
            if int(dataApiTimeFmt(start_time)) < int(cold_time):
                table = table + "_cold"

        query_params = self._get_scan_query_params(table, topic, row_id, time_start=dataApiTimeFmt(start_time),
                                                   time_end=dataApiTimeFmt(end_time), columns=columns)

        attempt = 0
        while True:
            try:
                with self.connPool.connection(timeout) as conn:
                    conn_table = conn.table(table)
                    data = self.get_data_from_hbase(table=conn_table, query_params=query_params)
                return data
            except ConnectionResetError as err:
                logger.error("HBaseConnError Topic= {} msg:{}".format(topic, err))
                raise ConnectionResetError("1101: ConnectionResetError")
            except TimeoutError as err:
                logger.error("HBaseTimeout Topic= {}, msg:{}".format(topic, err))
                raise TimeoutError("1102: Timeout when Collect data")
            except Exception as err:
                attempt += 1
                if attempt >= 3:
                    logger.error("HBaseError Topic= {}, msg:{}".format(topic, err))
                    raise Exception("1199: Unknow Error")

    @timepiece(msg=1)
    def get_default_time_range(self, prefix_filter, table):
        """
            在HBase中獲取某個主題中最新數據, 返回数据rowkey中的时间参数. 最好不要在rowkey中放timestamp，根据业务会产生数据倾斜。
            Args:
                prefix_filter (str): Hbase rowkey前缀过滤器 "PrefixFilter('xxxxxxxx')".
                                     其中xxxxxxx为table和topic生成的前缀.
                table (str): 要查询的table.
            Returns:
                str: str(sys.maxsize - 20180101090500).
        """
        prefix = PREFIX_FILTER_REGEX.findall(prefix_filter)[0]
        start_row_id = '0'.zfill(ID_FILL_SIZE.get(table, 0))
        time_end = arrow.utcnow().to('Asia/Shanghai')
        row_start = ROWKEY_FMT.format(
            prefix, sys.maxsize - int(time_end.format('YYYYMMDDHHmm00')),
            start_row_id)

        time_start_list = (time_end.shift(minutes=-5),
                           time_end.shift(minutes=-20),
                           time_end.shift(hours=-1),
                           time_end.shift(days=-1),
                           time_end.shift(days=-15))

        attempt = 0
        while True:
            try:
                with self.connPool.connection(5) as connection:
                    conn_table = connection.table(table)
                    for time_start in time_start_list:
                        row_stop = ROWKEY_FMT.format(
                            prefix, sys.maxsize - int(time_start.format('YYYYMMDDHHmm00')), '99' * len(start_row_id))
                        try:
                            key = [k for k, _ in
                                   conn_table.scan(row_start=row_start, row_stop=row_stop, filter=prefix_filter,
                                                   limit=1)][0]
                            return key.decode('utf-8').split('|')[1]
                        except IndexError:
                            pass
                return sys.maxsize - int(time_end.format('YYYYMMDDHHmm00'))
            except Exception as err:
                attempt += 1
                if attempt >= 3:
                    logger.warning("HBaseError table= {}, msg:{}".format(table, err))
                    return sys.maxsize - int(time_end.format('YYYYMMDDHHmm00'))

    def _get_scan_query_params(self, table, topic, row_id=None, time_start=None, time_end=None, columns=None):
        """
            该方法获取scan的参数
            Args:
                table (str): 要查询的表.
                topic (str): 要查询的主题.
                row_id: list
                time_start (int): 20191010000000
                time_end (int): 同上
                columns (list): 要查询的列
            Returns:
                query_params (dict):scan的参数
        """
        query_params = {'batch_size': 100000}
        # HBase prefix filter, 用於過濾主題.
        prefix = self.get_rowkey_prefix(table, topic)
        query_params['filter'] = HBASE_PREFIX_FILTER.format(hashlib.sha256(prefix.encode('utf-8')).hexdigest()[:16])

        row_ids = ([] if row_id is None or len(row_id) == 1 else row_id)
        row_id = '0' if row_id is None or len(row_id) > 1 else row_id[0]
        # row ID填充0, 使數據庫row key和查詢row key等長.
        row_id = str(row_id).zfill(ID_FILL_SIZE.get(table, 0))
        # HBase scan row_start, row_stop範圍參數, 如果沒有, 默認為查詢最新的數據
        if not (time_start or time_end):
            default_time_diff = self.get_default_time_range(query_params['filter'], table)
            time_start = time_end = sys.maxsize - int(default_time_diff)
        if time_start:
            if all(i == '0' for i in row_id):
                query_params['row_stop'] = bytes(self.get_row_key(prefix, time_start, len(row_id) * "9"), "utf-8")
            else:
                query_params['row_stop'] = bytes(self.get_row_key(prefix, time_start, row_id), "utf-8")
        if time_end:
            query_params['row_start'] = bytes(self.get_row_key(prefix, time_end, row_id), "utf-8")
        # 根據row ID查詢數據, 使用row filter.
        if not all(i == '0' for i in row_id):
            query_params['filter'] += ' AND ' + HBASE_ROW_SUBSTR_FILTER.format(
                row_id)
        # 多個row ID查詢, 只查詢前5個ID.
        if row_ids:
            row_ids_filter = ' OR '.join(HBASE_ROW_SUBSTR_FILTER.format(
                    str(rid).zfill(ID_FILL_SIZE.get(table, 0))) for rid in row_ids)
            query_params['filter'] += ' AND ( ' + row_ids_filter + ' )'
        # HBase scan columns參數, 表示只顯示那些column, 如果沒有該參數顯示所有column.
        if columns:
            # 為column添加column family, 如果column只有一個, 先轉換成列表
            if not isinstance(columns, list):
                columns = [columns]
            # query_params['columns'] = columns = list(map(_add_cf, columns))
            query_params['columns'] = columns = list(
                map(lambda x: bytes('info:' + x, 'utf-8'), columns)) if columns != None else None
        return query_params


if __name__ == '__main__':
    # from stream_collect import *
    # connpool = hb.Connection(host="0.0.0.0", port=9190)
    # with connpool.connection() as conn:
    # print(conn.is_table_enabled("mytable"))
    # print(connpool.tables())
    data = HbaseClient(host="47.56.47.48", port=9090).get_data(
        table="mytable",
        topic="mytopic",
        # columns=["columns",],
        # start_time=arrow.now().shift(minutes=-30),
        # end_time=arrow.now().shift(minutes=-29),
        # record_path="distribute_index",
        # meta=['id', 'distribute_index']
    )
    print(data.to_dict(orient="records"))
