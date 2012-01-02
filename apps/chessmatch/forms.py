from django import forms
from chessmatch.models import *


class NewGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('name','board_setup')



class BoardSetupForm(forms.ModelForm):
    class Meta:
        model = BoardSetup
        fields = ('name','description','num_rows','num_cols','min_players','max_players','pieces','squares')
        exclude = ('slug',)
        #widgets = {
        #   'num_rows': forms.Select(choices=((c,c) for c in range(1,100)))
        #}


class GameMovesForm(forms.Form):

    def __init__(self, gameplayer, *args, **kwargs):
        self.gameplayer = gameplayer
        super(GameMovesForm, self).__init__(*args, **kwargs)
        if gameplayer:
            choices = [('','---')]
            for gp in gameplayer.game.gameplayer_set.exclude(id=gameplayer.id):
                if gp.color:
                    choices.append( (gp.color.letter, "%s (%s)" % (gp.color.name, gp.player.moniker)) )
            self.fields['other_players'] = forms.ChoiceField(choices=choices)
            

class AccountForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('nickname','avatar_url','notify_type','notify_after')
