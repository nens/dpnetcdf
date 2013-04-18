# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from collections import defaultdict
import logging

from django.contrib import admin
from django.contrib.gis.gdal import OGRException
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext as _

from geoalchemy import WKTSpatialElement
from geoserverlib.client import GeoserverClient

from dpnetcdf.conf import settings
from dpnetcdf.models import (OpendapCatalog, OpendapSubcatalog, OpendapDataset,
                             Variable, MapLayer, Datasource, Style, ShapeFile)
from dpnetcdf.opendap import get_dataset
from dpnetcdf.utils import parse_dataset_name
from dpnetcdf.alchemy import (create_geo_table, session, metadata, engine,
                              drop_table)

SCENARIO_MAP = {
    'R': 'rust',
    'W': 'warm',
    'D': 'druk',
    'S': 'stoom'
}

logger = logging.getLogger(__name__)


class OpendapDatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'catalog', 'date')
    list_filter = ['catalog']
    search_fields = ['name']
    readonly_fields = ('variables',)


class MapLayerAdmin(admin.ModelAdmin):
    list_display = ['parameter', 'nr_of_datasources', 'nr_of_styles']
    filter_horizontal = ('datasources', 'styles')

    actions = ['full_delete', 'publish_to_geoserver']

    def nr_of_datasources(self, obj):
        """Return number of datasources."""
        return obj.datasources.count()
    nr_of_datasources.allow_tags = False
    nr_of_datasources.short_description = _("datasources")

    def nr_of_styles(self, obj):
        """Return number of styles."""
        return obj.styles.count()
    nr_of_styles.allow_tags = False
    nr_of_styles.short_description = _("styles")

    def get_actions(self, request):
        """Remove default delete action."""
        actions = super(MapLayerAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def full_delete(self, request, queryset):
        """Custom delete action that ensures the delete method on the
        map layer instance is called. The default admin delete action calls
        delete on the queryset and thus bypasses the model's delete method
        and thereby skipping deletion of geoserver layer and database table.
        """
        for obj in queryset:
            obj.delete()
    full_delete.short_description = _("Delete selected layers.")

    def publish_to_geoserver(self, request, queryset):
        gs = GeoserverClient(**settings.GEOSERVER_CONFIG)
        workspace = settings.NETCDF_WORKSPACE_NAME
        for obj in queryset:
            # upload to geoserver, steps:
            # - create column definitions based on the datasources variables
            variable_names = set()
            variable_columns = []
            datasources = obj.datasources.all()
            for datasource in datasources:
                variable = datasource.variable
                variable_names.add(variable.name)
                for variable_name in variable_names:
                    column_definition = {
                        'type': 'float', 'name': variable_name,
                        'nullable': True}
                    variable_columns.append(column_definition)
            # - fill this table with the correct values
            raw_rows = defaultdict(dict)
            for datasource in datasources:
                # make fill_value NULL in database
                ds = get_dataset(datasource.dataset.dataset_url)
                name_params = parse_dataset_name(datasource.dataset.name)
                year = name_params['year']
                scenario = name_params.get('scenario', '')
                variable_name = datasource.variable.name
                shape_file = datasource.shape_file or obj.shape_file
                fill_value = ds[variable_name].attributes.get(
                    '_FillValue')
                x_values = ds['x'][:]  # [:] loads the data
                y_values = ds['y'][:]
                # try to get the identifier value
                if 'station_id' in ds.keys():
                    identifier_values = ds['station_id'][:]
                else:
                    identifier_values = None
                values = ds[variable_name][:]
                # create insertable rows
                for i in range(len(x_values)):
                    x = x_values[i]
                    y = y_values[i]
                    if identifier_values is not None:
                        identifier = identifier_values[i]
                        try:
                            geom = shape_file.identifier_geom_map[
                                identifier]
                        except OGRException:
                            if not shape_file.identifier:
                                msg = _("Shapefile instance %s needs an "
                                        "identifier.") % shape_file
                            else:
                                msg = _("Field '%s' not found in shapefile %s."
                                        "Falling back to NetCDF point." % (
                                        shape_file.identifier, shape_file))
                            logger.debug(msg)
                            geom = Point(x, y, srid=28992)
                        except KeyError:
                            # netcdf identifier not in shapefile, fallback
                            # to netcdf point
                            msg = _("NetCDF identifier '%s' not in shapefile."
                                    " Falling back to NetCDF point.") % \
                                identifier
                            logger.debug(msg)
                            geom = Point(x, y, srid=28992)
                    else:
                        identifier = None
                        # RD srid (lizard_map/coordinates)
                        geom = Point(x, y, srid=28992)
                    value = values[i]
                    if value == fill_value:
                        value = None
                        if int(x) == 0 and int(y) == 0:
                            # skip x = 0.0, y = 0.0 and no value,
                            continue
                    if not scenario:
                        # probably reference dataset
                        ref_year = settings.NETCDF_REFERENCE_YEAR
                        if not str(year) == str(ref_year):
                            # This shouldn't happen. No scenario means year
                            # should be the same as the reference year.
                            # Therefore, this warning. Maybe, the reference
                            # year has changed for certain files.
                            logger.warning(
                                _("No scenario and year %s does not equal "
                                  "reference year %s.") % (year, ref_year))
                        scenarios = SCENARIO_MAP.keys()
                    elif scenario in ['SW', 'RD']:
                        # split in 'S', 'W', 'R' and 'D'
                        scenarios = [scenario[0], scenario[1]]
                    else:
                        scenarios = [scenario]
                    for sc in scenarios:
                        if sc in SCENARIO_MAP.keys():
                            # map scenario character to more verbose scenario
                            # word
                            sc = SCENARIO_MAP[sc]
                        row_key = (geom, year, sc)
                        raw_rows[row_key][variable_name] = value
                        if identifier:
                            raw_rows[row_key]['identifier'] = identifier
            inserts = []
            drop_table(obj.parameter)  # first drop table, then create again
            Table = create_geo_table(obj.parameter, *variable_columns)
            for row_key, variables in raw_rows.items():
                geom, year, scenario = row_key
                t = Table()
                # need to cast this point to a WKTSpatialElement with the
                # RD (28992) srid for GeoAlchemy
                geom_type = ('%s' % geom.geom_type).upper()
                t.geom = WKTSpatialElement(geom.wkt, 28992,
                                           geometry_type=geom_type)
                t.zichtjaar = year
                t.scenario = scenario
                # add variables
                for var, value in variables.items():
                    # identifier is an integer, so do not cast it to float
                    if value is not None and var != 'identifier':
                        # to cast a numpy.float32 to float
                        value = float(value)
                    setattr(t, var, value)
                inserts.append(t)
            # delete existing data from table
            tbl = metadata.tables[obj.parameter]
            con = engine.connect()
            con.execute(tbl.delete())
            # now commit the data
            session.add_all(inserts)
            session.commit()
            # now upload settings to geoserver:
            # - check for workspace 'deltaportaal', if it does not exist,
            #   create it:
            gs.create_workspace(workspace)
            # - check for datastore, if it does not exist, create it with the
            #   correct connection parameters
            datastore = settings.NETCDF_DATASTORE_NAME
            connection_parameters = settings.GEOSERVER_DELTAPORTAAL_DATASTORE
            gs.create_datastore(workspace, datastore, connection_parameters)
            # - create feature type (or layer), based on this map layer with
            #   the correct sql query:
            sql_query = 'SELECT * FROM %s' % obj.parameter  # sweet and simple
            view = obj.parameter
            # delete the layer (if it exists)
            gs.delete_layer(view)
            # delete the feature type (if it exists)
            gs.delete_feature_type(workspace, datastore, view)
            # then create it again
            gs.create_feature_type(workspace, datastore, view, sql_query)
            # recalculate native and lat/lon bounding boxes
            gs.recalculate_bounding_boxes(workspace, datastore, view)
            # - create or update style(s) and connect it to this view:
            styles = obj.styles.all()
            if len(styles):
                style = styles[0]
                style_name = style.name
                style_xml = style.xml.strip()
                # first delete style
                gs.delete_style(style_name)
                # then create it again
                gs.create_style(style_name, style_data=style_xml)
                gs.set_default_style(workspace, datastore, view, style_name)
            else:
                # if no styles are given, set default style to point
                gs.set_default_style(workspace, datastore, view, 'point')
    publish_to_geoserver.short_description = _("Publish to geoserver")

    class Media:
        css = {
            'all': ('dpnetcdf/css/custom_admin.css',)
        }


class ShapeFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'identifier')


admin.site.register(OpendapCatalog)
admin.site.register(OpendapSubcatalog)
admin.site.register(OpendapDataset, OpendapDatasetAdmin)
admin.site.register(Variable)
admin.site.register(MapLayer, MapLayerAdmin)
admin.site.register(Style)
admin.site.register(Datasource)
admin.site.register(ShapeFile, ShapeFileAdmin)
