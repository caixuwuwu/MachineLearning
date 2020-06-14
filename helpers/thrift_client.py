# coding=utf-8

from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.Thrift import TApplicationException
from thrift.transport import TSocket, TTransport
from configs.ConfManage import ConfManage
from helpers.logger import Logger

logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))


class ThriftClient:
    '''thrift client'''

    def __init__(self, client_class, host=None, port=None, timeout=None):
        host = host if host is not None else ConfManage.getString("THRIFT_HOST")
        port = port if port is not None else ConfManage.getInt("THRIFT_PORT")
        timeout = timeout if timeout is not None else ConfManage.getInt("THRIFT_TIMEOUT")
        socket = TSocket.TSocket(host, port)
        socket.setTimeout(timeout)
        self.transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        # Create a client
        self.client = client_class.Client(protocol)

    def close(self):
        if self.transport.isOpen():
            self.transport.close()
            # logger.info('thrift transport IS CLOSED!')

    def __enter__(self):
        if not self.transport.isOpen():
            try:
                self.transport.open()
            except Thrift.TException as e:
                logger.error('open transport Thrift.TException: {}'.format(e))
            logger.info('thrift transport IS OPENED!')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def invoke(self, method, *args):
        '''调用THRIFT CLIENT方法'''
        result = None
        try:
            if not self.transport.isOpen():
                self.transport.open()
            func = getattr(self.client, method)
            result = func() if not args else func(*args)
        except (TTransport.TTransportException, TApplicationException) as te:
            logger.error(f'Thrift-Error: {te}')
            self.close()
        except Exception as e:
            logger.error('thrift Exception. %s' % [method, args])
            logger.error('thrift Exception. %s' % e)
            self.close()
        return result
