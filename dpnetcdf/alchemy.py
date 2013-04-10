# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from geoalchemy import (Geometry, GeometryExtensionColumn, GeometryColumn,
                        GeometryDDL)
from geoalchemy.postgis import PGComparator
from sqlalchemy import (create_engine, MetaData, Table, Column, Integer,
                        Unicode, Float)
from sqlalchemy.orm import sessionmaker, mapper

from dpnetcdf.conf import settings

engine = create_engine(settings.NETCDF_SQLALCHEMY_CONNECTION, echo=True)
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData(bind=engine)


class CreateColumnException(BaseException):
    pass


class ColumnMaker(object):

    DEFAULT_STRING_LENGTH = 50

    def _pk_column(self, name='id', **kwargs):
        return Column(name, Integer, primary_key=True)

    def _float_column(self, name, *args, **kwargs):
        return Column(name, Float)

    def _integer_column(self, name, *args, **kwargs):
        return Column(name, Integer)

    def _string_column(self, name, max_length, *args, **kwargs):
        return Column(name, Unicode(max_length))

    def _point_column(self, name, *args, **kwargs):
        return GeometryExtensionColumn(
            name, Geometry(2))

    def create(self, col_data):
        col_type = col_data.pop('type')
        try:
            col_func = getattr(self, '_%s_column' % col_type)
        except AttributeError, msg:
            raise CreateColumnException(msg)
        else:
            return col_func(**col_data)


def create_geo_table(table_name, *extra_columns):
    # geom, year, scenario are always required
    # extra_columns are for extra values
    class GeoTable(object):
        """Empty mapper class for generated geo tables."""
        pass
    cm = ColumnMaker()
    columns = [
        cm.create({'type': 'pk', 'name': 'id'}),
        cm.create({'type': 'point', 'name': 'geom'}),
        cm.create({'type': 'string', 'name': 'year', 'max_length': 6}),
        cm.create({'type': 'string', 'name': 'scenario', 'max_length': 2}),
    ]
    for col_data in extra_columns:
        columns.append(cm.create(col_data))
    geo_table = Table(table_name, metadata, *tuple(columns),
                      extend_existing=True)
    GeometryDDL(geo_table)
    metadata.create_all()
    mapper(GeoTable, geo_table, properties={
        'geom': GeometryColumn(geo_table.c.geom, comparator=PGComparator)
    })
    return GeoTable


def test(nr=1):
    table_name = 'geo_table_%s' % nr
    TableClass = create_geo_table(table_name)
    t = TableClass()
    t.geom = 'POINT(-88.5945861592357 42.9480095987261)'
    t.year = '2015'
    t.scenario = 'RD'
    session.add(t)
    session.commit()
    return TableClass
