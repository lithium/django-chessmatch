from django.db import models
from django.conf import settings
from basic_models import models as basic_models
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

import re
import random
import datetime
import string


from chessmatch import tasks


class PieceColor(models.Model):
    name = models.CharField(max_length=64)
    letter = models.CharField(max_length=1, unique=True)
    hexvalue = models.CharField(max_length=64, blank=True)

    #class Meta:
        #ordering = ('turn_order',)

    def __unicode__(self):
        return self.name

DIR_NONE = 'n'
DIR_UP = 'u'
DIR_UPRIGHT = 'ur'
DIR_RIGHT = 'r'
DIR_DOWNRIGHT = 'dr'
DIR_DOWN = 'd'
DIR_DOWNLEFT = 'dl'
DIR_LEFT = 'l'
DIR_UPLEFT = 'ul'
DIR_CHOICES = (
    (DIR_NONE, 'None'),
    (DIR_UP, 'Up'),
    (DIR_UPRIGHT, 'Up-Right'),
    (DIR_RIGHT, 'Right'),
    (DIR_DOWNRIGHT, 'Down-Right'),
    (DIR_DOWN, 'Down'),
    (DIR_DOWNLEFT, 'Down-Left'),
    (DIR_LEFT, 'Left'),
    (DIR_UPLEFT, 'Up-Left'),
)


class BoardSetup(basic_models.SlugModel):
    description = models.TextField(blank=True)
    num_rows = models.PositiveIntegerField(choices=((c,c) for c in range(8,27)), default=14)
    num_cols = models.PositiveIntegerField(choices=((c,c) for c in range(8,27)), default=14)
    min_players = models.PositiveIntegerField(choices=((c,c) for c in range(2,17)), default=4)
    max_players = models.PositiveIntegerField(choices=((c,c) for c in range(2,17)), default=4)
    squares = models.TextField(blank=True)
    pieces = models.TextField(blank=True)

    @property
    def files(self):
        return string.ascii_lowercase[:self.num_cols]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(BoardSetup, self).save(*args, **kwargs)


    def is_coord_valid(self, file, rank):
        col = string.ascii_lowercase.find(file)+1
        return  (col > 0 and col <= self.num_cols) and \
                (rank > 0 and rank <= self.num_rows) and \
                ('%s%s'%(file,rank) not in self.squares)

    def get_space_color(self, file, rank):
        color = ""
        if not self.is_coord_valid(file,rank):
            color = "unusable "
        files_odds = self.files[::2]
        files_evens = self.files[1::2]
        if rank % 2:
            color += "black" if file in files_odds else "white"
        else:
            color += "black" if file in files_evens else "white"
        return color

    def get_starting_piece(self, file, rank, show_directions=True):
        piece_unicode = {'K': '&#9818', 'Q': '&#9819', 'R': '&#9820', 'B': '&#9821', 'N': '&#9822', 'P': '&#9823', }
        arrow_unicode = {DIR_UP: '&uarr;', DIR_UPRIGHT: '&#x2197;', DIR_RIGHT: '&rarr;', 
                         DIR_DOWNRIGHT: '&#x2198;', DIR_DOWN: '&darr;', DIR_DOWNLEFT: '&#x2199;', 
                         DIR_LEFT: '&larr;', DIR_UPLEFT: '&#x2196;', DIR_NONE: '', }
        colors = dict(((pc.letter,pc.name.lower()) for pc in PieceColor.objects.all()))
        for p in re.split(r'\s+', self.pieces):
            p = p.strip()
            if p.endswith("%s%s" % (file,rank)):
                # Get pawn direction
                direction = p[1] in ('p', 'P') and self.get_pawn_direction(p[0]) or DIR_NONE
                return mark_safe('<div class="piece %(color)s id="piece_%(piece)s-%(color)s" piece="%(name)s">%(unicode)s;<div class="arrow %(dirname)s">%(dirchar)s</div></div>' % {
                    'color': colors[p[0]],
                    'piece': p[1],
                    'unicode': piece_unicode[p[1].upper()],
                    'dirname': direction,
                    'dirchar': show_directions and arrow_unicode[direction] or '',
                    'name': p,
                })
        return ''

    def get_color_letters(self):
        ret = ""
        for pc in self.get_piece_colors():
            ret += pc.letter
        return ret

    def get_piece_colors(self):
        return [bsc.color for bsc in self.boardsetupcolor_set.all().order_by('turn_order').select_related()]

    def get_turn_color(self, turn_order):
        return self.boardsetupcolor_set.get(turn_order=turn_order)

    def get_pawn_direction(self, color):
        try:
            bcs = self.boardsetupcolor_set.get(color__letter=color)
            return bcs.pawn_vector
        except BoardSetupColor.DoesNotExist:
            return DIR_NONE

