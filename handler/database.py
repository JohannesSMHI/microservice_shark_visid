#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-20 15:35

@author: johannes
"""
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path

try:
    from . import utils
except BaseException:
    import utils

DB_PATH = Path(__file__).parent.joinpath('resources/visit_db.db')
TS_FMT = '%Y-%m-%d %H:%M:%S'
TIME_DELTA = pd.Timedelta(hours=6)
DEFAULT_DB_FIELDS = ('timestamp', 'reg_id', 'year', 'id_number', 'visit_id')


def get_connection():
    """Return a connected database instance."""
    return sqlite3.connect(str(DB_PATH))


def put_to_db(data):
    conn = get_connection()
    df = pd.DataFrame(data)
    df.to_sql('ids', conn, if_exists='append', index=False)
    conn.close()


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


def get_min_max_timestamps(tss):
    """Return min and max of a specific timestamp list.

    Return min timestamp with time 00:00:00 and max timestamp with
    time 23:59:59, because to some datatypes don´t ues STIME. It does not
    matter if we get a date that´s lower than min-date.
    """
    dates = pd.to_datetime(tss, format='%Y-%m-%d %H:%M:%S')
    return (dates.min() - TIME_DELTA).strftime('%Y-%m-%d 00:00:00'), \
           (dates.max() + TIME_DELTA).strftime('%Y-%m-%d 23:59:59')


def validate_timestamp(ts_validation, ts_db):
    return (ts_db - TIME_DELTA) < pd.Timestamp(ts_validation) < (
            ts_db + TIME_DELTA)


def nearest_ind(dates, control_date):
    time_diff = dates - pd.Timestamp(control_date)
    return np.abs(time_diff).argmin()


def convert_to_np_arrays(data_dict):
    d = {key: np.array(array) for key, array in data_dict.items()}
    d['ts'] = pd.to_datetime(d['timestamp'], format='%Y-%m-%d %H:%M:%S')
    return d


def loop_visits(db_data, timestamp_list=None, reg_id_list=None):
    db_data = convert_to_np_arrays(db_data)
    id_set = set(db_data['reg_id'])
    resp = {'timestamp': [], 'reg_id': [], 'visit_id': []}
    not_in_db = {'timestamp': [], 'reg_id': []}
    for ts, reg_id in zip(timestamp_list, reg_id_list):
        if reg_id:
            reg_id = int(reg_id)
        if not reg_id:
            resp['visit_id'].append(None)
            resp['timestamp'].append(ts)
            resp['reg_id'].append(reg_id)
        elif reg_id in id_set:
            id_indices = db_data['reg_id'] == reg_id
            idx = nearest_ind(db_data['ts'][id_indices], ts)
            validation = validate_timestamp(
                ts, db_data['ts'][id_indices][idx])
            if validation:
                vis_index = np.logical_and(
                    db_data['ts'] == db_data['ts'][id_indices][idx],
                    id_indices
                )
                resp['visit_id'].append(db_data['visit_id'][vis_index][0])
                resp['timestamp'].append(ts)
                resp['reg_id'].append(reg_id)
            else:
                not_in_db['timestamp'].append(ts)
                not_in_db['reg_id'].append(reg_id)
        else:
            not_in_db['timestamp'].append(ts)
            not_in_db['reg_id'].append(reg_id)

    if any(not_in_db['reg_id']):
        append_new_ids(not_in_db, resp)

    return resp


def get_max_value_from_db(year):
    query = utils.get_max_id_query(
        equal_params={'year': year}
    )
    return get_dict(query)['max_value'][0] or 0


def append_new_ids(not_in_db, resp):
    current_ids = {}
    new_data = {k: [] for k in (
        'timestamp', 'reg_id', 'year', 'id_number', 'visit_id')}
    for ts, reg_id in zip(not_in_db['timestamp'], not_in_db['reg_id']):
        year = pd.Timestamp(ts).year
        if year not in current_ids:
            max_value = get_max_value_from_db(year)
            current_ids[year] = max_value + 1

        new_data['timestamp'].append(ts)
        new_data['reg_id'].append(reg_id)
        new_data['year'].append(year)
        new_data['id_number'].append(current_ids[year])
        new_data['visit_id'].append(f'{year}_{current_ids[year]}')

        current_ids[year] += 1

    put_to_db(new_data)

    for key in ('timestamp', 'reg_id', 'visit_id'):
        resp.setdefault(key, []).extend(new_data[key])


def get_dict(query, fields=None):
    """Return dictionary of the SQL query."""
    conn = get_connection()
    conn.row_factory = utils.dict_factory
    cur = conn.cursor()
    cur.execute(query)
    data = {}
    for d in cur.fetchall():
        for c, v in d.items():
            data.setdefault(c, []).append(v)
    if data:
        return data
    else:
        return {c: [] for c in fields or DEFAULT_DB_FIELDS}


class DbHandler:
    """SQLite database handler.

    Perhaps we´ll be using PostGIS instead of SQLite later on..
    """

    #TODO CHECK OUT
    # https://fastapi.tiangolo.com/tutorial/sql-databases/

    def get_id(self, timestamp=None, reg_id=None):
        """Return dictionary with id and info."""
        if not reg_id or not timestamp:
            return None
        reg_id = int(reg_id)

        start, end = get_start_end_timestamps(timestamp)
        query = utils.get_query(
            between_params={'timestamp': [start, end]},
            equal_params={'reg_id': reg_id}
        )
        data = get_dict(query)
        if len(data['reg_id']) == 1:
            return data['visit_id'][0]
        elif len(data['reg_id']) > 1:
            idx = nearest_ind(data['timestamp'], timestamp)
            return data['visit_id'][idx][0]
        else:
            resp = {}
            append_new_ids({'timestamp': [timestamp], 'reg_id': [reg_id]}, resp)
            return resp.get('visit_id')

    def get_id_list(self, timestamp_list=None, reg_id_list=None):
        """Return dictionary with id and info."""
        if not reg_id_list:
            return None
        if len(reg_id_list) == 1:
            return self.get_id(
                timestamp=timestamp_list[0], reg_id=reg_id_list[0])

        start, end = get_min_max_timestamps(timestamp_list)
        query = utils.get_query(
            between_params={'timestamp': [start, end]},
            in_list_params={'reg_id': reg_id_list}
        )
        db_data = get_dict(query)
        response_data = loop_visits(
            db_data, timestamp_list=timestamp_list, reg_id_list=reg_id_list)
        return response_data

    def post_id(self):
        """Doc."""
        raise NotImplementedError


if __name__ == "__main__":
    import time
    # start_time = time.time()
    db = DbHandler()  # Timeit:--0.00400 sec  raw_python=True
    start_time = time.time()
    # ids = db.get_id(timestamp='2022-08-23', reg_id=2)
    print("Timeit:--%.5f sec" % (time.time() - start_time))
