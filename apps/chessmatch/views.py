from django.views.generic import TemplateView, DetailView, CreateView, RedirectView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.models import inlineformset_factory
from django import http
from django.core import serializers


from mainsite.views import LoginRequiredMixin, JsonDetailView
from chessmatch.models import *
from chessmatch.forms import *


class LobbyView(TemplateView):
    template_name = 'chessmatch/lobby.html'

    def get_context_data(self, **kwargs):
        c = super(LobbyView, self).get_context_data(**kwargs)
        c.update({
            'games': Game.objects.active().filter(started_at__isnull=False),
            'open_games': Game.objects.active().filter(started_at=None),
            'archive': Game.objects.filter(is_active=False),
        })
        return c

class BoardView(DetailView):
    model = Game
    template_name = 'chessmatch/board.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        c = super(BoardView, self).get_context_data(**kwargs)

        players = {}
        for gp in self.object.gameplayer_set.all():
            if gp.color >= 0:
                players[gp.color] = gp.player

        current_player = None
        try:
            if self.request.user.is_authenticated():
                current_player = self.object.gameplayer_set.get(player=self.request.user.get_profile())
        except GamePlayer.DoesNotExist as e:
            pass

        files = string.ascii_lowercase[:self.object.board_setup.num_cols]
        files_odds = files[::2]
        files_evens = files[1::2]

        is_lite = self.request.GET.get('lite','')

        c.update({
            'players': players,
            'files': files,
            'files_odds': files_odds,
            'files_evens': files_evens,
            'lite': is_lite,
            'base_template': 'lite.html' if is_lite else 'base.html',
            'moves_form': GameMovesForm(current_player),
        })
        return c


class HistoryView(JsonDetailView):
    model = Game

    def get_context_data(self, **kwargs):
        queryset = self.object.gameaction_set.all()
        last_seen = self.kwargs.get('last_seen', None)
        if last_seen:
            turn, color = last_seen.split('.')
            queryset = queryset.filter(models.Q(turn__gt=turn) | models.Q(turn=turn,color__gt=color))

        colors = self.object.board_setup.get_piece_colors()
        players = []
        for gp in self.object.gameplayer_set.all().order_by('turn_order'):
            players.append({
                'username': gp.controlling_player.moniker,
                'avatar': gp.controlling_player.avatar,
                'owner': gp.player.moniker,
            })
            if gp.color:
                colors.append(gp.color)

        state = {
            'turn': "%s.%s" % (self.object.turn_number, self.object.turn_color),
            'moves': [],
            'my_colors': [],
            'colors': [c.name.lower() for c in colors],
            'players': players,
        }

        if self.request.user.is_authenticated():
            player = self.request.user.get_profile()
            for gp in self.object.gameplayer_set.filter(models.Q(player=player) | models.Q(controller=player)):
                state['my_colors'].append(gp.turn_order)

        for move in queryset:
            direction = None
            if colors:
                direction = move.piece == 'P' and move.game.board_setup.get_pawn_direction([c.letter for c in colors][move.color]) or DIR_NONE
            state['moves'].append({
                'to_coord': move.to_coord,
                'from_coord': move.from_coord,
                'turn': move.turn,
                'color': move.color,
                'piece': move.piece,
                'direction': direction,
                'expr': move.expression,
            })
        return state

class NewGameView(LoginRequiredMixin, CreateView):
    model = Game
    form_class = NewGameForm 
    template_name = 'chessmatch/newgame.html'
    success_url = '/'

    def form_valid(self, form):
        obj = form.save()
        obj.setup_new_game()
        gp, created = GamePlayer.objects.get_or_create(
            game=obj, 
            player=self.request.user.get_profile()
        )
        return super(NewGameView, self).form_valid(form)

class JoinGameView(LoginRequiredMixin, DetailView):
    model = Game
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.is_authenticated():
            player = request.user.get_profile()
            gp, created = GamePlayer.objects.get_or_create(game=obj, player=player)
        return http.HttpResponseRedirect(reverse('chessmatch_game', kwargs={'slug':obj.slug}))


class StartGameView(LoginRequiredMixin, DetailView):
    model = Game
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.gameplayer_set.filter(player__user=request.user).count() > 0:
            obj.start_new_game()
        return http.HttpResponseRedirect(reverse('chessmatch_game', kwargs={'slug':obj.slug}))


class MakeMoveView(DetailView):
    model = Game
    def get(self, request, *args, **kwargs):
        return http.HttpResponseBadRequest()

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        if not request.user.is_authenticated():
            return http.HttpResponseForbidden()

        player = request.user.get_profile()
        from_coord = request.POST.get('from_coord','').strip()
        to_coord = request.POST.get('to_coord','').strip()

        if game.make_move(player, from_coord, to_coord):
            # notify next player its their move if they want.
            game.notify_next_player()
            return http.HttpResponseRedirect(reverse('chessmatch_game', kwargs={'slug':game.slug}))
        else:
            return http.HttpResponseForbidden()





class ManageBoardsView(TemplateView):
    template_name = 'chessmatch/manage_boards.html'

    def get_context_data(self, **kwargs):
        c = super(ManageBoardsView, self).get_context_data(**kwargs)
        c.update({
            'board_setups': BoardSetup.objects.all(),
        })
        return c

class EditBoardView(UpdateView):
    model = BoardSetup
    form_class = BoardSetupForm 
    template_name = 'chessmatch/edit_board.html'
    context_object_name = 'boardsetup'
    def get_success_url(self, **kwargs):
        return reverse('chessmatch_manage_boards')

    @property
    def color_formset(self):
        return inlineformset_factory(BoardSetup, BoardSetupColor, extra=self.object.max_players, max_num=self.object.max_players)

    def get_context_data(self, **kwargs):
        c = super(EditBoardView, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            formset = self.color_formset(self.request.POST, self.request.FILES, instance=self.object)
        else:
            formset = self.color_formset(instance=self.object)

        c.update({
            'colors': PieceColor.objects.all(),
            'formset': formset,
        })
        return c

    def form_valid(self, form):
        formset = self.color_formset(self.request.POST, self.request.FILES, instance=self.object)
        if not formset.is_valid():
            return self.form_invalid(form)
        formset.save()
        return super(EditBoardView, self).form_valid(form)



class NewBoardView(CreateView):
    model = BoardSetup
    form_class = BoardSetupForm
    template_name = 'chessmatch/edit_board.html'
    context_object_name = 'boardsetup'
    def get_success_url(self, **kwargs):
        return reverse('chessmatch_manage_boards')


class AccountView(UpdateView):
    model = Player
    form_class = AccountForm
    template_name = 'chessmatch/account.html'
    context_object_name = 'player'
    success_url = '/account/'

    def get(self, request, **kwargs):
        if not request.user.is_authenticated():
            return http.HttpResponseRedirect('/')
        return super(AccountView, self).get(request, **kwargs)

    def get_object(self, *args, **kwargs):
        return self.request.user.get_profile()



        