class BoardSetupColor(models.Model):
    board_setup = models.ForeignKey(BoardSetup)
    turn_order = models.IntegerField(choices=((c,c) for c in range(0,33)))
    pawn_vector = models.CharField(max_length=2, choices=DIR_CHOICES, default=DIR_NONE)
    color = models.ForeignKey(PieceColor)

    class Meta:
        ordering = ('turn_order',)



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
    NOTIFY_NONE = ''
    NOTIFY_TWITTER = 'twitter'
    NOTIFY_CHOICES = (
       (NOTIFY_NONE, 'Dont notify'),
       (NOTIFY_TWITTER, 'Twitter'),
    )

    user = models.OneToOneField('auth.User')
    ranking = models.IntegerField(default=1500)
    nickname = models.CharField(max_length=64, blank=True)
    avatar_url = models.URLField(verify_exists=False, blank=True)

    notify_type = models.CharField(max_length=64, choices=NOTIFY_CHOICES, default=NOTIFY_NONE, blank=True)
    notify_after = models.IntegerField(default=1) # in minutes

    twitter_access_token = models.CharField(max_length=1024, blank=True)
    twitter_screen_name = models.CharField(max_length=1024, blank=True)
    twitter_profile_image_url = models.URLField(verify_exists=False, blank=True)
    twitter_name = models.CharField(max_length=1024, blank=True)

    def __unicode__(self):
        return unicode(self.user)
       
    @property
    def moniker(self):
        if self.nickname:
            return self.nickname
        if self.twitter_name:
            return self.twitter_name 
        if self.twitter_screen_name:
            return self.twitter_screen_name 
        return self.user.username

    @property
    def avatar(self):
        from mainsite.helpers import gravatar_image_url

        if self.avatar_url:
            return self.avatar_url
        if self.twitter_profile_image_url:
            return self.twitter_profile_image_url
        default = getattr(settings, 'DEFAULT_AVATAR_URL', None)
        return gravatar_image_url(self.user.email, default=default)
        



