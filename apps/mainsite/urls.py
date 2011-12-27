from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

handler500 = 'mainsite.views.error500'
handler404 = 'mainsite.views.error404'

from mainsite.views import LoginView


urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^logout/$', 'mainsite.views.logout', name='logout'),
    url(r'^login/$', LoginView.as_view(), name='login'),

    url(r'^login/twitter/$', 'mainsite.views.twitter_signin', name='login_twitter'),
    url(r'^login/twitter/return/$', 'mainsite.views.twitter_return', name='login_twitter_return'),


    url(r'', include('chessmatch.urls')),

)

if getattr(settings, 'DEBUG', False) or getattr(settings, 'DEBUG_STATIC', False):
    # If we are in debug mode, prepend a rule to urlpatterns to serve the static media
    import re
    urlpatterns = patterns('',
        url(r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL), 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT
        }),
    ) + urlpatterns
