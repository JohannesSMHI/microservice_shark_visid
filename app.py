#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Microservice Template: https://github.com/shark-microservices/microservice_template

This service is intended for SMHI-NODC use.
    - It keeps track on visit IDs across datatypes.
      The IDs can be used to match data points from different
      sampling types on the same sampling visit.
    - The ID are based on the sampling year and a serial number (YYYY_NR).
      The serial number is simply the number in the order
      from when it was put into the database. If later a new
      dataset is 'databased' with visits already in this log,
      those vistis will get the ID from this log.
      If there is no match, the service will provide the visit
      with a new ID.
    - The match consists of timestamp, position and ship code.
    - Each ID is put into a SQLite (later possibly PostGIS) database
      including the position and a polygon based on a square buffer
      of 2, 20, or 100 m.
    - Using SWEREF99TM as the projected coordinate system.

Example:
    kwargs = dict(
        timestamp='2019-12-09 02:10:00',
        east=884958,
        north=7252206,
        shipc='77SE'
    )
    resp = requests.request(
        "GET", 'http://localhost:5000/getid',
        params=kwargs,
        headers={
            "Content-Type": "application/json",
        },
    )
"""
import connexion
from log import DbHandler

db = DbHandler()


def get_id(*args, timestamp=None, shipc=None, east=None, north=None, **kwargs):
    """Get id function.

    As of now, we only accept SWEREF99TM.
    """
    return db.get_id(
        timestamp=timestamp,
        shipc=shipc,
        east=east,
        north=north,
    )


app = connexion.FlaskApp(
    __name__,
    specification_dir='./',
    options={'swagger_url': '/'},
)
app.add_api('openapi.yaml')

if __name__ == "__main__":
    app.run(port=5000)
