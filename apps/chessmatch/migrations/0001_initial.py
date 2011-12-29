# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PieceColor'
        db.create_table('chessmatch_piececolor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('letter', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1)),
            ('hexvalue', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
        ))
        db.send_create_signal('chessmatch', ['PieceColor'])

        # Adding model 'BoardSetup'
        db.create_table('chessmatch_boardsetup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='boardsetup_created', null=True, blank=True, to=orm['auth.User'])),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='boardsetup_updated', null=True, blank=True, to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('num_rows', self.gf('django.db.models.fields.PositiveIntegerField')(default=14)),
            ('num_cols', self.gf('django.db.models.fields.PositiveIntegerField')(default=14)),
            ('min_players', self.gf('django.db.models.fields.PositiveIntegerField')(default=4)),
            ('max_players', self.gf('django.db.models.fields.PositiveIntegerField')(default=4)),
            ('squares', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pieces', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('chessmatch', ['BoardSetup'])

        # Adding model 'BoardSetupColor'
        db.create_table('chessmatch_boardsetupcolor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('board_setup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chessmatch.BoardSetup'])),
            ('turn_order', self.gf('django.db.models.fields.IntegerField')()),
            ('color', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chessmatch.PieceColor'])),
        ))
        db.send_create_signal('chessmatch', ['BoardSetupColor'])

        # Adding model 'Player'
        db.create_table('chessmatch_player', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('ranking', self.gf('django.db.models.fields.IntegerField')(default=1500)),
        ))
        db.send_create_signal('chessmatch', ['Player'])

        # Adding model 'Game'
        db.create_table('chessmatch_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='game_created', null=True, blank=True, to=orm['auth.User'])),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='game_updated', null=True, blank=True, to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255, db_index=True)),
            ('board_setup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chessmatch.BoardSetup'])),
            ('started_at', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('turn_number', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('turn_color', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('chessmatch', ['Game'])

        # Adding model 'GamePlayer'
        db.create_table('chessmatch_gameplayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chessmatch.Game'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chessmatch.Player'])),
            ('turn_order', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('color', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chessmatch.PieceColor'], null=True, blank=True)),
            ('controller', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['chessmatch.GamePlayer'], null=True, blank=True)),
        ))
        db.send_create_signal('chessmatch', ['GamePlayer'])

        # Adding model 'GameAction'
        db.create_table('chessmatch_gameaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chessmatch.Game'])),
            ('turn', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('color', self.gf('django.db.models.fields.IntegerField')()),
            ('piece', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('from_coord', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('to_coord', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('is_capture', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_check', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_mate', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('chessmatch', ['GameAction'])


    def backwards(self, orm):
        
        # Deleting model 'PieceColor'
        db.delete_table('chessmatch_piececolor')

        # Deleting model 'BoardSetup'
        db.delete_table('chessmatch_boardsetup')

        # Deleting model 'BoardSetupColor'
        db.delete_table('chessmatch_boardsetupcolor')

        # Deleting model 'Player'
        db.delete_table('chessmatch_player')

        # Deleting model 'Game'
        db.delete_table('chessmatch_game')

        # Deleting model 'GamePlayer'
        db.delete_table('chessmatch_gameplayer')

        # Deleting model 'GameAction'
        db.delete_table('chessmatch_gameaction')


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
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'game_updated'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"})
        },
        'chessmatch.gameaction': {
            'Meta': {'ordering': "('turn', 'color')", 'object_name': 'GameAction'},
            'color': ('django.db.models.fields.IntegerField', [], {}),
            'from_coord': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_capture': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_check': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_mate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'piece': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'to_coord': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'turn': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'chessmatch.gameplayer': {
            'Meta': {'ordering': "('turn_order',)", 'object_name': 'GamePlayer'},
            'color': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.PieceColor']", 'null': 'True', 'blank': 'True'}),
            'controller': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['chessmatch.GamePlayer']", 'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chessmatch.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        'chessmatch.player': {
            'Meta': {'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'ranking': ('django.db.models.fields.IntegerField', [], {'default': '1500'}),
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
