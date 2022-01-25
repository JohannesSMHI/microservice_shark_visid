#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Microservice Template: https://github.com/sharksmhi/microservice_template

This service is intended for SMHI-NODC use.
    - It keeps track on visit IDs across datatypes.
      The IDs can be used to match data points from different
      sampling types on the same sampling visit.
    - The ID are based on the sampling year and a serial number (YYYY_NR).
      The serial number is simply the number in the order
      from when it was put into the database. If later a new
      dataset id databased with visits already in this log,
      those vistis will get the ID from this log.
      If there is no match, the service will provide the visit
      with a new ID.
    - The match consists of only timestamp and position.
    - Each ID is put into a PostGIS database including the position
      and a polygon based on a square buffer of 0.001 degree (~111 m).

Examples:
    localhost:5000/getid?timestamp=2020-03-10&longi=11.54667&latit=58.32333

"""
from pathlib import Path
import connexion
from log import DbHandler
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.joinpath('.env'))

db = DbHandler()


def get_id(*args, timestamp=None, shipc=None, east=None, north=None,
           lon_dd=None, lat_dd=None, **kwargs):
    """Get function."""
    return db.get_id(
        timestamp=timestamp,
        shipc=shipc,
        east=east,
        north=north,
        lon_dd=lon_dd,
        lat_dd=lat_dd
    )


app = connexion.FlaskApp(
    __name__,
    specification_dir='./',
    options={'swagger_url': '/'},
)
app.add_api('openapi.yaml')

if __name__ == "__main__":
    app.run(port=5000)
