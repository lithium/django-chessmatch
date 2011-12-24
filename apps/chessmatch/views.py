from django.views.generic import TemplateView, DetailView, CreateView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse
from django.db import models
from django import http
from django.core import serializers

from chessmatch.models import *
from chessmatch.forms import *
import json


class LobbyView(TemplateView):
    template_name = 'chessmatch/lobby.html'

    def get_context_data(self, **kwargs):
        c = super(LobbyView, self).get_context_data(**kwargs)
        c.update({
            'games': Game.objects.active(),
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

        files = string.ascii_lowercase[:self.object.board_setup.num_cols]
        files_odds = files[::2]
        files_evens = files[1::2]

        c.update({
            'players': players,
            'files': files,
            'files_odds': files_odds,
            'files_evens': files_evens,
        })
        return c


class HistoryView(DetailView):
    model = Game
    def render_to_response(self, context):
        queryset = self.object.gameaction_set.all()
        last_seen = self.kwargs.get('last_seen', None)
        if last_seen:
            turn, color = last_seen.split('.')
            queryset = queryset.filter(models.Q(turn__gt=turn) | models.Q(turn=turn,color__gt=color))

        state = {
            'turn': "%s.%s" % (self.object.turn_number, self.object.turn_color),
            'moves': [],
            'my_colors': [],
        }

        if self.request.user.is_authenticated():
            player = self.request.user.get_profile()
            for gp in self.object.gameplayer_set.filter(models.Q(player=player) | models.Q(controller=player)):
                state['my_colors'].append(gp.color)

        for move in queryset:
            state['moves'].append({
                'to_coord': move.to_coord,
                'from_coord': move.from_coord,
                'turn': move.turn,
                'color': move.color,
                'piece': move.piece,
                'expr': move.expression,
            })
        content = json.dumps(state)
        #content = serializers.serialize('json', moves)


        return http.HttpResponse(content, content_type='application/json')

class NewGameView(CreateView):
    model = Game
    form_class = NewGameForm 
    template_name = 'chessmatch/newgame.html'
    success_url = '/'

    def form_valid(self, form):
        ret = super(NewGameView, self).form_valid(form)
        gp, created = GamePlayer.objects.get_or_create(
            game=self.object, 
            player=self.request.user.get_profile()
        )
        return ret

class JoinGameView(DetailView):
    model = Game
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.is_authenticated():
            player = request.user.get_profile()
            gp, created = GamePlayer.objects.get_or_create(game=obj, player=player)
        return http.HttpResponseRedirect(reverse('chessmatch_game', kwargs={'slug':obj.slug}))


class StartGameView(DetailView):
    model = Game
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
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
        qs = game.gameplayer_set.filter(models.Q(player=player) | models.Q(controller=player))
        legal_colors = [gp.color for gp in qs.all()]
        if len(legal_colors) < 1 or game.turn_color not in legal_colors:
            return http.HttpResponseForbidden()

        from_coord = request.POST.get('from_coord','').strip()
        to_coord = request.POST.get('to_coord','').strip()

        if not from_coord or not to_coord:
            return http.HttpResponseBadRequest()

        src_piece = game.get_latest_piece(from_coord)
        cap_piece = game.get_latest_piece(to_coord)
        if src_piece is None:
            return http.HttpResponseBadRequest()


        move, created = GameAction.objects.get_or_create(game=game,
            turn=game.turn_number,
            color=game.turn_color,
            piece=src_piece.piece,
            from_coord=from_coord,
            to_coord=to_coord,
            is_capture=(cap_piece is not None),
        )
        game.next_turn()
        return http.HttpResponseRedirect(reverse('chessmatch_game', kwargs={'slug':game.slug}))




