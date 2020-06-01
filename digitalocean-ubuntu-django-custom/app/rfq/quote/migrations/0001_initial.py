# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Customer'
        db.create_table(u'quote_customer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'quote', ['Customer'])

        # Adding model 'Packer'
        db.create_table(u'quote_packer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'quote', ['Packer'])

        # Adding model 'Terms'
        db.create_table(u'quote_terms', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'quote', ['Terms'])

        # Adding model 'Item'
        db.create_table(u'quote_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'quote', ['Item'])

        # Adding model 'Size'
        db.create_table(u'quote_size', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('size', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'quote', ['Size'])

        # Adding model 'Pack'
        db.create_table(u'quote_pack', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pack', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'quote', ['Pack'])

        # Adding model 'Brand'
        db.create_table(u'quote_brand', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'quote', ['Brand'])

        # Adding model 'QuoteItem'
        db.create_table(u'quote_quoteitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Item'])),
            ('size', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Size'])),
            ('pack', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Pack'])),
            ('brand', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Brand'])),
            ('cases', self.gf('django.db.models.fields.IntegerField')()),
            ('quantity_in_lbs', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('indication_selling_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('selling_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('quoted_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('final_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('counter_offer', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('po', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('container_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('gross_profit', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('approver_remarks', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('requester_remarks', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('final_approver_remarks', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('alert', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'quote', ['QuoteItem'])

        # Adding model 'QuoteInfo'
        db.create_table(u'quote_quoteinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('office_location', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('requester', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('packer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Packer'])),
            ('terms_of_purchase', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('item_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quote.Customer'], null=True, blank=True)),
            ('terms_of_sale', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('delivery_date', self.gf('django.db.models.fields.DateField')()),
            ('valid_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'quote', ['QuoteInfo'])

        # Adding M2M table for field items on 'QuoteInfo'
        m2m_table_name = db.shorten_name(u'quote_quoteinfo_items')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('quoteinfo', models.ForeignKey(orm[u'quote.quoteinfo'], null=False)),
            ('quoteitem', models.ForeignKey(orm[u'quote.quoteitem'], null=False))
        ))
        db.create_unique(m2m_table_name, ['quoteinfo_id', 'quoteitem_id'])


    def backwards(self, orm):
        # Deleting model 'Customer'
        db.delete_table(u'quote_customer')

        # Deleting model 'Packer'
        db.delete_table(u'quote_packer')

        # Deleting model 'Terms'
        db.delete_table(u'quote_terms')

        # Deleting model 'Item'
        db.delete_table(u'quote_item')

        # Deleting model 'Size'
        db.delete_table(u'quote_size')

        # Deleting model 'Pack'
        db.delete_table(u'quote_pack')

        # Deleting model 'Brand'
        db.delete_table(u'quote_brand')

        # Deleting model 'QuoteItem'
        db.delete_table(u'quote_quoteitem')

        # Deleting model 'QuoteInfo'
        db.delete_table(u'quote_quoteinfo')

        # Removing M2M table for field items on 'QuoteInfo'
        db.delete_table(db.shorten_name(u'quote_quoteinfo_items'))


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
        u'quote.item': {
            'Meta': {'object_name': 'Item'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Customer']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'delivery_date': ('django.db.models.fields.DateField', [], {}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['quote.QuoteItem']", 'symmetrical': 'False'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'office_location': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'packer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Packer']"}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'terms_of_purchase': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'terms_of_sale': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'valid_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'quote.quoteitem': {
            'Meta': {'object_name': 'QuoteItem'},
            'alert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approver_remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Brand']"}),
            'cases': ('django.db.models.fields.IntegerField', [], {}),
            'container_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'counter_offer': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'final_approver_remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'final_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'gross_profit': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indication_selling_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Item']"}),
            'pack': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Pack']"}),
            'po': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'quantity_in_lbs': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'quoted_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'requester_remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'selling_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quote.Size']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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