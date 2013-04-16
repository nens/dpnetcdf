# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing M2M table for field geometries on 'Datasource'
        db.delete_table('dpnetcdf_datasource_geometries')


    def backwards(self, orm):
        # Adding M2M table for field geometries on 'Datasource'
        db.create_table('dpnetcdf_datasource_geometries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datasource', models.ForeignKey(orm['dpnetcdf.datasource'], null=False)),
            ('geometry', models.ForeignKey(orm['dpnetcdf.geometry'], null=False))
        ))
        db.create_unique('dpnetcdf_datasource_geometries', ['datasource_id', 'geometry_id'])


    models = {
        'dpnetcdf.datasource': {
            'Meta': {'object_name': 'Datasource'},
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.OpendapDataset']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.Variable']", 'null': 'True'})
        },
        'dpnetcdf.geometry': {
            'Meta': {'object_name': 'Geometry'},
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'dpnetcdf.maplayer': {
            'Meta': {'object_name': 'MapLayer'},
            'datasources': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dpnetcdf.Datasource']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameter': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
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
            'Meta': {'object_name': 'OpendapDataset'},
            'calculation_facility': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.OpendapSubcatalog']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'program': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'scenario': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'strategy': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'time_zero': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'variables': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dpnetcdf.Variable']", 'symmetrical': 'False'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shape_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'dpnetcdf.style': {
            'Meta': {'object_name': 'Style'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'xml': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'dpnetcdf.value': {
            'Meta': {'ordering': "(u'geometry',)", 'object_name': 'Value'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.Datasource']"}),
            'geometry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.Geometry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'dpnetcdf.variable': {
            'Meta': {'object_name': 'Variable'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['dpnetcdf']