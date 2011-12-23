from django.conf.urls.defaults import patterns, include, url

from chessmatch.views import *

urlpatterns = patterns('',
    url(r'^board/(?P<slug>[^/]+)/history/(?:(?P<last_seen>[^/]+)/)?$', HistoryView.as_view(), name='chessmatch_history'),
    url(r'^board/(?P<slug>[^/]+)/$', BoardView.as_view(), name='chessmatch_game'),

    url(r'^$', LobbyView.as_view(), name='chessmatch_lobby'),
)
