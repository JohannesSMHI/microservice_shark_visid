#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-10-07 14:52

@author: johannes
"""
import pandas as pd
from pydantic import BaseModel, Field, validator
from typing import Union, List
from handler import DbHandler
from .exceptions import ModelDoesNotExists

db_handler = DbHandler()


class SingleIdModel(BaseModel):
    reg_id: int = Field(
        default=135298,
        title='REG_ID',
        description='Id for a given sampling site - "Provplats ID"'
    )
    timestamp: Union[str, pd.Timestamp] = Field(
        default='2022-01-10 10:30:00',
        title='Timestamp',
        description='Date and time together in the format Y-m-d H:M:S'
    )
    visit_id: Union[str, None] = Field(
        default=None,
        title='Visit-ID',
        description='Visit ID for a given sampling event.'
    )
    _name = 'SingleIdModel'

    @validator('reg_id', pre=True)
    def validate_reg_id(cls, value):
        return int(value) if value else None

    def update_visit_id(self):
        value = db_handler.get_id(reg_id=self.reg_id, timestamp=self.timestamp)
        if value:
            self.visit_id = value
        else:
            raise ModelDoesNotExists(
                self._name,
                detail='Could not return a visit-id'
            )


class MultiIdModel(BaseModel):
    reg_id_list: List[int] = Field(
        default=[135298],
        title='REG_ID list',
        description='Ids for a list of sampling sites - "Provplats ID"'
    )
    timestamp_list: List[str] = Field(
        default=['2022-01-10 10:30:00'],
        title='Timestamp list',
        description='Dates and times together in the format Y-m-d H:M:S'
    )
    visit_id_list: Union[List[str], List[None], None] = Field(
        default=[None],
        title='Visit-ID list',
        description='Visit IDs for a given list of sampling event.'
    )
    _name = 'MultiIdModel'

    @validator('timestamp_list', 'reg_id_list', pre=True)
    def validate_lists(cls, value):
        if type(value) == list:
            return value
        else:
            return None

    def update_visit_id_list(self):
        value = db_handler.get_id_list(
            reg_id_list=self.reg_id_list, timestamp_list=self.timestamp_list)
        if value:
            self.visit_id_list = value
        else:
            raise ModelDoesNotExists(
                self._name,
                detail='Could not return a list o visit-ids'
            )
