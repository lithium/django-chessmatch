from django.conf.urls.defaults import patterns, include, url

from chessmatch.views import *

urlpatterns = patterns('',
    url(r'^newgame/$', NewGameView.as_view(), name='chessmatch_newgame'),
    url(r'^manage-boards/$', ManageBoardsView.as_view(), name='chessmatch_manage_boards'),
    url(r'^manage-boards/create/$', NewBoardView.as_view(), name='chessmatch_new_board'),
    url(r'^manage-boards/(?P<pk>[^/]+)/$', EditBoardView.as_view(), name='chessmatch_edit_board'),

    url(r'^join/(?P<slug>[^/]+)/$', JoinGameView.as_view(), name='chessmatch_join'),
    url(r'^start/(?P<slug>[^/]+)/$', StartGameView.as_view(), name='chessmatch_start'),

    url(r'^board/(?P<slug>[^/]+)/history/(?:(?P<last_seen>[^/]+)/)?$', HistoryView.as_view(), name='chessmatch_history'),
    url(r'^board/(?P<slug>[^/]+)/$', BoardView.as_view(), name='chessmatch_game'),

    url(r'^move/(?P<slug>[^/]+)/$', MakeMoveView.as_view(), name='chessmatch_move'),


    url(r'^$', LobbyView.as_view(), name='chessmatch_lobby'),
)
