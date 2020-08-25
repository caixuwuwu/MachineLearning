#!/usr/bin/env python
# coding: utf-8

from configs.ConfManage import ConfManage
from tools.logger import Logger
from s2sphere import LatLng, CellId, Cell
from tools.cache import Cache


class S2(object):

    def __init__(self):
        self.logger = Logger.get_instance(ConfManage.getString("LOG_BASE_NAME"))
        self.cache = Cache().client
        self.cache_expire = ConfManage.getInt("OSRM_CACHE_EXPIRE")

    def lnglat_to_cellid(self, longitude, latitude):
        """坐标转s2 cellid"""
        LEVEL = ConfManage.getInt("S2_LEVEL")
        if latitude > 90 or latitude < -90:
            raise ValueError('4002:latitude out of range (-90,90)')
        elif longitude > 180 or longitude < -180:
            raise ValueError('4002:latitude out of range (-180,180)')
        elif LEVEL > 30:
            raise ValueError('4009:level must be litter than 30')
        else:
            latlng = LatLng.from_degrees(latitude, longitude)
            cell_id = CellId.from_lat_lng(latlng)
            level_cell_id = cell_id.parent(LEVEL)
            return level_cell_id.id()

    def get_cellid_center_coordinate(self, cellid):
        """
        get one cell's center point's coordinate [longitude, latitude]
        :param cellid: lnglat_to_cellid生成的cellid
        :return:tuple(center_longitude, center_latitude)
        """
        center = Cell(cell_id=CellId(cellid)).get_center()
        return (LatLng.longitude(center).degrees, LatLng.latitude(center).degrees)

    def get_s2_distance(self, traffic, starting_coordinates, destination_coordinates, fun, zone, timeout=None):
        """

        :param traffic: string("driving"/"walking")
        :param starting_coordinates:tuple(longitude,latitude)
        :param destination_coordinates:tuple(longitude,latitude)
        :param fun: OsrmApiClient.get_distance()
        :return:
        """
        try:
            start_id = self.lnglat_to_cellid(starting_coordinates[0], starting_coordinates[1])
            end_id = self.lnglat_to_cellid(destination_coordinates[0], destination_coordinates[1])
        except ValueError as err:
            self.logger.error("S2ValueError coor=%s,%s, msg:%s" % (starting_coordinates, destination_coordinates, err))
            return None
        cache_key = "%s_%s_to_%s" % (traffic, start_id, end_id)
        distance = self.cache.get(cache_key)
        if distance == None or distance == -1:
            start_center_coor = self.get_cellid_center_coordinate(start_id)
            end_center_coor = self.get_cellid_center_coordinate(end_id)
            distance = fun(traffic, start_center_coor, end_center_coor, timeout, zone)
            self.cache.set(cache_key, distance, self.cache_expire)
        return distance
