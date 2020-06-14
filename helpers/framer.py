#!/usr/bin/env python
# coding: utf-8
# Copyright (C) 2005-2018 All rights reserved.
# FILENAME: 	 framer.py
# VERSION: 	 1.0
# CREATED: 	 2018-01-25 12:23
# AUTHOR: 	 caixuwu@outlook.com
# DESCRIPTION:
#
# HISTORY:
# *************************************************************
"""Module definining useful DataFrame and Array data functions"""
import sys
from numpy import array, fromstring
from json import loads

if sys.version_info[:2] in [(2, 6), (2, 7)]:
    reload(sys)
    sys.setdefaultencoding('utf-8')
elif sys.version_info[:2] in [(3, 6), (3, 7)]:
    import importlib

    importlib.reload(sys)


def select(dataframe, column_row_tuple, return_type=None):
    column, row = column_row_tuple
    try:
        selected = dataframe.get(column).get(row)
        if return_type is None:
            return selected
        else:
            return return_type(selected)
    except AttributeError:
        return None


def select_array(dataframe, column_row_tuple, dtype=int, separator=' '):
    selected = select(dataframe, column_row_tuple)
    if type(selected) is list:
        return array(selected)
    elif selected is not None:
        try:
            return fromstring(selected, dtype=dtype, sep=separator)
        except TypeError:
            return selected


def jsonify(dataframe):
    return loads(dataframe.T.to_json()).values()


def slottify(dataframe, timeslot_tuples):
    slotted_frames = {}
    results = {}
    for slot, timeslot_tuple in timeslot_tuples.iteritems():
        query = 'hour >= %d and hour < %d' % (timeslot_tuple[0], timeslot_tuple[1]) \
            if timeslot_tuple[1] > timeslot_tuple[0] else \
            '(hour >= 0 and hour < %d) or (hour >= %d and hour < 24)' % \
            (timeslot_tuple[1], timeslot_tuple[0])
        slotted_frames[slot] = dataframe.query(query)
        intersect_tasker_max = 0
        for slotted, frame in slotted_frames.iteritems():
            if slotted == slot:
                continue
            intersect = frame.reset_index().merge(slotted_frames[slot], how='inner', \
                                                  on=['area_id', 'weekday', 'hour', 'optimal_tasker_count']).set_index(
                'index')
            if intersect.empty:
                continue
            intersect_tasker_max = intersect['optimal_tasker_count'].max()
            frame = frame.drop(intersect.index)
            # slotted_frames[slotted] = frame
            slotted_frames[slot] = slotted_frames[slot].drop(intersect.index)
            if not slotted_frames[slot].empty:
                results[slot] = max(slotted_frames[slot]['optimal_tasker_count'].max(),
                                    results.get(slot, 0))
            if not frame.empty:
                results[slotted] = max(frame['optimal_tasker_count'].max(),
                                       results.get(slotted, 0))
            if intersect_tasker_max > results.get(slot, 0) + results.get(slotted, 0):
                if results.get(slot, 0) > results.get(slotted, 0):
                    results[slotted] = intersect_tasker_max - results.get(slot, 0)
                else:
                    results[slot] = intersect_tasker_max - results.get(slotted, 0)
    return results
