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
      dataset is 'databased' with visits already in this handler,
      those vistis will get the ID from this handler.
      If there is no match, the service will provide the visit
      with a new ID.
    - The match consists of timestamp, position and ship code.
    - Each ID is put into a SQLite (later possibly PostGIS) database
      including the position and a polygon based on a square buffer
      of 2, 20, or 100 m.
    - Using SWEREF99TM as the projected coordinate system.

Example:
    kwargs = dict(
        timestamp='2022-01-10 10:30:00',
        reg_id=135298
    )
    resp = requests.request(
        "GET", 'http://localhost:5000/getid',
        params=kwargs,
        headers={
            "Content-Type": "application/json",
        },
    )
"""  # noqa: E501
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from routes.api import router as api_router
from src.models import ModelDoesNotExists


app = FastAPI()

origins = ['http://localhost:8010']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['GET'],
    allow_headers=['*'],
)

app.include_router(api_router)


@app.exception_handler(ModelDoesNotExists)
async def model_exception_handler(request, exc):
    """Override exceptions."""
    return PlainTextResponse(str(exc), status_code=404)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Override exceptions."""
    return PlainTextResponse(str(exc), status_code=400)


if __name__ == '__main__':
    uvicorn.run(
        'app:app',
        host='127.0.0.1',
        port=8010,
        log_level='info',
        reload=True
    )
