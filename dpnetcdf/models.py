# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.contrib.gis.db.models import GeometryField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dpnetcdf.opendap import urlify, get_dataset


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

    # Deltaportaal specific fields derived from file name
    # time_zero example: 199101060440
    time_zero = models.CharField(max_length=20, blank=True)
    # program examples: DPRD, DPR, DPR_maas, DPR_rijn
    program = models.CharField(max_length=30, blank=True)
    strategy = models.CharField(max_length=10, blank=True)  # e.g. S0v1
    # year is a CharField because it can have postfixes like 2100W
    year = models.CharField(max_length=10, blank=True)  # e.g. 2050, 2050G
    scenario = models.CharField(max_length=10, blank=True)  # e.g. RD
    # calculation_facility example: RF1p0p3
    calculation_facility = models.CharField(max_length=10, blank=True)

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

    def update_variables(self):
        dataset = get_dataset(self.dataset_url)
        # TODO: make variable 'mapper' more future proof
        var_names = [v for v in dataset.keys() if 'actueel' in v]
        for var_name in var_names:
            var, _created = Variable.objects.get_or_create(name=var_name)
            if _created:
                self.variables.add(var)
        return var_names

    class Meta:
        verbose_name = _("dataset")
        verbose_name_plural = _("datasets")

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


class Geometry(models.Model):
    """Base geometry field primarily for holding points, lines, etc."""
    geometry = GeometryField()

    class Meta:
        verbose_name = _("geometry")
        verbose_name_plural = _("geometries")

    def __unicode__(self):
        return unicode(self.geometry)


class Datasource(models.Model):
    dataset = models.ForeignKey('OpendapDataset', null=True)
    # the specific variable from the dataset
    variable = models.ForeignKey('Variable', null=True)
    imported = models.DateTimeField(blank=True, null=True)

    geometries = models.ManyToManyField('Geometry', blank=True)

    class Meta:
        verbose_name = _("datasource")
        verbose_name_plural = _("datasources")

    def __unicode__(self):
        return "%s (%s)" % (self.dataset, self.variable)


class MapLayer(models.Model):
    # Parameter can be something like waterstand_actueel or chloride. It is
    # the identifier for this map layer.
    parameter = models.CharField(max_length=100, blank=True)
    datasources = models.ManyToManyField(Datasource, blank=True)
    styles = models.ManyToManyField(Style, blank=True)

    class Meta:
        verbose_name = _("maplayer")
        verbose_name_plural = _("maplayers")

    def __unicode__(self):
        return self.parameter


class Value(models.Model):
    datasource = models.ForeignKey('Datasource')
    geometry = models.ForeignKey('Geometry')
    # value could be a char or boolean perhaps
    value = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("value")
        verbose_name_plural = _("values")
        ordering = ('geometry',)

    def __unicode__(self):
        return "%s - %s: %s" % (self.datasource, self.geometry, self.value)
