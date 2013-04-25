# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import logging

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


logger = logging.getLogger(__name__)


class CreateColumnException(BaseException):
    pass


class ColumnTypeException(BaseException):
    pass


def get_column_type(value):
    """Convert value type to column type."""
    if type(value) == int:
        return 'integer'
    elif type(value) == str:
        return 'string'
    elif type(value) == float:
        return 'float'
    else:
        msg = "Unknown column type: %s." % type(value)
        raise ColumnTypeException(msg)


class ColumnMaker(object):
    """Utility class for easily creating SQLAlchemy/GeoAlchemy columns."""
    DEFAULT_STRING_LENGTH = 50

    def _pk_column(self, name='id', **kwargs):
        return Column(name, Integer, primary_key=True)

    def _float_column(self, name, *args, **kwargs):
        return Column(name, Float, nullable=kwargs.get('nullable', False))

    def _integer_column(self, name, *args, **kwargs):
        return Column(name, Integer, nullable=kwargs.get('nullable', False))

    def _string_column(self, name, max_length=DEFAULT_STRING_LENGTH, *args,
                       **kwargs):
        return Column(name, Unicode(max_length),
                      nullable=kwargs.get('nullable', False))

    def _point_column(self, name, *args, **kwargs):
        srid = kwargs.pop('srid', 28992)
        return GeometryExtensionColumn(
            name, Geometry(2, srid=srid))

    def create(self, col_data):
        col_type = col_data.pop('type')
        try:
            col_func = getattr(self, '_%s_column' % col_type)
        except AttributeError, msg:
            raise CreateColumnException(msg)
        else:
            return col_func(**col_data)


def drop_table(table_name):
    """
    Need to call reflect() on metadata first to get the available tables in
    the metadata instance.

    """
    metadata.reflect()
    try:
        table = metadata.tables[table_name]
    except KeyError:
        logger.error("Could not drop table '%s'. Does not exist in SQLAlchemy "
                     "metadata." % table_name)
    else:
        try:
            table.drop(engine, checkfirst=False)
        except Exception, msg:
            logger.error("Error dropping table '%s'. Is it already dropped "
                         "manually?" % table_name)
        metadata.remove(table)


def create_geo_table(table_name, *extra_columns):
    # geom, year, scenario are always required
    # extra_columns are for extra values
    class GeoTable(object):
        """Empty mapper class for generated geo tables."""
        pass
    cm = ColumnMaker()
    columns = [
        cm.create({'type': 'pk', 'name': 'id'}),
        cm.create({'type': 'point', 'name': 'geom', 'srid': 28992}),
        cm.create({'type': 'string', 'name': 'year', 'max_length': 6}),
        cm.create({'type': 'string', 'name': 'scenario', 'max_length': 10,
                   'nullable': True}),
        # identifier can be used to match between shapes and netcdf files
        cm.create({'type': 'string', 'name': 'identifier', 'nullable': True})
    ]
    for col_data in extra_columns:
        columns.append(cm.create(col_data))
    columns = tuple(set(columns))
    geo_table = Table(table_name, metadata, *columns)
    GeometryDDL(geo_table)
    metadata.create_all()
    mapper(GeoTable, geo_table, properties={
        'geom': GeometryColumn(geo_table.c.geom, comparator=PGComparator)
    })
    return GeoTable


def test(nr=1):
    table_name = 'geo_table_%s' % nr
    extra_columns = [
        {'type': 'float', 'name': 'waterstand_actueel', 'nullable': True}
    ]
    TableClass = create_geo_table(table_name, *extra_columns)
    t = TableClass()
    t.geom = 'POINT(-88.5945861592357 42.9480095987261)'
    t.year = '2015'
    t.scenario = 'RD'
    session.add(t)
    session.commit()
    return TableClass
