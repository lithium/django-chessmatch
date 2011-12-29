from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import tweetstream
import time
import datetime
import re

from chessmatch.models import *


class Command(BaseCommand):
    hashtag_re = re.compile(r'#(\S+)', re.I)
    squares_re = re.compile(r'\b([a-z]+[0-9]+)\b', re.I)

    def _process_tweet(self, tweet):
        screen_name = tweet['user']['screen_name']
        text = tweet['text']
        hashtags = self.hashtag_re.findall(text) # match any hash tags
        squares = self.squares_re.findall(text)

        self.stdout.write("<%s> %s\n" % (screen_name, text))

        if len(squares) != 2:
            # couldn't find valid move
            self.stdout.write(" ! couldnt match coords\n")
            return 
        from_coord, to_coord = squares

        game = None
        if hashtags:
            try:
                game = Game.objects.get(slug=hashtags[0])
            except Game.DoesNotExist as e:
                self.stdout.write(" ! game %s does not exist\n" % (hashtags[0],))
                return

        try:
            player = Player.objects.get(twitter_screen_name=screen_name)
        except Player.DoesNotExist as e:
            # cant figure out what player
            self.stdout.write(" ! %s unknown player \n" % (screen_name,))
            return

        if not game: 
            games = GamePlayer.objects.filter(player=player, game__turn_color=models.F('turn_order'))
            if len(games) != 1:
                # either not in a game, or currently players turn in more than one game
                self.stdout.write(" ! cant determine game\n")
                return 
            game = games[0].game

        self.stdout.write("try to make move in %s for %s [%s:%s]\n" % (game, player, from_coord, to_coord))
        ret = game.make_move(player, from_coord, to_coord)
        if not ret:
                self.stdout.write(" ! illegal\n")



    def handle(self, *args, **kwargs):
        self.screen_name = getattr(settings, 'TWITTER_USERNAME', None)
        self.password = getattr(settings, 'TWITTER_PASSWORD', None)

        tracking = ["@"+self.screen_name]
        retry_wait = 1

        while True:
            try:
                self.stdout.write("connecting at %s..." % (datetime.datetime.now(),))
                self.stdout.flush()
                with tweetstream.FilterStream(self.screen_name, self.password, track=tracking) as stream:
                    self.stdout.write(" connected.\ntracking: %s\n"  % (tracking,))
                    for tweet in stream:
                        self._process_tweet(tweet)
            except tweetstream.ConnectionError as e:
                retry_wait *= 2
                self.stdout.write(" error '%s' retrying in %s...\n" % (e.reason, retry_wait))
                time.sleep(retry_wait)

