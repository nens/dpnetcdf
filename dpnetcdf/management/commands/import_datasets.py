# -*- coding: utf-8 -*-
# Copyright 2011 Nelen & Schuurmans
from django.core.management.base import BaseCommand

from dpnetcdf.opendap import (parse_catalog_urls, urlify,
                              parse_dataset_properties)
from dpnetcdf.models import OpendapCatalog
from dpnetcdf.models import OpendapSubcatalog, OpendapDataset


class Command(BaseCommand):
    args = ""
    help = ("Import Deltaportaal NetCDF dataset info into OpendapDataset "
            "instances.")

    def handle(self, *args, **options):
        root_catalog_params = {
            'name': 'Deltaportaal',
            'base_url': 'http://opendap-dm1.knmi.nl:8080/',
            'service_prefix': 'deltamodel/Deltaportaal',
            'catalog_url': '/thredds/catalog/',
            'opendap_url': '/thredds/dodsC/',
            'http_url': '/thredds/fileServer/'
        }
        rcp = root_catalog_params
        catalog, _created = OpendapCatalog.objects.get_or_create(
            name=rcp['name'], defaults=rcp)
        status = "created" if _created else "exists"
        root_url = urlify(catalog.base_url, catalog.catalog_url,
                          catalog.service_prefix, 'catalog.xml')
        print "base catalog url: %s (%s)" % (root_url, status)
        print
        print "sub catalogs"
        print "------------"
        for sc in parse_catalog_urls(root_url):
            # check if it exists
            sub_catalog, _created = OpendapSubcatalog.objects.get_or_create(
                catalog=catalog, identifier=sc['name'])
            status = "created" if _created else "exists"
            print "  - %(name)s (%(url)s) (%(status)s)" % {
                'name': sub_catalog.identifier, 'url': sub_catalog.url,
                'status': status}
            for props in parse_dataset_properties(
                    sub_catalog.url):
                dataset, _created = OpendapDataset.objects.get_or_create(
                    name=props['name'], defaults={'catalog': sub_catalog,
                                                  'url': props['url'],
                                                  'date': props['date']})
                status = "+" if _created else "="
                print "    %s dataset '%s'" % (status, dataset.name)
                if not _created:
                    if not props['date'] == dataset.date:
                        dataset.date = props['date']  # update date
                        dataset.save()
                # load/update variables for this dataset
                dataset.load_variables()
