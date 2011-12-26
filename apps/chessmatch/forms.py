from django import forms
from chessmatch.models import *


class NewGameForm(forms.ModelForm):
	class Meta:
		model = Game
		fields = ('name','board_setup','num_players')


class BoardSetupForm(forms.ModelForm):
	class Meta:
		model = BoardSetup
		fields = ('name','slug','description','num_rows','num_cols','min_players','max_players','pieces','squares')
		widgets = {
			'num_rows': forms.Select(choices=((c,c) for c in range(1,100)))
		}

			