# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.contrib import admin, messages
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _

from dpnetcdf.models import (OpendapCatalog, OpendapSubcatalog, OpendapDataset,
                             Variable)
from dpnetcdf.opendap import parse_dataset_properties, get_dataset
from dpnetcdf.models import Datasource
from dpnetcdf.models import Geometry
from dpnetcdf.models import Value


class OpendapDatasetAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'url', 'name', 'date')
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
                Value.objects.get_or_create(datasource=datasource,
                    geometry=geometry, value=values[i])


class OpendapSubcatalogAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'catalog')

    actions = ['load_datasets']

    def load_datasets(self, request, queryset):
        for obj in queryset:
            datasets_properties = parse_dataset_properties(obj.url)
            count = 0
            for props in datasets_properties:
                dataset, _created = OpendapDataset.objects.get_or_create(
                    catalog=obj, url=props['urlpath'], name=props['name'],
                    defaults={'date': props['timestamp']})
                if _created:
                    count += 1
            msg = _("Created %s datasets for %s" % (count, obj.url))
            messages.info(request, msg)
    load_datasets.short_description = _("Load related datasets")


admin.site.register(OpendapCatalog)
admin.site.register(OpendapSubcatalog, OpendapSubcatalogAdmin)
admin.site.register(OpendapDataset, OpendapDatasetAdmin)
admin.site.register(Variable)
admin.site.register(Value)
admin.site.register(Geometry)
