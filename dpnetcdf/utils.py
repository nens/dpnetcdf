# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

def parse_opendap_dataset_name(name):
    """
    Parse Deltaportaal Opendap file names into separate components. Very
    custom and delicate, so test extensively.

    """
    name = name.rstrip('.nc')
    fragments = name.split('_')
    time_zero = fragments[0]
    # last one is always calculation facility
    calculation_facility = fragments[-1]
    if fragments[-2] == 'RD' or fragments[-2] == 'SW':
        scenario = fragments[-2]
        year = fragments[-3]
        strategy = fragments[-4]
    else:
        scenario = ''
        year = fragments[-2]
        strategy = fragments[-3]
    if fragments[2].lower() == 'maas' or fragments[2].lower() == 'rijn':
        program = "%s_%s" % (fragments[1], fragments[2])
    else:
        program = fragments[1]
    return [time_zero, program, strategy, year, scenario,
            calculation_facility]
