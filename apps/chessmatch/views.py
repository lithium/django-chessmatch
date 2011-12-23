from django.views.generic import TemplateView, DetailView
from django.db import models
from django import http
from django.core import serializers

from chessmatch.models import *
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
