#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-09-23 10:28

@author: johannes
"""
from fastapi import APIRouter
from src.endpoints import indices


router = APIRouter()
router.include_router(indices.router)
