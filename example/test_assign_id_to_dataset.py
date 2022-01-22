#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-21 09:09

@author: johannes
"""
import time
import requests
import numpy as np
import pandas as pd
from pathlib import Path
import pyproj


def api_call(**kwargs):
    """Doc."""
    url = 'http://10.122.2.206:5000/getid?timestamp={t}&longi={lo}&latit={la}'
    return requests.request(
        "GET", url.format(**kwargs),
        headers={
            "Content-Type": "application/json",
        },
    )


def decmin_to_decdeg(pos):
    """Convert coordinates.

    Convert position from decimal degrees into degrees and decimal minutes.
    """
    pos = float(pos)
    output = np.floor(pos / 100.) + (pos % 100) / 60.
    return round(output, 5)


def convert_to_sweref(*xy):
    """Doc."""
    proj = pyproj.Transformer.from_crs(4326, 3006, always_xy=True)
    return proj.transform(*xy)


if __name__ == "__main__":
    # resp = api_call(t='2020-03-10', lo=11.54667, la=58.32333)
    data_path = r'C:\Arbetsmapp\datasets\Chlorophyll\SHARK_Chlorophyll_2018_ALCON_MSVVF\processed_data\data.txt'
    # get_id_to_dataset(data_path)
    df = pd.read_csv(
        data_path,
        sep='\t',
        encoding='cp1252',
        dtype=str,
        keep_default_na=False,
    )
    start_time = time.time()
    ids = []
    # pack_id_log = {}
    for row in df.itertuples():
        start_time = time.time()
        lat_dd = decmin_to_decdeg(row.LATIT.replace(',', '.'))
        lon_dd = decmin_to_decdeg(row.LONGI.replace(',', '.'))
        sr_x, sr_y = convert_to_sweref(lon_dd, lat_dd)
        timestamp = pd.Timestamp(' '.join((row.SDATE, row.STIME)))
        print("Timeit:--%.5f sec" % (time.time() - start_time))

        resp = api_call(
            t=timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            lo=round(sr_x, 1),
            la=round(sr_y, 1)
        )
        if resp.status_code == 200:
            data = resp.json()
            ids.append(data.get('id', ''))
            if 'id' not in data:
                print(data, row.STATN, row.SDATE)
        else:
            ids.append('')
    df['visit_id'] = ids
