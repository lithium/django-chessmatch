# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PieceMove'
        db.create_table('chessmatch_piecemove', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('piece_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chessmatch.PieceType'])),
            ('move_m', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('move_n', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('move_v', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('can_capture', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('initial_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('chessmatch', ['PieceMove'])

        # Adding model 'PieceType'
        db.create_table('chessmatch_piecetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='piecetype_created', null=True, blank=True, to=orm['auth.User'])),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='piecetype_updated', null=True, blank=True, to=orm['auth.User'])),
            ('ascii_glyph', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('unicode_glyph', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('rotation', self.gf('django.db.models.fields.CharField')(default=0, max_length=32, blank=True)),
        ))
        db.send_create_signal('chessmatch', ['PieceType'])


    def backwards(self, orm):
        
        # Deleting model 'PieceMove'
        db.delete_table('chessmatch_piecemove')

        # Deleting model 'PieceType'
        db.delete_table('chessmatch_piecetype')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'chessmatch.boardsetup': {
            'Meta': {'object_name': 'BoardSetup'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'boardsetup_created'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'max_players': ('django.db.models.fields.PositiveIntegerField', [], {'default': '4'}),
            'min_players': ('django.db.models.fields.PositiveIntegerField', [], {'default': '4'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'num_cols': ('django.db.models.fields.PositiveIntegerField', [], {'default': '14'}),
            'num_rows': ('django.db.models.fields.PositiveIntegerField', [], {'default': '14'}),
            'pieces': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'squares': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'boardsetup_updated'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"})
        },
        'chessmatch.boardsetupcolor': {
            'Meta': {'ordering': "('turn_order',)", 'object_name': 'BoardSetupColor'},
            'board_setup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.BoardSetup']"}),
            'color': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.PieceColor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pawn_vector': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '2'}),
            'turn_order': ('django.db.models.fields.IntegerField', [], {})
        },
        'chessmatch.game': {
            'Meta': {'object_name': 'Game'},
            'board_setup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.BoardSetup']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'game_created'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'started_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'turn_color': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'turn_number': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'game_updated'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'games_won'", 'null': 'True', 'blank': 'True', 'to': "orm['chessmatch.GamePlayer']"})
        },
        'chessmatch.gameaction': {
            'Meta': {'ordering': "('turn', 'color')", 'object_name': 'GameAction'},
            'color': ('django.db.models.fields.IntegerField', [], {}),
            'from_coord': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_capture': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'piece': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'to_coord': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'turn': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'chessmatch.gameplayer': {
            'Meta': {'ordering': "('turn_order',)", 'object_name': 'GamePlayer'},
            'color': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.PieceColor']", 'null': 'True', 'blank': 'True'}),
            'controller': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['chessmatch.GamePlayer']", 'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_playing': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.Player']"}),
            'turn_order': ('django.db.models.fields.IntegerField', [], {'default': '-1'})
        },
        'chessmatch.piececolor': {
            'Meta': {'object_name': 'PieceColor'},
            'hexvalue': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'letter': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'chessmatch.piecemove': {
            'Meta': {'object_name': 'PieceMove'},
            'can_capture': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'move_m': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'move_n': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'move_v': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'piece_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.PieceType']"})
        },
        'chessmatch.piecetype': {
            'Meta': {'object_name': 'PieceType'},
            'ascii_glyph': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'piecetype_created'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'rotation': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '32', 'blank': 'True'}),
            'unicode_glyph': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'piecetype_updated'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"})
        },
        'chessmatch.player': {
            'Meta': {'object_name': 'Player'},
            'avatar_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'notify_after': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'notify_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'ranking': ('django.db.models.fields.IntegerField', [], {'default': '1500'}),
            'twitter_access_token': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'twitter_name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'twitter_profile_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'twitter_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['chessmatch']
