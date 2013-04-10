# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.contrib import admin, messages
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _

from dpnetcdf.models import (OpendapCatalog, OpendapSubcatalog, OpendapDataset,
                             Variable, MapLayer, Datasource, Geometry, Value,
                             Style, ShapeFile)
from dpnetcdf.opendap import parse_dataset_properties, get_dataset
from dpnetcdf.utils import parse_opendap_dataset_name
from geoserverlib.client import GeoserverClient
from dpnetcdf.alchemy import create_geo_table


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

    actions = ['push_to_geoserver']

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

    def push_to_geoserver(self, request, queryset):
        # TODO: put geoserver connenction data in settings or DB
        gs = GeoserverClient('localhost', 8123, 'admin', 'geoserver')
        workspace = 'deltaportaal'
        for obj in queryset:
            # upload to geoserver, how?
            # steps:
            # - create column definitions based on the datasources variables
            datasources = obj.datasources()
            columns = []
            # - create intermediate table with SQLAlchemy
            Table = create_geo_table(obj.parameter)
            # - fill this table with the right values

            # - check for workspace 'deltaportaal', if it does not exist,
            #   create it: client.create_workspace(workspace)
            # - check for datastore 'deltaportaal', if it does not exist,
            #   create it with the correct connection parameters (from django.conf.settings?):
            #   client.create_datastore(workspace, datastore, connection_parameters)
            # - create feature type (or layer), based on this map layer with
            #   the correct sql query:
            #   client.create_feature_type(workspace, datastore, view, sql_query)
            # - create or update style(s) and connect it to this view:
            #   client.create_style(style, style_file)
            #   client.set_default_style(workspace, datastore, view, style)
            pass
    push_to_geoserver.short_description = _("Push to geoserver")

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
