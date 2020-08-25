#!/usr/bin/python
# coding:utf-8
# encoding=utf-8
# Copyright (C) 2005-2017 All rights reserved.
# FILENAME: 	modeler.py
# VERSION: 	 1.0
# CREATED: 	 2017-10-10 12:24
# AUTHOR: 	caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
import sys

if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    # pylint: disable=E0401, E0611, E1101
    import importlib

    importlib.reload(sys)


def get_model(module_name, folder_name='models'):
    """Return Model defined in models/ folder."""
    __import__('%s.%s' % (folder_name, module_name))
    module = sys.modules['%s.%s' % (folder_name, module_name)]
    class_name = module_name.split('_')
    new_class_name = ''
    for word in class_name:
        new_class_name += word.capitalize()
    attr = getattr(module, new_class_name)
    return attr()
