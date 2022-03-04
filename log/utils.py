#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-20 15:40

@author: johannes
"""
import math
from operator import itemgetter


def dict_factory(cursor, row):
    """Convert SQL-Row-object to dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_id_from_data_sweref(data, point=None):
    """Return list of 'year_id'(s).

    Preferably only one id will be appended to the list.
    """
    ids = []
    for p_id, r, x, y in zip(*itemgetter('year_id', 'radius', 'sweref99tm_east',
                                         'sweref99tm_north')(data)):
        d = distance_between_points_meters(x, point[0], y, point[1])
        if d < r:
            ids.append(p_id)
    return ids


def get_id_from_data_decdeg(data, point=None):
    """Return list of 'year_id'(s).

    Preferably only one id will be appended to the list.
    """
    ids = []
    for p_id, r, x, y in zip(*itemgetter('year_id', 'radius', 'lon_dd',
                                         'lat_dd')(data)):
        d = distance_between_points_decdeg(x, point[0], y, point[1])
        if d < r:
            ids.append(p_id)
    return ids


def distance_between_points_meters(x1, x2, y1, y2):
    """Distance between two points.

    Example of coordinate reference system in meters: SWEREF99TM
    """
    return (((x2 - x1) ** 2) + ((y2 - y1) ** 2)) ** 0.5


def distance_between_points_decdeg(x1, x2, y1, y2):
    """Distance between two positions.

    Args in decimal degrees, eg. (N)58.4561, (E)21.6548
    http://www.johndcook.com/blog/python_longitude_latitude/
    """
    if y1 == y2 and x1 == x2:
        return 0
    degrees_to_radians = math.pi / 180.0

    phi1 = (90.0 - y1) * degrees_to_radians
    phi2 = (90.0 - y2) * degrees_to_radians

    theta1 = x1 * degrees_to_radians
    theta2 = x2 * degrees_to_radians

    cos = (
        math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
        math.cos(phi1) * math.cos(phi2)
    )

    # 6371 ~ radius of the earth (km) * 1000 m
    distance = math.acos(cos) * 6371. * 1000.

    return distance
