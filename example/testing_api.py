#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-20 16:38

@author: johannes
"""
import requests


def api_call(**kwargs):
    """Doc."""
    url = 'http://10.122.2.206:5000/getid?timestamp={t}&longi={lo}&latit={la}'
    return requests.request(
        "GET", url.format(**kwargs),
        headers={
            "Content-Type": "application/json",
        },
    )


if __name__ == "__main__":
    resp = api_call(t='2020-03-10', lo=11.54667, la=58.32333)
    print(resp.status_code)
    print(resp.json())
