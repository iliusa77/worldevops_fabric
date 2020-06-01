# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Yields'
        db.create_table(u'raw_materials_yields', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Item'])),
            ('percentage', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'raw_materials', ['Yields'])

        # Adding model 'OtherPrice'
        db.create_table(u'raw_materials_otherprice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('yields', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['raw_materials.Yields'])),
            ('size', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Size'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'raw_materials', ['OtherPrice'])

        # Adding model 'Rates'
        db.create_table(u'raw_materials_rates', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('expense', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'raw_materials', ['Rates'])


    def backwards(self, orm):
        # Deleting model 'Yields'
        db.delete_table(u'raw_materials_yields')

        # Deleting model 'OtherPrice'
        db.delete_table(u'raw_materials_otherprice')

        # Deleting model 'Rates'
        db.delete_table(u'raw_materials_rates')


    models = {
        u'quote.item': {
            'Meta': {'object_name': 'Item'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'quote.size': {
            'Meta': {'object_name': 'Size'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'raw_materials.otherprice': {
            'Meta': {'object_name': 'OtherPrice'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Size']"}),
            'yields': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['raw_materials.Yields']"})
        },
        u'raw_materials.rates': {
            'Meta': {'object_name': 'Rates'},
            'expense': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        u'raw_materials.yields': {
            'Meta': {'object_name': 'Yields'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Item']"}),
            'percentage': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        }
    }

    complete_apps = ['raw_materials']