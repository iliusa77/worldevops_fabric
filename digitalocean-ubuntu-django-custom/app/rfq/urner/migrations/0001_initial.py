# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Product'
        db.create_table(u'urner_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'urner', ['Product'])

        # Adding model 'ProductDetails'
        db.create_table(u'urner_productdetails', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['urner.Product'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'urner', ['ProductDetails'])


    def backwards(self, orm):
        # Deleting model 'Product'
        db.delete_table(u'urner_product')

        # Deleting model 'ProductDetails'
        db.delete_table(u'urner_productdetails')


    models = {
        u'urner.product': {
            'Meta': {'object_name': 'Product'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'urner.productdetails': {
            'Meta': {'object_name': 'ProductDetails'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['urner.Product']"})
        }
    }

    complete_apps = ['urner']