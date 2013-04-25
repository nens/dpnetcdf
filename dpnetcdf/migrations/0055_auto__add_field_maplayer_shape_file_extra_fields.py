# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'MapLayer.shape_file_extra_fields'
        db.add_column('dpnetcdf_maplayer', 'shape_file_extra_fields',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=512, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'MapLayer.shape_file_extra_fields'
        db.delete_column('dpnetcdf_maplayer', 'shape_file_extra_fields')


    models = {
        'dpnetcdf.datasource': {
            'Meta': {'ordering': "(u'dataset__name',)", 'object_name': 'Datasource'},
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.OpendapDataset']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shape_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.ShapeFile']", 'null': 'True', 'blank': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.Variable']", 'null': 'True'})
        },
        'dpnetcdf.maplayer': {
            'Meta': {'object_name': 'MapLayer'},
            'connection_shape_file': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'map_layers'", 'null': 'True', 'to': "orm['dpnetcdf.ShapeFile']"}),
            'datasources': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dpnetcdf.Datasource']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameter': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shape_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.ShapeFile']", 'null': 'True', 'blank': 'True'}),
            'shape_file_extra_fields': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'sql_query': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dpnetcdf.Style']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'dpnetcdf.opendapcatalog': {
            'Meta': {'object_name': 'OpendapCatalog'},
            'base_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'catalog_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'http_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'opendap_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'service_prefix': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dpnetcdf.opendapdataset': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'OpendapDataset'},
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.OpendapSubcatalog']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'variables': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dpnetcdf.Variable']", 'symmetrical': 'False'})
        },
        'dpnetcdf.opendapsubcatalog': {
            'Meta': {'object_name': 'OpendapSubcatalog'},
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.OpendapCatalog']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'dpnetcdf.shapefile': {
            'Meta': {'object_name': 'ShapeFile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'dpnetcdf.style': {
            'Meta': {'object_name': 'Style'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'xml': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'dpnetcdf.variable': {
            'Meta': {'object_name': 'Variable'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['dpnetcdf']