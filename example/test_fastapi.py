#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-10-07 12:32

@author: johannes
"""
from handler.database import DbHandler
import pandas as pd
import numpy as np
import time


def get_example_data():
    df = pd.read_csv(
        'data/data.txt',
        sep='\t',
        header=0,
        encoding='cp1252',
        dtype=str,
        keep_default_na=False,
    )
    df['timestamp'] = df[['sdate', 'stime']].apply(
        lambda x: pd.Timestamp(' '.join(x)).strftime('%Y-%m-%d %H:%M:%S'), axis=1)
    return df[['timestamp', 'reg_id']]


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))


def nearest_ind(dates, control_date):
    time_diff = dates - control_date
    return np.abs(time_diff).argmin()


if __name__ == "__main__":
    data = get_example_data()
    # start_time = time.time()
    # minval = nearest(data['timestamp'], pd.Timestamp('2022-05-05'))
    # minval = nearest_ind(data['timestamp'], pd.Timestamp('2022-05-05'))
    # print("Timeit:--%.5f sec" % (time.time() - start_time))
    # print(minval)
    # start_time = time.time()
    db = DbHandler()  # Timeit:--0.00400 sec  raw_python=True
    start_time = time.time()
    # ids = db.get_id(timestamp='2022-08-23', reg_id=2)
    ids = db.get_id_list(timestamp_list=data['timestamp'].to_list(),
                         reg_id_list=data['reg_id'].to_list())
    print("Timeit:--%.5f sec" % (time.time() - start_time))
    print(ids)
