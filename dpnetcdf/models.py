# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.db import models
from django.utils.translation import ugettext_lazy as _

# which models do I need
# ----------------------
# DataSource
# ShapeFile
# Geometry
# Value
# Layer
# Style
# XMLField


class NetCDFDataset(models.Model):
    url = models.URLField(verify_exists=False)
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=10, blank=True)
    date = models.DateTimeField()
