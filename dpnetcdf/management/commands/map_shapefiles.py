# -*- coding: utf-8 -*-
# Copyright 2011 Nelen & Schuurmans
import os
import sys
from os.path import join

from django.core.management.base import BaseCommand

from dpnetcdf.conf import settings
from dpnetcdf.models import ShapeFile


class Command(BaseCommand):
    args = ""
    help = "Map file system based shapefiles to Django model instances."

    def handle(self, *args, **options):
        shape_dir = settings.NETCDF_SHAPE_FILE_DIR
        shape_files = {}
        any_created = 0
        for root, dirs, files in os.walk(shape_dir):
            shp_data = [(name[:-4], join(root, name)) for name in files if
                        name.endswith('.shp')]
            shape_files.update(dict(shp_data))
        for name, path in shape_files.items():
            identifier = 'LOCID'  # for now, this is the only identifier
            sf, _created = ShapeFile.objects.get_or_create(
                name=name, path=path, identifier=identifier)
            if _created:
                any_created += 1
                sys.stdout.write("created ShapeFile instance: %s\n" % sf)
        if not any_created:
            sys.stdout.write("no new ShapeFile instances created\n")
