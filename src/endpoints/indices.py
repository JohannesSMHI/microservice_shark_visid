#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-10-07 14:52

@author: johannes
"""
from fastapi import APIRouter
from typing import Union
from src.models import (
    SingleIdModel,
    MultiIdModel
)


router = APIRouter(
    tags=['Visit-ID'],
    responses={404: {'description': 'Not found'}},
)


@router.get('/visit-id', response_model=SingleIdModel)
async def get_attribute(reg_id: int, timestamp: str):
    """Return list for the given attribute."""
    item_model = SingleIdModel(reg_id=reg_id, timestamp=timestamp)
    item_model.update_visit_id()
    return item_model.dict()
