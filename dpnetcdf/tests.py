# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.test import TestCase

from dpnetcdf.utils import parse_dataset_name


TEST_DATA = {
    # key is input name, value is expected result after name is parsed
    # DPR
    '200506010000_DPR_maas_S0v1_2015_RF1p0p3.nc': [
        '200506010000', 'DPR_maas', 'S0v1', '2015', None, 'RF1p0p3'],
    '200506010000_DPR_maas_S0v1_2050G_RF1p0p3.nc': [
        '200506010000', 'DPR_maas', 'S0v1', '2050G', None, 'RF1p0p3'],
    '200506010000_DPR_maas_S0v1_2100G_RF1p0p3.nc': [
        '200506010000', 'DPR_maas', 'S0v1', '2100G', None, 'RF1p0p3'],
    '200506010000_DPR_maas_S0v1_2100W_RF1p0p3.nc': [
        '200506010000', 'DPR_maas', 'S0v1', '2100W', None, 'RF1p0p3'],
    '200506010000_DPR_rijn_S0v1_2015_RF1p0p3.nc': [
        '200506010000', 'DPR_rijn', 'S0v1', '2015', None, 'RF1p0p3'],
    '200506010000_DPR_rijn_S0v1_2050G_RF1p0p3.nc': [
        '200506010000', 'DPR_rijn', 'S0v1', '2050G', None, 'RF1p0p3'],
    '200506010000_DPR_rijn_S0v1_2100G_RF1p0p3.nc': [
        '200506010000', 'DPR_rijn', 'S0v1', '2100G', None, 'RF1p0p3'],
    '200506010000_DPR_rijn_S0v1_2100W_RF1p0p3.nc': [
        '200506010000', 'DPR_rijn', 'S0v1', '2100W', None, 'RF1p0p3'],
    # DPRD
    '199101060440_DPRD_S0v1_2015_RF1p0.nc': [
        '199101060440', 'DPRD', 'S0v1', '2015', None, 'RF1p0'],
    '199101060440_DPRD_S0v1_2015_RF1p0p3.nc': [
        '199101060440', 'DPRD', 'S0v1', '2015', None, 'RF1p0p3'],
    '199101060440_DPRD_S0v1_2050_RD_RF1p0p2.nc': [
        '199101060440', 'DPRD', 'S0v1', '2050', 'RD', 'RF1p0p2'],
    '199101060440_DPRD_S0v1_2050_RD_RF1p0p3.nc': [
        '199101060440', 'DPRD', 'S0v1', '2050', 'RD', 'RF1p0p3'],
    '199101060440_DPRD_S0v1_2050_SW_RF1p0p2.nc': [
        '199101060440', 'DPRD', 'S0v1', '2050', 'SW', 'RF1p0p2'],
    '199101060440_DPRD_S0v1_2050_SW_RF1p0p3.nc': [
        '199101060440', 'DPRD', 'S0v1', '2050', 'SW', 'RF1p0p3'],
    '199101060440_DPRD_S0v1_2100_RD_RF1p0p2.nc': [
        '199101060440', 'DPRD', 'S0v1', '2100', 'RD', 'RF1p0p2'],
    '199101060440_DPRD_S0v1_2100_RD_RF1p0p3.nc': [
        '199101060440', 'DPRD', 'S0v1', '2100', 'RD', 'RF1p0p3'],
    '199101060440_DPRD_S0v1_2100_SW_RF1p0p2.nc': [
        '199101060440', 'DPRD', 'S0v1', '2100', 'SW', 'RF1p0p2'],
    '199101060440_DPRD_S0v1_2100_SW_RF1p0p3.nc': [
        '199101060440', 'DPRD', 'S0v1', '2100', 'SW', 'RF1p0p3'],
    # DPZW
    '197612310100_DPZW_koelwater_S0v1_2015_RF1p0p4.nc': [
        '197612310100', 'DPZW_koelwater', 'S0v1', '2015', None, 'RF1p0p4'],
    '197612310100_DPZW_drinkwater_S0v1_2015_RF1p0p4.nc': [
        '197612310100', 'DPZW_drinkwater', 'S0v1', '2015', None, 'RF1p0p4'],
    '197612310100_DPZW_scheepvaart_S0v1_2015_RF1p0p4.nc': [
        '197612310100', 'DPZW_scheepvaart', 'S0v1', '2015', None, 'RF1p0p4'],
    '197612310100_DPZW_NHI30_AfvoerDMTakkenZomerperiode_S0v1_2050_D_RF1p0p4.nc': [
        '197612310100', 'DPZW_NHI30_AfvoerDMTakkenZomerperiode', 'S0v1', '2050', 'D', 'RF1p0p4'],
    '197612310100_DPZW_NHI30_WatervraagAanbodTekortKnelpuntenRegiosZomerperiode_S0v1_2050_D_RF1p0p4.nc': [
        '197612310100', 'DPZW_NHI30_WatervraagAanbodTekortKnelpuntenRegiosZomerperiode', 'S0v1', '2050', 'D', 'RF1p0p4']
}


def dataset_name_params_to_list(params):
    return [params.get('time_zero'), params.get('program'),
            params.get('strategy'), params.get('year'),
            params.get('scenario'), params.get('calculation_facility')]


class OpendapTests(TestCase):

    def test_name_parsing(self):
        for name, expected in TEST_DATA.items():
            params = parse_dataset_name(name)
            result = dataset_name_params_to_list(params)
            self.assertEquals(expected, result)
