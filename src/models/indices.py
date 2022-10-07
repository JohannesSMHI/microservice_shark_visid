#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-10-07 14:52

@author: johannes
"""
import pandas as pd
from pydantic import BaseModel, Field, validator
from typing import Union
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
    reg_id_list: int = Field(
        default=135298,
        title='REG_ID',
        description='Id for a given sampling site - "Provplats ID"'
    )
    timestamp_list: str = Field(
        default='2022-01-10 10:30:00',
        title='Timestamp',
        description='Date and time together in the format Y-m-d H:M:S'
    )
    _name = 'MultiIdModel'

    # @validator('reg_id_list', pre=True)
    # def validate_attribute_list(cls, value):
    #     if value:
    #         return db_handler.get_dictionary(attribute_list=value)
    #     else:
    #         raise ModelDoesNotExists(
    #             cls._name,
    #             detail='Could not return any visit-ids'
    #         )
