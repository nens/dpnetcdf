# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'OpendapCatalog.serivce_prefix'
        db.delete_column('dpnetcdf_opendapcatalog', 'serivce_prefix')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'OpendapCatalog.serivce_prefix'
        raise RuntimeError("Cannot reverse this migration. 'OpendapCatalog.serivce_prefix' and its values cannot be restored.")

    models = {
        'dpnetcdf.datasource': {
            'Meta': {'object_name': 'Datasource'},
            'geometries': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dpnetcdf.Geometry']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported': ('django.db.models.fields.DateTimeField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'variable': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dpnetcdf.geometry': {
            'Meta': {'object_name': 'Geometry'},
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'dpnetcdf.maplayer': {
            'Meta': {'object_name': 'MapLayer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameter': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dpnetcdf.Style']", 'symmetrical': 'False'})
        },
        'dpnetcdf.netcdfdataset': {
            'Meta': {'object_name': 'NetCDFDataset'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'variables': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dpnetcdf.Variable']", 'symmetrical': 'False'})
        },
        'dpnetcdf.opendapcatalog': {
            'Meta': {'object_name': 'OpendapCatalog'},
            'base_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'catalog_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'http_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opendap_url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dpnetcdf.style': {
            'Meta': {'object_name': 'Style'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'xml': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'dpnetcdf.value': {
            'Meta': {'object_name': 'Value'},
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.Datasource']"}),
            'geometry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.Geometry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'dpnetcdf.variable': {
            'Meta': {'object_name': 'Variable'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['dpnetcdf']