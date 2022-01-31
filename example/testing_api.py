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
    return requests.request(
        "GET", 'http://10.122.2.206:5000/getid/',
        params=kwargs,
        headers={
            "Content-Type": "application/json",
        },
    )


if __name__ == "__main__":
    resp = api_call(
        timestamp='2019-12-09 02:10:00',
        east=884958,
        north=7252206,
        shipc='77SE'
    )
    print(resp.status_code)
    print(resp.json())
