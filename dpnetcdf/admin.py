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
                             Variable, MapLayer, Datasource, Geometry, Value,
                             Style, ShapeFile)
from dpnetcdf.opendap import parse_dataset_properties, get_dataset
from dpnetcdf.utils import parse_opendap_dataset_name
from dpnetcdf.alchemy import create_geo_table, session, metadata, engine


class OpendapDatasetAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'name', 'date')
    list_filter = ['catalog']
    search_fields = ['name']
    readonly_fields = ('variables',)

    actions = ['load_variables', 'load_current_waterlevel']

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

    def load_current_waterlevel(self, request, queryset):
        """Test method for loading dataset data."""
        # TODO: make this dynamic: let user choose which variable to use
        var_name = 'waterstand_actueel'
        for obj in queryset:
            # load x,y and value data
            dataset = get_dataset(obj.dataset_url)
            # create datasource
            variable = Variable.objects.get(name=var_name)
            datasource, _created = Datasource.objects.get_or_create(
                dataset=obj, variable=variable)
            x_values = dataset['x'][:]  # [:] loads the data
            y_values = dataset['y'][:]
            values = dataset[var_name][:]
            for i in range(len(x_values)):
                point = Point(x_values[i], y_values[i])
                geometry, _created = Geometry.objects.get_or_create(
                    geometry=point)
                Value.objects.get_or_create(
                    datasource=datasource, geometry=geometry, value=values[i])


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


class ValueAdmin(admin.ModelAdmin):
    list_display = ('datasource', 'geometry', 'value')
    list_filter = ['datasource']


class MapLayerAdmin(admin.ModelAdmin):
    list_display = ['parameter', 'nr_of_datasources', 'nr_of_styles']
    filter_horizontal = ('datasources', 'styles')

    actions = ['publish_to_geoserver']

    def nr_of_datasources(self, obj):
        """Return number of datasources."""
        return obj.datasources.count()
    nr_of_datasources.allow_tags=False
    nr_of_datasources.short_description = _("datasources")

    def nr_of_styles(self, obj):
        """Return number of styles."""
        return obj.styles.count()
    nr_of_styles.allow_tags=False
    nr_of_styles.short_description = _("styles")

    def publish_to_geoserver(self, request, queryset):
        # TODO: put geoserver connenction data in settings or DB
        gs = GeoserverClient('localhost', 8123, 'admin', 'geoserver')
        workspace = 'deltaportaal'
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
            Table = create_geo_table(obj.parameter, *variable_columns)
            # - fill this table with the correct values
            raw_rows = defaultdict(dict)
            for datasource in datasources:
                # make fill_value NULL in database
                ds = get_dataset(datasource.dataset.dataset_url)
                year = datasource.dataset.year
                scenario = datasource.dataset.scenario
                variable_name = datasource.variable.name
                fill_value = ds[variable_name].attributes.get(
                    '_FillValue')
                x_values = ds['x'][:]  # [:] loads the data
                y_values = ds['y'][:]
                values = ds[variable_name][:]
                # create insertable rows
                for i in range(len(x_values)):
                    x = x_values[i]
                    y = y_values[i]
                    # RD srid (lizard_map/coordinates)
                    point = Point(x, y, srid=28992)
                    value = values[i]
                    if value == fill_value:
                        value = None
                        if int(x) == 0  and int(y) == 0:
                            # skip x = 0.0, y = 0.0 and no value,
                            continue
                    row_key = (point, year, scenario)
                    raw_rows[row_key][variable_name] = value
            inserts = []
            for row_key, variables in raw_rows.items():
                point, year, scenario = row_key
                t = Table()
                # need to cast this point to a WKTSpatialElement with the
                # RD (28992) srid for GeoAlchemy
                t.geom = WKTSpatialElement(point.wkt, 28992,
                                           geometry_type='POINT')
                t.zichtjaar = year
                t.scenario = scenario
                # add variables
                for var, value in variables.items():
                    if value is not None:
                        value = float(value)  # to cast a numpy.float32 to float
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
            # - check for datastore 'deltaportaal', if it does not exist,
            #   create it with the correct connection parameters (from django.conf.settings?):
            datastore = 'dpnetcdf'
            # TODO; set connection_parameters in django settings
            connection_parameters = settings.GEO_DATABASE_CONFIG
            gs.create_datastore(workspace, datastore, connection_parameters)
            # - create feature type (or layer), based on this map layer with
            #   the correct sql query:
            sql_query = 'SELECT * FROM %s' % obj.parameter
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
admin.site.register(Value, ValueAdmin)
admin.site.register(Geometry)
admin.site.register(MapLayer, MapLayerAdmin)
admin.site.register(Style)
admin.site.register(Datasource)
admin.site.register(ShapeFile)
