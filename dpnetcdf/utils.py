# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import re


DATASET_NAME_PATTERN = re.compile(
    r"""^(?P<time_zero>\d{12})  # e.g. 200506010000
         _
         (?P<program>DP.*)  # e.g. DPR_rijn, DPRD
         _
         (?P<strategy>S[a-zA-Z0-9]{3})  # e.g. S0v1
         _
         (?P<year>\d{4}[A-Z]?)  # year can have a one character appended
         (_(?P<scenario>[A-Z]{0,2}))?  # scenario is optional
         _
         (?P<calculation_facility>[A-Za-z0-9]*).nc$  # e.g. RF1p0p3
         """, re.X)


def parse_dataset_name(name):
    """Test the regex extensively. See tests file for specific tests."""
    return DATASET_NAME_PATTERN.match(name).groupdict()
