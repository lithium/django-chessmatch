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
        c.update({
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

        moves = []
        for move in queryset:
            moves.append({
                'to_coord': move.to_coord,
                'from_coord': move.from_coord,
                'turn': move.turn,
                'color': move.color,
                'piece': move.piece,
                'expr': move.expression,
            })
        content = json.dumps(moves)
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
