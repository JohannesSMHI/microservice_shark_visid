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


TS_FMT = '%Y-%m-%d %H:%M:%S'
TIME_DELTA = pd.Timedelta(hours=6)


def get_start_end_timestamps(ts):
    """Doc."""
    if ts.endswith(' 00:00:00'):
        ts = pd.Timestamp(ts)
        return (ts - TIME_DELTA).strftime(TS_FMT), \
               (ts + pd.Timedelta(hours=23, minutes=59)).strftime(TS_FMT)
    else:
        ts = pd.Timestamp(ts)
        return (ts - TIME_DELTA).strftime(TS_FMT), \
               (ts + TIME_DELTA).strftime(TS_FMT)


class DbHandler:
    """PostGIS database handler."""

    _query_date = """select * from ids where DATE(timestamp) = {}"""
    _query_window = """
    select * from ids where timestamp between {start} and {end}
    """

    def __init__(self):
        start_time = time.time()
        self.engine = get_connection()
        print("Timeit:--%.5f sec" % (time.time() - start_time))

    def get_id(self, timestamp=None, longi=None, latit=None):
        """Doc."""
        # date = pd.Timestamp(timestamp).strftime('%Y-%m-%d')
        start, end = get_start_end_timestamps(timestamp)
        gdf = gp.read_postgis(
            # self._query_date.format("""'{}'""".format(date)),
            self._query_window.format(start="""'{}'""".format(start),
                                      end="""'{}'""".format(end)),
            self.engine,
            geom_col='geometry'
        )
        boolean = gdf.contains(Point(longi, latit))
        point_frame = gdf.loc[boolean, 'year_id']

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


if __name__ == "__main__":
    import time

    db = DbHandler()
    ids = db.get_id(
        timestamp='2022-01-20 12:10:10',
        longi=58.22,
        latit=15.4
    )
