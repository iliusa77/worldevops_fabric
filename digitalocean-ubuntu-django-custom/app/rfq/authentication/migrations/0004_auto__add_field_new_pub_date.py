# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'New.pub_date'
        db.add_column(u'authentication_new', 'pub_date',
                      self.gf('django.db.models.fields.DateField')(auto_now=True, default=datetime.datetime(2014, 10, 10, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'New.pub_date'
        db.delete_column(u'authentication_new', 'pub_date')


    models = {
        u'authentication.new': {
            'Meta': {'object_name': 'New'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['authentication']