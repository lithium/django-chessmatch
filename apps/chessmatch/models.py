from django.db import models
from basic_models import models as basic_models
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

import re
import random
import datetime
import string



class PieceColorManager(models.Manager):
    def letters_array(self):
        ret = ""
        for pc in self.all().order_by('turn_order'):
            ret += pc.letter
        return ret


class PieceColor(models.Model):
    turn_order = models.IntegerField()
    name = models.CharField(max_length=64)
    letter = models.CharField(max_length=1, unique=True)
    hexvalue = models.CharField(max_length=64, blank=True)

    objects = PieceColorManager()

    class Meta:
        ordering = ('turn_order',)

    def __unicode__(self):
        return self.name

class BoardSetup(basic_models.SlugModel):
    description = models.TextField(blank=True)
    num_rows = models.PositiveIntegerField(default=14)
    num_cols = models.PositiveIntegerField(default=14)
    squares = models.TextField(blank=True)
    min_players = models.PositiveIntegerField(default=4)
    max_players = models.PositiveIntegerField(default=4)
    pieces = models.TextField()

    @property
    def files(self):
        return string.ascii_lowercase[:self.num_cols]

    def is_coord_valid(self, file, rank):
        col = string.ascii_lowercase.find(file)+1
        return  (col > 0 and col <= self.num_cols) and \
                (rank > 0 and rank <= self.num_rows) and \
                ('%s%s'%(file,rank) not in self.squares)

    def get_space_color(self, file, rank):
        if not self.is_coord_valid(file,rank):
            return "unusable"
        files_odds = self.files[::2]
        files_evens = self.files[1::2]
        if rank % 2:
            return "black" if file in files_odds else "white"
        else:
            return "black" if file in files_evens else "white"

    def get_starting_piece(self, file, rank):
        unicodes = {'K': '&#9818', 'Q': '&#9819', 'R': '&#9820', 'B': '&#9821', 'N': '&#9822', 'P': '&#9823', }
        colors = dict(((pc.letter,pc.name.lower()) for pc in PieceColor.objects.all()))
        for p in re.split(r'\s+', self.pieces):
            p = p.strip()
            if p.endswith("%s%s" % (file,rank)):
                return mark_safe('<div class="piece %(color)s id="piece_%(piece)s-%(color)s">%(unicode)s</div>' % {
                    'color': colors[p[0]],
                    'piece': p[1],
                    'unicode': unicodes[p[1]],
                })
        return ''





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
    board_setup = models.ForeignKey(BoardSetup)
    started_at = models.DateTimeField(blank=True, null=True, default=None)
    turn_number = models.PositiveIntegerField(default=0)
    turn_color = models.IntegerField(default=0)
    num_players = models.PositiveIntegerField(default=4)

    @property
    def comma_players(self):
        return ', '.join(unicode(gp.player) for gp in self.gameplayer_set.all())


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Game, self).save(*args, **kwargs)

    def start_new_game(self):
        if self.started_at is not None:
            return

        color_letters = PieceColor.objects.letters_array()
        piece_letters = 'PRNBQK'

        for placement in re.split(r'\s+', self.board_setup.pieces):
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

        # randomize player positions
        turns = sorted(zip([random.random() for c in range(0,4)], [player for player in self.gameplayer_set.all()]), lambda a,b: cmp(a[0],b[0]))
        color = 0
        for weight,player in turns:
            player.color = color
            player.save()
            color += 1

        self.started_at = datetime.datetime.now()
        self.turn_number = 1
        self.turn_color = 0
        self.save()

    def next_turn(self):
        self.turn_color += 1
        if self.turn_color >= self.num_players:
            self.turn_color = 0
            self.turn_number += 1
        self.save()

    def action_log(self):
        return self.gameaction_set.all()

    def get_latest_piece(self, coord):
        qs = self.gameaction_set.filter(to_coord=coord).order_by('-turn','-color')
        if len(qs) < 1:
            return None
        return qs[0]


class GamePlayer(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)
    color = models.IntegerField(default=-1)
    controller = models.ForeignKey('self', blank=True, null=True, default=None)

    def __unicode__(self):
        return "%s (%s)" % (self.color, self.controller if self.controller else self.player)




class GameAction(models.Model):
    game = models.ForeignKey(Game)
    turn = models.PositiveIntegerField()
    color = models.IntegerField()
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