class Game(basic_models.SlugModel):
    board_setup = models.ForeignKey(BoardSetup)
    started_at = models.DateTimeField(blank=True, null=True, default=None)
    turn_number = models.PositiveIntegerField(default=0)
    turn_color = models.IntegerField(default=0)
    winner = models.ForeignKey("chessmatch.GamePlayer", blank=True, null=True, default=None, related_name='games_won')

    @property
    def num_players(self):
        return self.gameplayer_set.all().count()

    @property
    def comma_players(self):
        return ', '.join(gp.player.moniker for gp in self.gameplayer_set.all())

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Game, self).save(*args, **kwargs)

    def start_new_game(self):
        if self.started_at is not None:
            return

        color_letters = self.board_setup.get_color_letters()
        piece_letters = 'PRNBQK'
        piece_colors = self.board_setup.get_piece_colors()

        for placement in re.split(r'\s+', self.board_setup.pieces):
            placement = placement.strip()
            if not placement:
                continue
            turn_order = color_letters.find(placement[0].lower())
            piece = placement[1].upper()
            square = placement[2:].lower()
            if turn_order == -1 or piece not in piece_letters:
                continue
            action, created = GameAction.objects.get_or_create(game=self,
                turn=0,color=turn_order,
                piece=piece,
                from_coord='',
                to_coord=square)



        # randomize player positions
        turns = sorted(zip([random.random() for c in range(0,self.num_players)], [player for player in self.gameplayer_set.all()]), lambda a,b: cmp(a[0],b[0]))
        turn_order = 0
        for weight,player in turns:
            player.turn_order = turn_order
            player.color = piece_colors[turn_order]
            player.save()
            turn_order += 1

        self.started_at = datetime.datetime.now()
        self.turn_number = 1
        self.turn_color = 0
        self.save()

    def next_turn(self):
        def _inc_color():
            self.turn_color += 1
            if self.turn_color >= self.num_players:
                self.turn_color = 0
                self.turn_number += 1
        players = self.gameplayer_set.all()
        if len(players.filter(is_playing=True)) == 1:
            return
        _inc_color()
        while not players[self.turn_color].is_playing:
            _inc_color()
        self.save()

    def action_log(self):
        return self.gameaction_set.all()

    def get_latest_piece(self, coord):
        qs = self.gameaction_set.filter(to_coord=coord).order_by('-turn','-color')
        if len(qs) < 1:
            return None
        return qs[0]

    def is_playing(self, user):
        return (self.gameplayer_set.filter(player__user=user.id).count() > 0)


    def generate_board_state(self):
        board = {}

        nix_check_re = re.compile(r'[\+x].*$')
        for action in self.gameaction_set.all().order_by('turn','color'):
            if action.from_coord in ('x','-','yield'):
                continue
            if action.from_coord:
                board[action.from_coord] = None
            to_coord = nix_check_re.sub('', action.to_coord)
            board[to_coord] = "%s%s" % (action.color, action.piece)
        return board


    def make_move(self, player, from_coord, to_coord):
        qs = self.gameplayer_set.filter(models.Q(player=player) | models.Q(controller__player=player))
        legal_colors = [gp.turn_order for gp in qs.all()]
        if len(legal_colors) < 1 or self.turn_color not in legal_colors:
            return False

        cur_player = self.gameplayer_set.get(turn_order=self.turn_color)

        from_coord = from_coord.lower()
        to_coord = to_coord.lower()

        if from_coord == '-' and to_coord == '-':  # pass
            move, created = GameAction.objects.get_or_create(game=self,
                turn=self.turn_number,
                color=self.turn_color,
                piece='',
                from_coord='-',
                to_coord='-',
                is_capture=False,
            )
            self.next_turn()
            return True

        if from_coord == 'x' and to_coord == 'x':  # concede
            cur_player.is_playing = False
            cur_player.save()
            move, created = GameAction.objects.get_or_create(game=self,
                turn=self.turn_number,
                color=self.turn_color,
                piece='',
                from_coord='x',
                to_coord='x',
                is_capture=False,
            )
            self.next_turn()
            return True

        if from_coord == 'yield':  # yield control
            qs = self.gameplayer_set.filter(color__letter=to_coord)
            if len(qs) < 1: # invalid color letter
                return False 
            cur_player.controller = qs[0]
            cur_player.save()
            move, created = GameAction.objects.get_or_create(game=self,
                turn=self.turn_number,
                color=self.turn_color,
                piece='',
                from_coord=from_coord,
                to_coord=to_coord,
                is_capture=False,
            )
            return True


        if not from_coord or not to_coord or (from_coord == to_coord):
            return False


        board = self.generate_board_state()
        src_piece = board.get(from_coord, None)
        cap_piece = board.get(re.sub(r'[\+x].*$', '', to_coord), None)
        if src_piece is None:
            return False

        move, created = GameAction.objects.get_or_create(game=self,
            turn=self.turn_number,
            color=self.turn_color,
            piece=src_piece[-1],
            from_coord=from_coord,
            to_coord=to_coord,
            is_capture=(cap_piece is not None),
        )
        self.next_turn()
        return True

    def current_turn_player(self):
        gp = self.gameplayer_set.filter(turn_order=self.turn_color)
        if len(gp) > 0:
            return gp[0].player

    def notify_next_player(self):
        gp = self.gameplayer_set.filter(turn_order=self.turn_color)
        if len(gp) < 1:
            return
        gp = gp[0]
        if gp.player.notify_type == Player.NOTIFY_TWITTER and gp.player.twitter_screen_name:
            when = datetime.datetime.now() + datetime.timedelta(minutes=gp.player.notify_after)
            tasks.notify_player_twitter.apply_async(args=[gp.id], eta=when)



class GamePlayer(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)
    turn_order = models.IntegerField(default=-1)
    color = models.ForeignKey(PieceColor, blank=True, null=True)
    controller = models.ForeignKey('self', blank=True, null=True, default=None)
    is_playing = models.BooleanField(default=True)


    class Meta:
        ordering = ('turn_order',)

    def __unicode__(self):
        return "%s (%s)" % (self.color, self.controller if self.controller else self.player)

    @property
    def controlling_player(self):
        return self.controller.player if self.controller_id else self.player




class GameAction(models.Model):
    game = models.ForeignKey(Game)
    turn = models.PositiveIntegerField()
    color = models.IntegerField()
    piece = models.CharField(max_length=64, choices=PIECE_CHOICES, blank=True)
    from_coord = models.CharField(max_length=64, blank=True)
    to_coord = models.CharField(max_length=64)
    is_capture = models.BooleanField(default=False)

    class Meta:
        ordering = ('turn','color')

    @property
    def expression(self):
        if self.from_coord == 'x' and self.to_coord == 'x':
            return "#"
        if self.from_coord == 'yield':
            return ">%s" % (self.to_coord,)
        suffix = ''

        cap = ''
        if self.is_capture:
            cap = 'x'
            if self.piece == 'P':
                cap = self.from_coord[0]+cap 

        return "%(piece)s%(is_cap)s%(to_coord)s%(suffix)s" % {
            'piece': self.piece if self.piece != PIECE_PAWN else '',
            'to_coord': self.to_coord,
            'is_cap': cap,
            'suffix': suffix,
        }

    def __unicode__(self):
        fmts = ("%s", "... %s", "... ... %s", "... ... ... %s")
        return "%s. %s" % (self.turn, fmts[self.color] % (self.expression,))
