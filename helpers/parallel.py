#!/usr/bin/python
# coding:utf-8
"""
  线程池模块
"""

from multiprocessing.pool import ThreadPool, Pool
# from multiprocessing import Process, Manager
from configs.ConfManage import ConfManage
from helpers.logger import Logger

logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))


def multi_thread(functions, args=[], kwds=[], threadnum=None):
    threadnum = ConfManage.getInt("PARALLEL_NUM") if threadnum is None else threadnum
    logger.debug('mulit_thread processes={}'.format(threadnum))
    pool = ThreadPool(threadnum)
    func_length = len(functions)
    results = []
    for i in range(0, func_length):
        arg = () if len(args) == 0 else args[i]
        kwd = {} if len(kwds) == 0 else kwds[i]
        result = pool.apply_async(functions[i], args=arg, kwds=kwd)
        results.append(result)
    pool.close()
    pool.join()
    return results


def multi_process(functions, args=(), kwds=[], processnum=None):
    # 多进程
    processnum = ConfManage.getInt("PROCESS_NUM") if processnum is None else processnum
    pool = Pool(processnum)
    func_length = len(functions)
    results = []
    for i in range(0, func_length):
        arg = () if len(args) == 0 else args[i]
        kwd = {} if len(kwds) == 0 else kwds[i]
        result = pool.apply_async(functions[i], args=arg, kwds=kwd)
        results.append(result)
    pool.close()
    pool.join()
    return results


# import gevent
# def gevent_thread(functions, args=(), kwds={}):
#     results = []
#     for i in range(0, len(functions)):
#         arg = () if len(args) == 0 else args[i]
#         kwd = {} if len(kwds) == 0 else kwds[i]
#         results = results.append(gevent.spawn(functions[i], arg, kwds=kwd))
#     gevent.joinall(results)

if __name__ == '__main__':
    def test_thread(arg):
        # time.sleep(arg)
        o = 0
        while True:
            o += 1
        # print(arg)


    fun = [test_thread for i in range(2)]
    args = [{'arg': i + i} for i in range(2)]
    threads = multi_process(fun, kwds=args, processnum=2)
    # threads = multi_thread(fun, kwds=args, threadnum=2)

    threads[0].get()
    threads[1].get()
    print("over")
    # [threads[i].get() for i in range(5,10)]
