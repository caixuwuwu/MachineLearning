# /usr/bin/python
# -*- encoding:utf-8 -*-
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME:  ConfManage.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

from configs import conf


class ConfManage(object):

    @staticmethod
    def getString(env):
        try:
            envString = str(getattr(conf, env))
        except AttributeError:
            raise Exception("1502:Have not the env({}) in conf, please check it!".format(env))
        return envString

    @staticmethod
    def getInt(env):
        try:
            envInt = int(getattr(conf, env))
        except ValueError:
            raise Exception("1501:The configuration can't be as integer")
        except AttributeError:
            raise Exception("1502:Have not the env({}) in conf, please check it!".format(env))
        return envInt

    @staticmethod
    def getFloat(env):
        try:
            envFloat = float(getattr(conf, env))
        except ValueError:
            raise Exception("1501:The configuration can't be as float")
        except AttributeError:
            raise Exception("1502:Have not the env({}) in conf, please check it!".format(env))
        return envFloat

    @staticmethod
    def getBool(env):
        try:
            envBool = bool(getattr(conf, env))
        except ValueError:
            raise ValueError("1501:The configuration can't be as Boolen")
        except AttributeError:
            raise Exception("1502:Have not the env({}) in conf, please check it!".format(env))
        return envBool


if __name__ == '__main__':
    env = ConfManage.getString("P4")
    print(type(env))
