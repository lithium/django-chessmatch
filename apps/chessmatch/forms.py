from django import forms
from chessmatch.models import Game


class NewGameForm(forms.ModelForm):
	class Meta:
		model = Game
		fields = ('name','board_setup','num_players')