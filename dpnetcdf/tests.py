# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.test import TestCase

from dpnetcdf.utils import parse_dataset_name
from dpnetcdf.alchemy import ColumnMaker


TEST_DATA = {
    # key is input name, value is expected result after name is parsed
    # DPR
    '200506010000_DPR_maas_S0v1_2015_RF1p0p3.nc': [
        'S0v1', '2015'],
    '200506010000_DPR_maas_S0v1_2050G_RF1p0p3.ns': [
        'S0v1', '2050G'],
    '200506010000_DPR_maas_S0v1_2100G_RF1p0p3.nc': [
        'S0v1', '2100G'],
    '200506010000_DPR_maas_S0v1_2100W_RF1p0p3.nc': [
        'S0v1', '2100W'],
    '200506010000_DPR_rijn_S0v1_2015_RF1p0p3.nc': [
        'S0v1', '2015'],
    '200506010000_DPR_rijn_S0v1_2050G_RF1p0p3.nc': [
        'S0v1', '2050G'],
    '200506010000_DPR_rijn_S0v1_2100G_RF1p0p3.nc': [
        'S0v1', '2100G'],
    '200506010000_DPR_rijn_S0v1_2100W_RF1p0p3.nc': [
        'S0v1', '2100W'],
    # DPRD
    '199101060440_DPRD_S0v1_2015_RF1p0.nc': [
        'S0v1', '2015'],
    '199101060440_DPRD_S0v1_2015_RF1p0p3.nc': [
        'S0v1', '2015'],
    '199101060440_DPRD_S0v1_2050_RD_RF1p0p2.nc': [
        'S0v1', '2050'],
    '199101060440_DPRD_S0v1_2050_RD_RF1p0p3.nc': [
        'S0v1', '2050'],
    '199101060440_DPRD_S0v1_2050_SW_RF1p0p2.nc': [
        'S0v1', '2050'],
    '199101060440_DPRD_S0v1_2050_SW_RF1p0p3.nc': [
        'S0v1', '2050'],
    '199101060440_DPRD_S0v1_2100_RD_RF1p0p2.nc': [
        'S0v1', '2100'],
    '199101060440_DPRD_S0v1_2100_RD_RF1p0p3.nc': [
        'S0v1', '2100'],
    '199101060440_DPRD_S0v1_2100_SW_RF1p0p2.nc': [
        'S0v1', '2100'],
    '199101060440_DPRD_S0v1_2100_SW_RF1p0p3.nc': [
        'S0v1', '2100'],
    # DPZW
    '197612310100_DPZW_koelwater_2015_RF1p0p4.nc': [
        None, '2015'],
    '197612310100_DPZW_drinkwater_2015_RF1p0p4.nc': [
        None, '2015'],
    '197612310100_DPZW_scheepvaart_2015_RF1p0p4.nc': [
        None, '2015'],
    '197612310100_DPZW_NHI30_AfvoerDMTakkenZomerperiode_2050_D_RF1p0p4.nc': [
        None, '2050'],
    '197612310100_DPZW_NHI30_WatervraagAanbodTekortKnelpuntenRegiosZomerperiode_2050_D_RF1p0p4.nc': [
        None, '2050'],
}


def dataset_name_params_to_list(params):
    return [params.get('scenario'), params.get('year')]


class OpendapTests(TestCase):

    def test_name_parsing(self):
        for name, expected in TEST_DATA.items():
            params = parse_dataset_name(name)
            result = dataset_name_params_to_list(params)
            self.assertEquals(expected, result)


class GeoAlchemyColumnMakerTests(TestCase):
    """Tests for column creation by ColumnMaker utility class."""
    def setUp(self):
        self.cm = ColumnMaker()

    def test_primary_key_column(self):
        col = self.cm.create({'type': 'pk', 'name': 'id'})
        self.assertTrue(col.primary_key)
        self.assertEqual(col.name, 'id')
        self.assertFalse(col.nullable)
        self.assertEqual(str(col.type), 'INTEGER')

    def test_string_column(self):
        col = self.cm.create({'type': 'string', 'name': 'identifier',
                              'nullable': True})
        self.assertFalse(col.primary_key)
        self.assertEqual(col.name, 'identifier')
        self.assertTrue(col.nullable)
        # max_length default is 50
        self.assertEqual(str(col.type), 'VARCHAR(50)')

    def test_string_column_2(self):
        col = self.cm.create({'type': 'string', 'name': 'scenario',
                              'max_length': 10})
        self.assertEqual(col.name, 'scenario')
        self.assertFalse(col.nullable)
        self.assertEqual(str(col.type), 'VARCHAR(10)')

    def test_geometry_column(self):
        col = self.cm.create({'type': 'point', 'name': 'geom', 'srid': 28992})
        self.assertEqual(col.name, 'geom')
        self.assertTrue(col.nullable)
        self.assertEqual(str(col.type), 'GEOMETRY')
        self.assertTrue('srid=28992' in '%r' % col)

    def test_float_column(self):
        col = self.cm.create({'type': 'float', 'name': 'waterstand_actueel'})
        self.assertFalse(col.primary_key)
        self.assertEqual(col.name, 'waterstand_actueel')
        self.assertFalse(col.nullable)
        self.assertEqual(str(col.type), 'FLOAT')

    def test_integer_column(self):
        col = self.cm.create({'type': 'integer', 'name': 'area_code',
                              'nullable': True})
        self.assertFalse(col.primary_key)
        self.assertEqual(col.name, 'area_code')
        self.assertTrue(col.nullable)
        self.assertEqual(str(col.type), 'INTEGER')
