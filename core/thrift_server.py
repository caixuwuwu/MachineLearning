#!/usr/bin/python
# coding:utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 thrift.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
"""Module defining class ETAThriftServer & EstimateTaskDurationsHandler"""

from configs.ConfManage import ConfManage
from core.eta_thrift_handler import EstimateTaskDurationsHandler
import os
import signal
try:
    from thrift.transport import TSocket, TTransport
    from thrift.protocol import TBinaryProtocol, TCompactProtocol
    from thrift.server import TServer, TNonblockingServer
    from thrift.server.TProcessPoolServer import TProcessPoolServer
    from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
except ImportError:
    print('Please run `pip install thrift==0.11.0`')
    raise

import sys
import glob
from tools.logger import Logger
requirements_logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))
try:
    sys.path.append('gen-py')
    sys.path.insert(0, glob.glob('../../lib/py/build/lib*'[0]))
    from eta import EstimateTaskDurations
except ImportError:
    requirements_logger.error('Cannot find thrift classes.')
    requirements_logger.error('Have you run `thrift --gen py eta.thrift`?')
    raise

class RTForkingServer(TServer.TForkingServer):
    def serve(self):
        def try_close(file):
            try:
                file.close()
            except IOError as e:
                requirements_logger.warning(e, exc_info=True)

        self.serverTransport.listen()
        while True:
            client = self.serverTransport.accept()
            if not client:
                continue
            try:
                pid = os.fork()

                if pid:  # parent
                    # add before collect, otherwise you race w/ waitpid
                    self.children.append(pid)
                    self.collect_children()

                    # Parent must close socket or the connection may not get
                    # closed promptly
                    itrans = self.inputTransportFactory.getTransport(client)
                    otrans = self.outputTransportFactory.getTransport(client)
                    try_close(itrans)
                    try_close(otrans)
                else:
                    itrans = self.inputTransportFactory.getTransport(client)
                    otrans = self.outputTransportFactory.getTransport(client)

                    iprot = self.inputProtocolFactory.getProtocol(itrans)
                    oprot = self.outputProtocolFactory.getProtocol(otrans)

                    ecode = 0
                    try:
                        try:
                            while True:
                                self.processor.process(iprot, oprot, client)
                        except TTransport.TTransportException:
                            pass
                        except Exception as e:
                            requirements_logger.exception(e)
                            ecode = 1
                    finally:
                        try_close(itrans)
                        try_close(otrans)

                    os._exit(ecode)

            except TTransport.TTransportException:
                pass
            except Exception as x:
                requirements_logger.exception(x)

class RTThreadedServer(TServer.TThreadedServer):
    """ 多线程式服务端 """
    def handle(self, client):
        itrans = self.inputTransportFactory.getTransport(client)
        otrans = self.outputTransportFactory.getTransport(client)
        iprot = self.inputProtocolFactory.getProtocol(itrans)
        oprot = self.outputProtocolFactory.getProtocol(otrans)
        try:
            while True:
                self.processor.process(iprot, oprot, client)
        except TTransport.TTransportException:
            pass
        except ConnectionResetError:
            pass
        except Exception as x:
            requirements_logger.info(x)

        itrans.close()
        otrans.close()

import threading, queue
class RTProcessPoolServer(TProcessPoolServer):
    """ 多进程式服务端 """

    def setNumThreads(self, thread_num=5):
        self.threads = thread_num

    def setClient(self, methor=queue.Queue()):
        self.clients = methor

    def serveThread(self):
        while True:
            try:
                client = self.clients.get()
                if self.clients.qsize() > 10:
                    requirements_logger.warning("Queue size={}".format(self.clients.qsize()))
                self.serveClient(client)
            except Exception as x:
                requirements_logger.exception(x)

    def workerProcess(self):
        """Loop getting clients from the shared queue and process them"""
        if self.postForkCallback:
            self.postForkCallback()

        for i in range(self.threads):
            try:
                t = threading.Thread(target=self.serveThread)
                t.setDaemon(False)
                t.start()
            except Exception as x:
                requirements_logger.exception(x)

        while self.isRunning.value:
            try:
                client = self.serverTransport.accept()
                if not client:
                    continue
                # self.serveClient(client)
                self.clients.put(client)
            except (KeyboardInterrupt, SystemExit):
                return 0
            except Exception as x:
                requirements_logger.exception(x)

    def serveClient(self, client):
        """Process input/output from a client for as long as possible"""
        itrans = self.inputTransportFactory.getTransport(client)
        otrans = self.outputTransportFactory.getTransport(client)
        iprot = self.inputProtocolFactory.getProtocol(itrans)
        oprot = self.outputProtocolFactory.getProtocol(otrans)

        try:
            while True:
                self.processor.process(iprot, oprot, client)
        except TTransport.TTransportException:
            pass
        except ConnectionResetError:
            pass
        except Exception as x:
            requirements_logger.exception(x)

        itrans.close()
        otrans.close()

class RProcessor(EstimateTaskDurations.Processor):

    def process(self, iprot, oprot, client):
        (name, type, seqid) = iprot.readMessageBegin()
        requirements_logger.info("Client clientIP={}, name: {}".format(client.handle.getpeername()[0][7:], name))
        if name not in self._processMap:
            iprot.skip(TType.STRUCT)
            iprot.readMessageEnd()
            x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
            oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
            x.write(oprot)
            oprot.writeMessageEnd()
            oprot.trans.flush()
            return
        else:

            self._processMap[name](self, seqid, iprot, oprot)
        return True


def run():
    handler = EstimateTaskDurationsHandler()
    # handler.settimeout = ConfManage.getInt("THRIFT_TIMEOUT")
    processor = RProcessor(handler)
    transport = TSocket.TServerSocket(port=ConfManage.getInt("THRIFT_PORT"))
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    # Start Server
    server = RTProcessPoolServer(processor, transport, tfactory, pfactory)
    print('Starting Thrift {} at port: {}'.format(server.__class__.__name__, ConfManage.getInt("THRIFT_PORT")))
    server.setClient()
    server.setNumThreads(ConfManage.getInt("THRIFT_THREAD_COUNT"))
    server.setNumWorkers(ConfManage.getInt("PROCESS_NUM"))

    def clean_shutdown(signum, frame):
        for worker in server.workers:
            requirements_logger.info('Terminating worker: %s' % worker)
            worker.terminate()
        requirements_logger.info('Requesting server to stop()')
        try:
            server.stop()
        except Exception:
            pass
    def set_alarm():
        signal.signal(signal.SIGALRM, clean_shutdown)
        signal.alarm(4)

    set_alarm()
    # 处理僵尸子进程：
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    server.serve()

if __name__ == "__main__":
    run()
