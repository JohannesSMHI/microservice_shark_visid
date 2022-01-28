#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-20 15:35

@author: johannes
"""
import os
import pandas as pd
import sqlite3

try:
    from . import utils
except:
    import utils


def get_connection():
    """Return a connected database instance."""
    return sqlite3.connect(os.getenv('SHARK_VISIT_DB'))


TS_FMT = '%Y-%m-%d %H:%M:%S'
TIME_DELTA = pd.Timedelta(hours=6)


def get_start_end_timestamps(ts):
    """Return start and end of a specific time window."""
    if ts.endswith(' 00:00:00'):
        ts = pd.Timestamp(ts)
        return (ts - TIME_DELTA).strftime(TS_FMT), \
               (ts + pd.Timedelta(hours=23, minutes=59)).strftime(TS_FMT)
    else:
        ts = pd.Timestamp(ts)
        return (ts - TIME_DELTA).strftime(TS_FMT), \
               (ts + TIME_DELTA).strftime(TS_FMT)


def get_dict(query):
    """Return dictionary of the SQL query."""
    conn = get_connection()
    conn.row_factory = utils.dict_factory
    cur = conn.cursor()
    cur.execute(query)
    data = {}
    for d in cur.fetchall():
        for c, v in d.items():
            data.setdefault(c, []).append(v)
    return data


class DbHandler:
    """SQLite database handler.

    Perhaps we´ll be using PostGIS instead of SQLite later on..
    """

    _query = """
    select * from ids 
    where timestamp between {start} and {end}
    """
    _query_incl_ship = """
    select * from ids 
    where timestamp between {start} and {end}
    and shipc = {shipcode}
    """

    def get_id(self, timestamp=None, east=None, north=None,
               lon_dd=None, lat_dd=None, shipc=None):
        """Return dictionary with id and info."""
        start, end = get_start_end_timestamps(timestamp)
        if shipc:
            data = get_dict(self._query_incl_ship.format(
                start="""'{}'""".format(start), end="""'{}'""".format(end),
                shipcode="""'{}'""".format(shipc))
            )
        else:
            data = get_dict(self._query.format(
                start="""'{}'""".format(start), end="""'{}'""".format(end))
            )

        visit_ids = []
        if data:
            if east:
                visit_ids = utils.get_id_from_data_sweref(
                    data, point=(east, north)
                )
            elif lon_dd:
                visit_ids = utils.get_id_from_data_decdeg(
                    data, point=(lon_dd, lat_dd)
                )

        if len(visit_ids) == 1:
            return {'id': visit_ids[0],
                    'info': 'success'}
        elif len(visit_ids) == 0:
            return {'id': None,
                    'info': 'No match'}
        else:
            # TODO: refine handling and match with closest time?
            return {'id': visit_ids,
                    'info': 'Multiple matches'}

    def post_id(self):
        """Doc."""
        raise NotImplementedError


if __name__ == "__main__":
    import time

    # start_time = time.time()
    # db = DbHandler()  # --0.03690 sec
    db = DbHandler()  # Timeit:--0.00400 sec  raw_python=True
    # # db = DbHandler(postgis=True)
    start_time = time.time()

    ids = db.get_id(
        timestamp='2019-12-09 02:10:00',
        east=884958,
        north=7252206,
        shipc='77SE'
    )
    print("Timeit:--%.5f sec" % (time.time() - start_time))
