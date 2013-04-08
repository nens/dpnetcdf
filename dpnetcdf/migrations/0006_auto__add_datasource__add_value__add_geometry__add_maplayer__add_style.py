# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Datasource'
        db.create_table('dpnetcdf_datasource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('variable', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('imported', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('dpnetcdf', ['Datasource'])

        # Adding M2M table for field geometries on 'Datasource'
        db.create_table('dpnetcdf_datasource_geometries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datasource', models.ForeignKey(orm['dpnetcdf.datasource'], null=False)),
            ('geometry', models.ForeignKey(orm['dpnetcdf.geometry'], null=False))
        ))
        db.create_unique('dpnetcdf_datasource_geometries', ['datasource_id', 'geometry_id'])

        # Adding model 'Value'
        db.create_table('dpnetcdf_value', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datasource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dpnetcdf.Datasource'])),
            ('geometry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dpnetcdf.Geometry'])),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('dpnetcdf', ['Value'])

        # Adding model 'Geometry'
        db.create_table('dpnetcdf_geometry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('dpnetcdf', ['Geometry'])

        # Adding model 'MapLayer'
        db.create_table('dpnetcdf_maplayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parameter', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('dpnetcdf', ['MapLayer'])

        # Adding M2M table for field styles on 'MapLayer'
        db.create_table('dpnetcdf_maplayer_styles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('maplayer', models.ForeignKey(orm['dpnetcdf.maplayer'], null=False)),
            ('style', models.ForeignKey(orm['dpnetcdf.style'], null=False))
        ))
        db.create_unique('dpnetcdf_maplayer_styles', ['maplayer_id', 'style_id'])

        # Adding model 'Style'
        db.create_table('dpnetcdf_style', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('xml', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('dpnetcdf', ['Style'])


    def backwards(self, orm):
        # Deleting model 'Datasource'
        db.delete_table('dpnetcdf_datasource')

        # Removing M2M table for field geometries on 'Datasource'
        db.delete_table('dpnetcdf_datasource_geometries')

        # Deleting model 'Value'
        db.delete_table('dpnetcdf_value')

        # Deleting model 'Geometry'
        db.delete_table('dpnetcdf_geometry')

        # Deleting model 'MapLayer'
        db.delete_table('dpnetcdf_maplayer')

        # Removing M2M table for field styles on 'MapLayer'
        db.delete_table('dpnetcdf_maplayer_styles')

        # Deleting model 'Style'
        db.delete_table('dpnetcdf_style')


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
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
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
        }
    }

    complete_apps = ['dpnetcdf']