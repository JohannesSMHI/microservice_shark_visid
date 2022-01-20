#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-20 15:35

@author: johannes
"""
import pandas as pd
import geopandas as gp
from shapely.geometry import Point
from sqlalchemy import create_engine


def get_connection():
    """Doc."""
    return create_engine(
        "postgresql://postgres:jj@localhost:5432/sharkids"
    )


class DbHandler:
    """PostGIS database handler."""

    _search_query = """select * from ids where DATE(timestamp) = {}"""

    def __init__(self):
        self.engine = get_connection()

    def get_id(self, date=None, longi=None, latit=None):
        """Doc."""
        date = pd.Timestamp(date).strftime('%Y-%m-%d')
        gdf = gp.read_postgis(
            self._search_query.format("""'{}'""".format(date)),
            self.engine,
            geom_col='geometry'
        )

        p = Point(longi, latit)
        point_frame = gdf.loc[gdf.contains(p), 'year_id']

        if len(point_frame.index) == 1:
            return {'id': point_frame.iloc[0]}
        elif len(point_frame.index) == 0:
            return {'info': 'No match'}
        else:
            # TODO: refine handling and match with closest time?
            return {'info': 'Multiple matches'}

    def post_id(self):
        """Doc."""
        raise NotImplementedError
