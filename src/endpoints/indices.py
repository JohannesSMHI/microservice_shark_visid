#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-10-07 14:52

@author: johannes
"""
from fastapi import APIRouter
from typing import List

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


@router.post('/visit-id-list')
async def get_attribute_list(content: MultiIdModel):
    """Return list for the given attribute."""
    content.update_visit_id_list()
    return content.dict()


# @router.get('/visit-id-list', response_model=MultiIdModel)
# async def get_attribute_list(reg_id_list: List[int], timestamp_list: List[str]):
#     """Return list for the given attribute."""
#     item_model = MultiIdModel(
#         reg_id_list=reg_id_list, timestamp_list=timestamp_list)
#     item_model.update_visit_id_list()
#     return item_model.dict()
