# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Product.name'
        db.alter_column(u'urner_product', 'name', self.gf('django.db.models.fields.CharField')(max_length=700))

    def backwards(self, orm):

        # Changing field 'Product.name'
        db.alter_column(u'urner_product', 'name', self.gf('django.db.models.fields.CharField')(max_length=500))

    models = {
        u'urner.product': {
            'Meta': {'object_name': 'Product'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '700'})
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