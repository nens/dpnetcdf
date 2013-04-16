# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from collections import defaultdict

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _

from geoalchemy import WKTSpatialElement
from geoserverlib.client import GeoserverClient

from dpnetcdf.models import (OpendapCatalog, OpendapSubcatalog, OpendapDataset,
                             Variable, MapLayer, Datasource, Style, ShapeFile)
from dpnetcdf.opendap import parse_dataset_properties, get_dataset
from dpnetcdf.utils import parse_opendap_dataset_name
from dpnetcdf.alchemy import (create_geo_table, session, metadata, engine,
                              drop_table)


class OpendapDatasetAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'name', 'date')
    list_filter = ['catalog']
    search_fields = ['name']
    readonly_fields = ('variables',)

    actions = ['load_variables']

    def load_variables(self, request, queryset):
        for obj in queryset:
            try:
                obj.update_variables()
            except Exception, msg:
                messages.error(request, msg)
            else:
                msg = _("Loaded variables for %s" % obj)
                messages.info(request, msg)
    load_variables.short_description = "Load related variables"


class OpendapSubcatalogAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'catalog')

    actions = ['load_datasets']

    def load_datasets(self, request, queryset):
        for obj in queryset:
            datasets_properties = parse_dataset_properties(obj.url)
            count = 0
            for props in datasets_properties:
                nf = parse_opendap_dataset_name(props['name'])
                defaults = {
                    'time_zero': nf[0], 'program': nf[1], 'strategy': nf[2],
                    'year': nf[3], 'scenario': nf[4],
                    'calculation_facility': nf[5], 'date': props['timestamp']}
                dataset, _created = OpendapDataset.objects.get_or_create(
                    catalog=obj, url=props['urlpath'], name=props['name'],
                    defaults=defaults)
                if _created:
                    count += 1
            msg = _("Created %s datasets for %s" % (count, obj.url))
            messages.info(request, msg)
    load_datasets.short_description = _("Load related datasets")


class MapLayerAdmin(admin.ModelAdmin):
    list_display = ['parameter', 'nr_of_datasources', 'nr_of_styles']
    filter_horizontal = ('datasources', 'styles')

    actions = ['publish_to_geoserver']

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

    def publish_to_geoserver(self, request, queryset):
        gs = GeoserverClient(**settings.GEOSERVER_CONFIG)
        workspace = 'deltaportaal'  # TODO: put in settings
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
            # - create intermediate table with SQLAlchemy
            drop_table(obj.parameter)  # first drop, then create again
            Table = create_geo_table(obj.parameter, *variable_columns)
            # - fill this table with the correct values
            raw_rows = defaultdict(dict)
            for datasource in datasources:
                # make fill_value NULL in database
                ds = get_dataset(datasource.dataset.dataset_url)
                year = datasource.dataset.year
                scenario = datasource.dataset.scenario
                variable_name = datasource.variable.name
                shape_file = datasource.shape_file
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
                        except KeyError:
                            # netcdf identifier not in shapefile, fallback
                            # to netcdf point
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
                    if scenario in ['SW', 'RD']:
                        # split in 'S', 'W', 'R' and 'D'
                        scenarios = [scenario[0], scenario[1]]
                    else:
                        scenarios = [scenario]
                    for sc in scenarios:
                        row_key = (geom, year, sc)
                        raw_rows[row_key][variable_name] = value
                        if identifier:
                            raw_rows[row_key]['identifier'] = identifier
            inserts = []
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
            datastore = 'dpnetcdf'
            connection_parameters = settings.GEOSERVER_DELTAPORTAAL_DATASTORE
            gs.create_datastore(workspace, datastore, connection_parameters)
            # - create feature type (or layer), based on this map layer with
            #   the correct sql query:
            sql_query = 'SELECT * FROM %s' % obj.parameter  # sweet and simple
            view = obj.parameter
            gs.create_feature_type(workspace, datastore, view, sql_query)
            # recalculate native and lat/lon bounding boxes
            gs.recalculate_bounding_boxes(workspace, datastore, view)
            # - create or update style(s) and connect it to this view:
            styles = obj.styles.all()
            if styles:
                style = obj.styles.all()[0]
                style_name = style.name
                style_xml = style.xml.strip()
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


admin.site.register(OpendapCatalog)
admin.site.register(OpendapSubcatalog, OpendapSubcatalogAdmin)
admin.site.register(OpendapDataset, OpendapDatasetAdmin)
admin.site.register(Variable)
admin.site.register(MapLayer, MapLayerAdmin)
admin.site.register(Style)
admin.site.register(Datasource)
admin.site.register(ShapeFile)
