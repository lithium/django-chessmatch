from django import http
from django import template
from django.conf import settings
from django.views.generic import FormView
from django.contrib import auth

from contrib import twitterauth, oauth
from mainsite.forms import LoginForm
from chessmatch.models import Player

def error500(request, template_name='500.html'):
    t = template.loader.get_template(template_name)
    context = template.Context({
        'STATIC_URL': settings.STATIC_URL,
    })
    return http.HttpResponseServerError(t.render(context))

def error404(request, template_name='404.html'):
    t = template.loader.get_template(template_name)
    context = template.Context({
        'STATIC_URL': settings.STATIC_URL,
    })
    return http.HttpResponseNotFound(t.render(context))


class LoginView(FormView):
    form_class=LoginForm
    success_url='/'
    template_name='login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return http.HttpResponseRedirect(self.get_success_url())
        return super(LoginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.data.get('username',None)
        password = form.data.get('password',None)
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(self.request, user)
            return http.HttpResponseRedirect(self.get_success_url())
        return super(LoginView, self).form_invalid(form)


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return http.HttpResponseRedirect(request.META.get('referer', '/'))
    





def twitter_signin(request):
    consumer_key = getattr(settings, 'CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'CONSUMER_SECRET', None)
    if not (consumer_key and consumer_secret):
        return http.HttpResponseRedirect(request.META.get('referer', '/'))

    twitter = twitterauth.TwitterAuth(consumer_key, consumer_secret)
    request_token = twitter.get_request_token()
    request.session['twitter_request_token'] = request_token.to_string()
    signin_url = twitter.get_authorization_url(request_token)
    return http.HttpResponseRedirect(signin_url)

def twitter_return(request):
    if request.user.is_authenticated():
        return http.HttpResponseRedirect(request.META.get('referer', '/'))

    consumer_key = getattr(settings, 'CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'CONSUMER_SECRET', None)
    request_token = request.session.get('twitter_request_token', None)
    oauth_verifier = request.GET.get('oauth_verifier', None)
    if not (request_token and consumer_key and consumer_secret):
        return http.HttpResponseRedirect(request.META.get('referer', '/'))

    # check that the request token matches
    token = oauth.OAuthToken.from_string(request_token)
    if token.key != request.GET.get('oauth_token', 'no-token'):
        del request.session['twitter_request_token']
        return http.HttpResponseRedirect(login)

    # get the access token
    twitter = twitterauth.TwitterAuth(consumer_key, consumer_secret)
    access_token = twitter.get_access_token(token, oauth_verifier=oauth_verifier)
    request.session['twitter_access_token'] = access_token.to_string()

    # lookup the twitter username
    credentials = twitter.verify_credentials(access_token)
    if not credentials or 'screen_name' not in credentials: # not logged in to twitter
        del request.session['twitter_request_token']
        return http.HttpResponseRedirect(login)
    username = credentials.get('screen_name', None)

    user, created = auth.models.User.objects.get_or_create(username=username)
    if created: # if contrib.auth.user doesnt exist with matching username, create one
        user.set_password(access_token)
        user.save()
    elif not user.check_password(access_token): # if one exists check the access token against password
        del request.session['twitter_access_token']
        del request.session['twitter_request_token']
        return http.HttpResponseRedirect(login)

    # this jigpokery is because we didnt call authenticate()...
    backend = auth.get_backends()[0]
    user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)

    # log in the user
    auth.login(request, user)

    # create the profile if needed
    player, player_created = Player.objects.get_or_create(user=user)
    return http.HttpResponseRedirect(request.META.get('referer', '/'))










