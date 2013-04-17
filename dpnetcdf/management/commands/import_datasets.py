# -*- coding: utf-8 -*-
# Copyright 2011 Nelen & Schuurmans
import os
import sys
from os.path import join

from django.core.management.base import BaseCommand

from dpnetcdf.conf import settings
from dpnetcdf.opendap import fetch_all, root_catalog_url, parse_catalog_urls


class Command(BaseCommand):
    args = ""
    help = ("Import Deltaportaal NetCDF dataset info into OpendapDataset "
            "instances.")

    def handle(self, *args, **options):
        # get base catalog and check if it needs to be created in database
        root_url = root_catalog_url()
        print "root catalog url: %s" % root_url
        subcatalog_data = [cat for cat in parse_catalog_urls(root_url)]
        print
        print "sub catalogs"
        print "------------"
        for sc_data in subcatalog_data:
            print "  - %(name)s (%(url)s)" % sc_data
        # get subcatalog and create if necessary

        # get netcdf dataset info and create if necessary

        # get variables from netcdf

# do not create any of these if they already exist

# get catalog
# get subcatalog
# get netcdf per subcatalog
# get variables from netcdf
