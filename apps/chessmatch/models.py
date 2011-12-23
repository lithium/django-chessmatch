from django.db import models
from basic_models import models as basic_models

import re

import chessmatch.boards


COLOR_WHITE=0
COLOR_RED=1
COLOR_BLACK=2
COLOR_GREEN=3
COLOR_CHOICES = (
    (COLOR_WHITE, 'White'),
    (COLOR_RED, 'Red'),
    (COLOR_BLACK, 'Black'),
    (COLOR_GREEN, 'Green'),
)

BOARD_SETUP_HUGHES='all_queens_on_left'
BOARD_SETUP_CHOICES = (
    (BOARD_SETUP_HUGHES, 'Hughes (Queens always on the left)'),
)

PIECE_PAWN='P'
PIECE_ROOK='R'
PIECE_KNIGHT='N'
PIECE_BISHOP='B'
PIECE_QUEEN='Q'
PIECE_KING='K'
PIECE_CHOICES = (
    (PIECE_PAWN, 'Pawn'),
    (PIECE_ROOK, 'Rook'),
    (PIECE_KNIGHT, 'Knight'),
    (PIECE_BISHOP, 'Bishop'),
    (PIECE_QUEEN, 'Queen'),
    (PIECE_KING, 'King'),
)

class Player(basic_models.ActiveModel):
    user = models.OneToOneField('auth.User')
    ranking = models.IntegerField(default=1500)

    def __unicode__(self):
        return unicode(self.user)


class Game(basic_models.SlugModel):
    board_setup = models.CharField(max_length=64, choices=BOARD_SETUP_CHOICES, default=BOARD_SETUP_HUGHES)
    started_at = models.DateTimeField(blank=True, null=True, default=None)
    turn_number = models.PositiveIntegerField(default=0)
    turn_color = models.IntegerField(choices=COLOR_CHOICES, default=0)


    def start_new_game(self):
        if self.started_at is not None:
            return
        starting_pieces = getattr(chessmatch.boards, self.board_setup, None)
        if starting_pieces is None:
            raise AttributeError("Could not find board setup '%s'" % (self.board_setup,))

        color_letters = 'wrbg'
        piece_letters = 'PRNBQK'

        for placement in re.split(r'\s+', starting_pieces):
            placement = placement.strip()
            if not placement:
                continue
            color = color_letters.find(placement[0].lower())
            piece = placement[1].upper()
            square = placement[2:].lower()
            if color == -1 or piece not in piece_letters:
                continue
            action, created = GameAction.objects.get_or_create(game=self,
                turn=0,color=color,
                piece=piece,
                from_coord='',
                to_coord=square)
        self.started_at = datetime.datetime.now()
        self.turn_number = 1
        self.turn_color = COLOR_WHITE
        self.save()

    def action_log(self):
        return self.gameaction_set.all()



class GamePlayer(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)
    color = models.IntegerField(choices=COLOR_CHOICES)
    controller = models.ForeignKey('self', blank=True, null=True, default=None)


class GameAction(models.Model):
    game = models.ForeignKey(Game)
    turn = models.PositiveIntegerField(default=0)
    color = models.IntegerField(choices=COLOR_CHOICES, default=0)
    piece = models.CharField(max_length=64, choices=PIECE_CHOICES)
    from_coord = models.CharField(max_length=64, blank=True)
    to_coord = models.CharField(max_length=64)
    is_capture = models.BooleanField(default=False)
    is_check = models.BooleanField(default=False)
    is_mate = models.BooleanField(default=False)

    class Meta:
        ordering = ('turn','color')

    @property
    def expression(self):
        suffix = ''
        if self.is_mate:
            suffix = '#'
        elif self.is_check:
            suffix = '+'
        return "%(piece)s%(is_cap)s%(to_coord)s%(suffix)s" % {
            'piece': self.piece if self.piece != PIECE_PAWN else '',
            'to_coord': self.to_coord,
            'is_cap': 'x' if self.is_capture else '',
            'suffix': suffix,
        }

    def __unicode__(self):
        fmts = ("%s", "... %s", "... ... %s", "... ... ... %s")
        return "%s. %s" % (self.turn, fmts[self.color] % (self.expression,))
