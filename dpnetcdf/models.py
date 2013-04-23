# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.contrib.gis.gdal import DataSource as GDALDataSource
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dpnetcdf.conf import settings
from dpnetcdf.opendap import urlify, get_dataset
from geoserverlib.client import GeoserverClient
from dpnetcdf.alchemy import drop_table
from dpnetcdf.utils import parse_dataset_name


class OpendapCatalog(models.Model):
    # fields can be with or without starting and trailing slashes
    name = models.CharField(max_length=100, blank=True)
    # base_url example: 'http://opendap-dm1.knmi.nl:8080/'
    base_url = models.CharField(max_length=100)
    # service_prefix example: 'deltamodel/Deltaportaal'
    service_prefix = models.CharField(max_length=100)
    # catalog_url example: '/thredds/catalog/'
    catalog_url = models.CharField(max_length=100)
    # opendap_url example: '/thredds/dodsC/'
    opendap_url = models.CharField(max_length=100)
    # http_url example: '/thredds/fileServer/'
    http_url = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("catalog")
        verbose_name_plural = _("catalogs")

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return urlify(self.base_url, self.service_prefix)


class OpendapSubcatalog(models.Model):
    catalog = models.ForeignKey('OpendapCatalog')
    identifier = models.CharField(max_length=30)  # e.g. DPRD

    @property
    def url(self):
        cat = self.catalog
        return urlify(cat.base_url, cat.catalog_url, cat.service_prefix,
                      self.identifier, 'catalog.xml')

    class Meta:
        verbose_name = _("subcatalog")
        verbose_name_plural = _("subcatalogs")

    def __unicode__(self):
        return "%s::%s" % (self.catalog, self.identifier)


class Variable(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("variable")
        verbose_name_plural = _("variables")

    def __unicode__(self):
        return self.name


class OpendapDataset(models.Model):
    catalog = models.ForeignKey('OpendapSubcatalog')
    url = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()

    variables = models.ManyToManyField('Variable')
    # TODO: add `modified` DateTimeField

    @property
    def base_url(self):
        return self.catalog.catalog.base_url

    @property
    def opendap_url(self):
        return self.catalog.catalog.opendap_url

    @property
    def dataset_url(self):
        return urlify(self.base_url, self.opendap_url, self.url)

    def get_params_from_name(self):
        """Parse name params, e.g. time_zero, program, strategy, year,
        scenario, calculation_facility.

        - time_zero example: 199101060440
        - program examples: DPRD, DPR, DPR_maas, DPR_rijn
        - strategy example: S0v1
        - year is a CharField because it can have postfixes like 2100W, example
        2050, 2050G
        - scenario example: RD
        - calculation_facility example: RF1p0p3

        """
        return parse_dataset_name(self.name)

    def load_variables(self):
        dataset = get_dataset(self.dataset_url)
        # For variable names, see:
        # http://opendap-dm1.knmi.nl:8080/thredds/dodsC/deltamodel/\
        # Deltaportaal/DPRD/199101060440_DPRD_S0v1_2100_SW_RF1p0p3.nc.html
        excluded_variables = ['time', 'analysis_time', 'lat', 'lon', 'x', 'y',
                              'station_id', 'station_names']
        var_names = [v for v in dataset.keys() if v not in excluded_variables]
        for var_name in var_names:
            var, _created = Variable.objects.get_or_create(name=var_name)
            if _created:
                self.variables.add(var)
            else:
                if var not in self.variables.all():
                    self.variables.add(var)
        return var_names

    class Meta:
        verbose_name = _("dataset")
        verbose_name_plural = _("datasets")
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Style(models.Model):
    name = models.CharField(max_length=100)
    xml = models.TextField(blank=True)  # the actual style in xml format

    class Meta:
        verbose_name = _("style")
        verbose_name_plural = _("styles")

    def __unicode__(self):
        return self.name


class ShapeFile(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, blank=True)
    # identifier_column is the column that maps to  the netcdf's identifier
    # column name
    identifier = models.CharField(max_length=30, blank=True)

    def get_identifier_geom_map(self):
        ds = GDALDataSource(self.path)
        layer = ds[0]
        identifiers = layer.get_fields(self.identifier)
        geoms = layer.get_geoms()
        result = {}
        for i in range(len(identifiers)):
            result[identifiers[i]] = geoms[i]
        return result

    class Meta:
        verbose_name = _("shapefile")
        verbose_name_plural = _("shapefiles")

    def __unicode__(self):
        return self.name


class Datasource(models.Model):
    dataset = models.ForeignKey('OpendapDataset', null=True)
    # the specific variable from the dataset
    variable = models.ForeignKey('Variable', null=True)
    # datasource specific shape file, can be used for dbf values (
    # to be determined how, is work in progress)
    shape_file = models.ForeignKey('ShapeFile', blank=True, null=True)

    class Meta:
        verbose_name = _("datasource")
        verbose_name_plural = _("datasources")
        ordering = ('dataset__name',)

    def __unicode__(self):
        return "%s (%s)" % (self.dataset, self.variable)


class MapLayer(models.Model):
    # Parameter can be something like waterstand_actueel or chloride. It is
    # the identifier for this map layer and the geoserver layer name.
    parameter = models.CharField(max_length=100, blank=True)
    datasources = models.ManyToManyField(Datasource, blank=True)
    styles = models.ManyToManyField(Style, blank=True)

    shape_file = models.ForeignKey('ShapeFile', blank=True, null=True)

    def delete(self):
        """Deleting the maplayer also deletes the related layer and feature
        type on the GeoServer.

        """
        workspace = settings.NETCDF_WORKSPACE_NAME
        datastore = settings.NETCDF_DATASTORE_NAME
        view = self.parameter
        gs = GeoserverClient(**settings.GEOSERVER_CONFIG)
        gs.delete_layer(view)
        gs.delete_feature_type(workspace, datastore, view)
        # now drop the table as well
        drop_table(self.parameter)
        super(MapLayer, self).delete()

    class Meta:
        verbose_name = _("maplayer")
        verbose_name_plural = _("maplayers")

    def __unicode__(self):
        return self.parameter
