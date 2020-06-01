# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Remarks'
        db.create_table(u'quote_remarks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rfq', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.QuoteInfo'], null=True, blank=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('remark', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal(u'quote', ['Remarks'])

        # Adding model 'Destination'
        db.create_table(u'quote_destination', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'quote', ['Destination'])

        # Adding model 'Alert'
        db.create_table(u'quote_alert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('to_user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('from_user', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='from_user', unique=True, null=True, to=orm['auth.User'])),
            ('itm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.QuoteItem'], null=True, blank=True)),
            ('alert', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'quote', ['Alert'])


        # Renaming column for 'LocationRelation.destination' to match new field type.
        db.rename_column(u'quote_locationrelation', 'destination', 'destination_id')
        # Changing field 'LocationRelation.destination'
        db.alter_column(u'quote_locationrelation', 'destination_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Destination'], null=True))
        # Adding index on 'LocationRelation', fields ['destination']
        db.create_index(u'quote_locationrelation', ['destination_id'])

        # Adding field 'QuoteInfo.po'
        db.add_column(u'quote_quoteinfo', 'po',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'QuoteInfo.container_number'
        db.add_column(u'quote_quoteinfo', 'container_number',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'QuoteInfo.alert'
        db.add_column(u'quote_quoteinfo', 'alert',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'QuoteInfo.status'
        db.add_column(u'quote_quoteinfo', 'status',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=100),
                      keep_default=False)

        # Adding field 'QuoteInfo.approver_remarks'
        db.add_column(u'quote_quoteinfo', 'approver_remarks',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'QuoteInfo.requester_remarks'
        db.add_column(u'quote_quoteinfo', 'requester_remarks',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'QuoteInfo.final_approver_remarks'
        db.add_column(u'quote_quoteinfo', 'final_approver_remarks',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


        # Renaming column for 'QuoteInfo.destination' to match new field type.
        db.rename_column(u'quote_quoteinfo', 'destination', 'destination_id')
        # Changing field 'QuoteInfo.destination'
        db.alter_column(u'quote_quoteinfo', 'destination_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Destination'], null=True))
        # Adding index on 'QuoteInfo', fields ['destination']
        db.create_index(u'quote_quoteinfo', ['destination_id'])


        # Changing field 'QuoteInfo.packer'
        db.alter_column(u'quote_quoteinfo', 'packer_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Packer'], null=True))

        # Changing field 'QuoteInfo.delivery_date'
        db.alter_column(u'quote_quoteinfo', 'delivery_date', self.gf('django.db.models.fields.DateField')(null=True))
        # Deleting field 'QuoteItem.requester_remarks'
        db.delete_column(u'quote_quoteitem', 'requester_remarks')

        # Deleting field 'QuoteItem.container_number'
        db.delete_column(u'quote_quoteitem', 'container_number')

        # Deleting field 'QuoteItem.po'
        db.delete_column(u'quote_quoteitem', 'po')

        # Deleting field 'QuoteItem.status'
        db.delete_column(u'quote_quoteitem', 'status')

        # Deleting field 'QuoteItem.alert'
        db.delete_column(u'quote_quoteitem', 'alert')

        # Deleting field 'QuoteItem.approver_remarks'
        db.delete_column(u'quote_quoteitem', 'approver_remarks')

        # Deleting field 'QuoteItem.final_approver_remarks'
        db.delete_column(u'quote_quoteitem', 'final_approver_remarks')


    def backwards(self, orm):
        # Removing index on 'QuoteInfo', fields ['destination']
        db.delete_index(u'quote_quoteinfo', ['destination_id'])

        # Removing index on 'LocationRelation', fields ['destination']
        db.delete_index(u'quote_locationrelation', ['destination_id'])

        # Deleting model 'Remarks'
        db.delete_table(u'quote_remarks')

        # Deleting model 'Destination'
        db.delete_table(u'quote_destination')

        # Deleting model 'Alert'
        db.delete_table(u'quote_alert')


        # Renaming column for 'LocationRelation.destination' to match new field type.
        db.rename_column(u'quote_locationrelation', 'destination_id', 'destination')
        # Changing field 'LocationRelation.destination'
        db.alter_column(u'quote_locationrelation', 'destination', self.gf('django.db.models.fields.CharField')(default=None, max_length=20))
        # Deleting field 'QuoteInfo.po'
        db.delete_column(u'quote_quoteinfo', 'po')

        # Deleting field 'QuoteInfo.container_number'
        db.delete_column(u'quote_quoteinfo', 'container_number')

        # Deleting field 'QuoteInfo.alert'
        db.delete_column(u'quote_quoteinfo', 'alert')

        # Deleting field 'QuoteInfo.status'
        db.delete_column(u'quote_quoteinfo', 'status')

        # Deleting field 'QuoteInfo.approver_remarks'
        db.delete_column(u'quote_quoteinfo', 'approver_remarks')

        # Deleting field 'QuoteInfo.requester_remarks'
        db.delete_column(u'quote_quoteinfo', 'requester_remarks')

        # Deleting field 'QuoteInfo.final_approver_remarks'
        db.delete_column(u'quote_quoteinfo', 'final_approver_remarks')


        # Renaming column for 'QuoteInfo.destination' to match new field type.
        db.rename_column(u'quote_quoteinfo', 'destination_id', 'destination')
        # Changing field 'QuoteInfo.destination'
        db.alter_column(u'quote_quoteinfo', 'destination', self.gf('django.db.models.fields.CharField')(default=None, max_length=20))

        # Changing field 'QuoteInfo.packer'
        db.alter_column(u'quote_quoteinfo', 'packer_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['quote.Packer']))

        # Changing field 'QuoteInfo.delivery_date'
        db.alter_column(u'quote_quoteinfo', 'delivery_date', self.gf('django.db.models.fields.DateField')(default=None))
        # Adding field 'QuoteItem.requester_remarks'
        db.add_column(u'quote_quoteitem', 'requester_remarks',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'QuoteItem.container_number'
        db.add_column(u'quote_quoteitem', 'container_number',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'QuoteItem.po'
        db.add_column(u'quote_quoteitem', 'po',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'QuoteItem.status'
        db.add_column(u'quote_quoteitem', 'status',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=100),
                      keep_default=False)

        # Adding field 'QuoteItem.alert'
        db.add_column(u'quote_quoteitem', 'alert',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'QuoteItem.approver_remarks'
        db.add_column(u'quote_quoteitem', 'approver_remarks',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'QuoteItem.final_approver_remarks'
        db.add_column(u'quote_quoteitem', 'final_approver_remarks',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'quote.alert': {
            'Meta': {'object_name': 'Alert'},
            'alert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'from_user': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'from_user'", 'unique': 'True', 'null': 'True', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.QuoteItem']", 'null': 'True', 'blank': 'True'}),
            'to_user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'quote.brand': {
            'Meta': {'object_name': 'Brand'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'quote.customer': {
            'Meta': {'object_name': 'Customer'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'quote.destination': {
            'Meta': {'object_name': 'Destination'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'quote.item': {
            'Meta': {'object_name': 'Item'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'quote.locationrelation': {
            'Meta': {'object_name': 'LocationRelation'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Customer']", 'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Destination']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'packer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Packer']", 'null': 'True', 'blank': 'True'})
        },
        u'quote.pack': {
            'Meta': {'object_name': 'Pack'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pack': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'quote.packer': {
            'Meta': {'object_name': 'Packer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'quote.quoteinfo': {
            'Meta': {'object_name': 'QuoteInfo'},
            'alert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approver_remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'container_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Customer']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'delivery_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Destination']", 'null': 'True', 'blank': 'True'}),
            'final_approver_remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['quote.QuoteItem']", 'symmetrical': 'False'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'office_location': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'packer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Packer']", 'null': 'True', 'blank': 'True'}),
            'po': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'port_of_delivery': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'requester_remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'specifications': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'terms_of_purchase': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'terms_of_sale': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'type_of_delivery': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'valid_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'quote.quoteitem': {
            'Meta': {'object_name': 'QuoteItem'},
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Brand']"}),
            'cases': ('django.db.models.fields.IntegerField', [], {}),
            'counter_offer': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'final_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'gross_profit': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indication_selling_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Item']"}),
            'pack': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Pack']"}),
            'quantity_in_lbs': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'quoted_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Size']"})
        },
        u'quote.remarks': {
            'Meta': {'object_name': 'Remarks'},
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'rfq': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.QuoteInfo']", 'null': 'True', 'blank': 'True'})
        },
        u'quote.size': {
            'Meta': {'object_name': 'Size'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'quote.terms': {
            'Meta': {'object_name': 'Terms'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['quote']