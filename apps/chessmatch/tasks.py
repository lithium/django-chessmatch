from celery.task import task
from django.conf import settings



@task
def notify_player_twitter(gameplayer_id):
    import twitter
    from chessmatch.models import GamePlayer

    gameplayer = None
    try:
        gameplayer = GamePlayer.objects.get(pk=gameplayer_id)
    except GamePlayer.DoesNotExist as e:
        return

    if gameplayer.game.turn_color != gameplayer.turn_order:  # no longer their turn
        return

    consumer_key = getattr(settings, 'CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'CONSUMER_SECRET', None)
    access_token_key = getattr(settings, 'ACCESS_TOKEN_KEY', None)
    access_token_secret = getattr(settings, 'ACCESS_TOKEN_SECRET', None)
    if not all((consumer_key,consumer_secret,access_token_key,access_token_secret)):
        return

    api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)
    tweet = "@%s it's turn %s.%s on #%s, your move." % (gameplayer.player.twitter_screen_name, gameplayer.game.turn_number, gameplayer.color.letter, gameplayer.game.slug)

    api.PostUpdate(tweet)



