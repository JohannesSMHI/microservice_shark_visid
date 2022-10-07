#!/usr/bin/env python
# Copyright (c) 2022 SMHI, Swedish Meteorological and Hydrological Institute.
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
"""
Created on 2022-01-20 15:40

@author: johannes
"""
from pathlib import Path
from jinja2 import FileSystemLoader, Environment

TEMPLATES = Environment(
    loader=FileSystemLoader(
        searchpath=Path(__file__).parent.joinpath('resources/templates')
    )
)


def get_template(tmp_file):
    """Return jinja template."""
    return TEMPLATES.get_template(tmp_file)


QUERY_TEMPLATE = get_template('query.jinja')
QUERY_MAX_TEMPLATE = get_template('query_max_value.jinja')


def get_query(between_params=None, in_list_params=None, equal_params=None):
    return QUERY_TEMPLATE.render(
        table='ids',
        between_params=between_params,
        in_list_params=in_list_params,
        equal_params=equal_params
    )


def get_max_id_query(equal_params=None):
    return QUERY_MAX_TEMPLATE.render(
        column='id_number',
        table='ids',
        equal_params=equal_params
    )


def dict_factory(cursor, row):
    """Convert SQL-Row-object to dictionary."""
    return {c[0]: row[i] for i, c in enumerate(cursor.description)}
