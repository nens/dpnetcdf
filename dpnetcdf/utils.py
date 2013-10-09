# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import re


DATASET_NAME_PATTERN = re.compile(
    r"""^(?P<time_zero>\d{12})  # e.g. 200506010000
         _
         (?P<program>DP[a-zA-Z]*)  # e.g. DPR_rijn, DPRD
         (_(?P<strategy>S[0-9]v[0-9]))?  # e.g. S0v1
         _

         (_(?P<scenario>[A-Z]{0,2}))?  # scenario is optional
         _
         (?P<calculation_facility>[A-Za-z0-9]*).nc$  # e.g. RF1p0p3
         """, re.X)


year = re.compile(
    r"""
    _(?P<year>\d{4}[A-Z]?)_  # year can have a one character appended
    """, re.X)

scenario = re.compile(
    r"""
    _(?P<scenario>S\dv\d)_  # scenario is optional
    """, re.X)


def parse_dataset_name(name):
    """Test the regex extensively. See tests file for specific tests."""
    d = year.search(name).groupdict()
    scenario_search = scenario.search(name)
    if scenario_search:
        d.update(scenario_search.groupdict())
    return d
