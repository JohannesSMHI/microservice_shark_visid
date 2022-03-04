#!/usr/bin/env python3
"""
Created on 2022-01-25 15:20

@author: johannes
"""
import requests
import numpy as np
import pandas as pd
from pathlib import Path
import pyproj


def api_call(**kwargs):
    """Return API response."""
    url = 'http://10.122.2.240:5000/getid?timestamp={t}&east={lo}&north={la}'
    if kwargs.get('shipc'):
        url += '&shipc={sc}'
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
    if pos < 70:
        # Already DD
        return pos
    output = np.floor(pos / 100.) + (pos % 100) / 60.
    return round(output, 5)


def convert_to_sweref(*xy):
    """Convert wgs84 to sweref99tm coordinates."""
    proj = pyproj.Transformer.from_crs(4326, 3006, always_xy=True)
    return proj.transform(*xy)


if __name__ == "__main__":

    df_fields = ['STATN', 'SDATE', 'STIME', 'LATIT', 'LONGI', 'SHIPC']

    directory = r'C:\Arbetsmapp\datasets\Phytoplankton'
    for fid in Path(directory).glob('**/data.txt'):
        print(fid.parent.parent)
        df = pd.read_csv(
            fid,
            sep='\t',
            encoding='cp1252',
            dtype=str,
            keep_default_na=False,
        )
        try:
            df = df[df_fields].drop_duplicates()
        except KeyError:
            for col in df_fields:
                if col not in df:
                    df[col] = ''
        ids = []
        # pack_id_log = {}
        for row in df.itertuples():
            lat_dd = decmin_to_decdeg(row.LATIT.replace(',', '.'))
            lon_dd = decmin_to_decdeg(row.LONGI.replace(',', '.'))
            sr_x, sr_y = convert_to_sweref(lon_dd, lat_dd)
            timestamp = pd.Timestamp(' '.join((row.SDATE, row.STIME)))
            resp = api_call(
                t=timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                lo=round(sr_x, 1),
                la=round(sr_y, 1),
                sc=row.SHIPC if len(row.SHIPC) == 4 else ''
            )
            if resp.status_code == 200:
                data = resp.json()
                ids.append(data.get('id', ''))
                if 'id' not in data:
                    print(data, row)
            else:
                print('ERROR', row)
                ids.append('')
        df['visit_id'] = ids
