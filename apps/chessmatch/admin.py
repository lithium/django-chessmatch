from django.contrib import admin
from django import forms
from basic_models.admin import DefaultModelAdmin, SlugModelAdmin
from chessmatch.models import *

admin.site.register(Player, DefaultModelAdmin)


class GameAdminForm(forms.ModelForm):
    class Meta:
        model = Game
    def __init__(self, *args, **kwargs):
        super(GameAdminForm, self).__init__(*args, **kwargs)
    # def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    #     field = super(GamePlayerInline, self).formfield_for_foreignkey(db_field, request=request, **kwargs)
    #     if db_field.name == 'controller':
    #         print vars(self).keys()
    #         if 'instance' in kwargs:
    #             field.queryset = field.queryset.filter(game=kwargs['instance'].game)
    #     return field

class GamePlayerForm(forms.ModelForm):
    class Meta:
        model = GamePlayer
    def __init__(self, *args, **kwargs):
        super(GamePlayerForm, self).__init__(*args, **kwargs)
        try:
            self.fields['controller'].queryset = self.fields['controller'].queryset.filter(game=self.instance.game)
        except Game.DoesNotExist:
            pass

class GameAdminForm(forms.ModelForm):
    class Meta:
        model = Game
    def __init__(self, *args, **kwargs):
        super(GameAdminForm, self).__init__(*args, **kwargs)
        try:
            self.fields['winner'].queryset = self.fields['winner'].queryset.filter(game=self.instance)
        except Game.DoesNotExist:
            pass


class GameAdmin(SlugModelAdmin):
    class GamePlayerInline(admin.TabularInline):
        model = GamePlayer
        extra = 0
        form = GamePlayerForm
    class GameActionInline(admin.TabularInline):
        model = GameAction
        extra = 0
    form = GameAdminForm
    inlines = (GamePlayerInline, GameActionInline)

admin.site.register(Game, GameAdmin)


class PieceColorAdmin(DefaultModelAdmin):
	list_display = ('name','hexvalue')
	fields = ('name','letter','hexvalue')
admin.site.register(PieceColor, PieceColorAdmin)

class BoardSetupAdmin(SlugModelAdmin):
	class BoardSetupColorInline(admin.TabularInline):
		model = BoardSetupColor
		extra = 0
	inlines = (BoardSetupColorInline,)
admin.site.register(BoardSetup, BoardSetupAdmin)