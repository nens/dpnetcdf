# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'NetCDFDataset.netcdf'
        db.add_column('dpnetcdf_netcdfdataset', 'netcdf',
                      self.gf('django.db.models.fields.FilePathField')(max_length=100, path='/tmp/netcdfs', null=True, match=u'.*\\.nc$', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'NetCDFDataset.netcdf'
        db.delete_column('dpnetcdf_netcdfdataset', 'netcdf')


    models = {
        'dpnetcdf.netcdfdataset': {
            'Meta': {'object_name': 'NetCDFDataset'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'netcdf': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'path': "'/tmp/netcdfs'", 'null': 'True', 'match': "u'.*\\\\.nc$'", 'blank': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['dpnetcdf']