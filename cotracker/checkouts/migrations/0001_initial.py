# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Airstrip'
        db.create_table(u'checkouts_airstrip', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('ident', self.gf('django.db.models.fields.CharField')(unique=True, max_length=4)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_base', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'checkouts', ['Airstrip'])

        # Adding M2M table for field bases on 'Airstrip'
        db.create_table(u'checkouts_airstrip_bases', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_airstrip', models.ForeignKey(orm[u'checkouts.airstrip'], null=False)),
            ('to_airstrip', models.ForeignKey(orm[u'checkouts.airstrip'], null=False))
        ))
        db.create_unique(u'checkouts_airstrip_bases', ['from_airstrip_id', 'to_airstrip_id'])

        # Adding model 'AircraftType'
        db.create_table(u'checkouts_aircrafttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'checkouts', ['AircraftType'])

        # Adding model 'Checkout'
        db.create_table(u'checkouts_checkout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('pilot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('airstrip', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checkouts.Airstrip'])),
            ('aircraft_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['checkouts.AircraftType'])),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'checkouts', ['Checkout'])

        # Adding unique constraint on 'Checkout', fields ['pilot', 'airstrip', 'aircraft_type']
        db.create_unique(u'checkouts_checkout', ['pilot_id', 'airstrip_id', 'aircraft_type_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Checkout', fields ['pilot', 'airstrip', 'aircraft_type']
        db.delete_unique(u'checkouts_checkout', ['pilot_id', 'airstrip_id', 'aircraft_type_id'])

        # Deleting model 'Airstrip'
        db.delete_table(u'checkouts_airstrip')

        # Removing M2M table for field bases on 'Airstrip'
        db.delete_table('checkouts_airstrip_bases')

        # Deleting model 'AircraftType'
        db.delete_table(u'checkouts_aircrafttype')

        # Deleting model 'Checkout'
        db.delete_table(u'checkouts_checkout')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'checkouts.aircrafttype': {
            'Meta': {'object_name': 'AircraftType'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'checkouts.airstrip': {
            'Meta': {'object_name': 'Airstrip'},
            'bases': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['checkouts.Airstrip']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ident': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4'}),
            'is_base': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'checkouts.checkout': {
            'Meta': {'unique_together': "(('pilot', 'airstrip', 'aircraft_type'),)", 'object_name': 'Checkout'},
            'aircraft_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['checkouts.AircraftType']"}),
            'airstrip': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['checkouts.Airstrip']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'pilot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['checkouts']