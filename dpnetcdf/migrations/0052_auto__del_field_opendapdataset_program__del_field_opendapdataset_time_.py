# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'OpendapDataset.program'
        db.delete_column('dpnetcdf_opendapdataset', 'program')

        # Deleting field 'OpendapDataset.time_zero'
        db.delete_column('dpnetcdf_opendapdataset', 'time_zero')

        # Deleting field 'OpendapDataset.calculation_facility'
        db.delete_column('dpnetcdf_opendapdataset', 'calculation_facility')

        # Deleting field 'OpendapDataset.year'
        db.delete_column('dpnetcdf_opendapdataset', 'year')

        # Deleting field 'OpendapDataset.scenario'
        db.delete_column('dpnetcdf_opendapdataset', 'scenario')

        # Deleting field 'OpendapDataset.strategy'
        db.delete_column('dpnetcdf_opendapdataset', 'strategy')


    def backwards(self, orm):
        # Adding field 'OpendapDataset.program'
        db.add_column('dpnetcdf_opendapdataset', 'program',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True),
                      keep_default=False)

        # Adding field 'OpendapDataset.time_zero'
        db.add_column('dpnetcdf_opendapdataset', 'time_zero',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'OpendapDataset.calculation_facility'
        db.add_column('dpnetcdf_opendapdataset', 'calculation_facility',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'OpendapDataset.year'
        db.add_column('dpnetcdf_opendapdataset', 'year',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'OpendapDataset.scenario'
        db.add_column('dpnetcdf_opendapdataset', 'scenario',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)

        # Adding field 'OpendapDataset.strategy'
        db.add_column('dpnetcdf_opendapdataset', 'strategy',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True),
                      keep_default=False)


    models = {
        'dpnetcdf.datasource': {
            'Meta': {'object_name': 'Datasource'},
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.OpendapDataset']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shape_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.ShapeFile']", 'null': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.Variable']", 'null': 'True'})
        },
        'dpnetcdf.maplayer': {
            'Meta': {'object_name': 'MapLayer'},
            'datasources': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dpnetcdf.Datasource']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameter': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shape_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dpnetcdf.ShapeFile']", 'null': 'True'}),
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