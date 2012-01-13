from django.contrib import admin
from basic_models.admin import DefaultModelAdmin, SlugModelAdmin
from chessmatch.models import *

admin.site.register(Player, DefaultModelAdmin)


class GameAdmin(SlugModelAdmin):
    class GamePlayerInline(admin.TabularInline):
        model = GamePlayer
        extra = 0
    class GameActionInline(admin.TabularInline):
        model = GameAction
        extra = 0
    inlines = (GamePlayerInline, GameActionInline)

admin.site.register(Game, GameAdmin)


class PieceColorAdmin(DefaultModelAdmin):
	list_display = ('name','hexvalue')
	fields = ('name','letter','hexvalue')
admin.site.register(PieceColor, PieceColorAdmin)

class PieceTypeAdmin(DefaultModelAdmin):
    class PieceMoveInline(admin.TabularInline):
        model = PieceMove
        extra = 0
    list_display = ('name','ascii_glyph','safe_unicodes','move_description')
    fields = ('name','ascii_glyph','unicode_glyph','rotation')
    inlines = (PieceMoveInline,)
admin.site.register(PieceType, PieceTypeAdmin)


class BoardSetupAdmin(SlugModelAdmin):
	class BoardSetupColorInline(admin.TabularInline):
		model = BoardSetupColor
		extra = 0
	inlines = (BoardSetupColorInline,)
admin.site.register(BoardSetup, BoardSetupAdmin)