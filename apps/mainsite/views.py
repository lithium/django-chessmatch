from django import http
from django import template
from django.db import models
from django.conf import settings
from django.views.generic import FormView
from django.contrib import auth

from contrib import twitterauth, oauth
from mainsite.forms import LoginForm
from chessmatch.models import Player


from django.views.generic import DetailView
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class JsonDetailView(DetailView):
    def render_to_response(self, context):
        content = json.dumps(context)
        return http.HttpResponse(content, content_type='application/json')




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

    def get_success_url(self):
        return self.request.GET.get('next', getattr(self,'success_url','/'))

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
    referer = request.META.get('referer', '/')

    consumer_key = getattr(settings, 'CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'CONSUMER_SECRET', None)
    request_token = request.session.get('twitter_request_token', None)
    oauth_verifier = request.GET.get('oauth_verifier', None)
    if not (request_token and consumer_key and consumer_secret):
        return http.HttpResponseRedirect(referer)

    del request.session['twitter_request_token']

    # check that the request token matches
    token = oauth.OAuthToken.from_string(request_token)
    if token.key != request.GET.get('oauth_token', 'no-token'):
        return http.HttpResponseRedirect(referer)

    # get the access token
    twitter = twitterauth.TwitterAuth(consumer_key, consumer_secret)
    access_token = twitter.get_access_token(token, oauth_verifier=oauth_verifier)
    request.session['twitter_access_token'] = access_token.to_string()

    # lookup the twitter username
    credentials = twitter.verify_credentials(access_token)
    if not credentials or 'screen_name' not in credentials: # not logged in to twitter
        return http.HttpResponseRedirect(referer)

    screen_name = credentials.get('screen_name', None)


    # look up the profile class 
    auth_profile_module = getattr(settings, 'AUTH_PROFILE_MODULE', None)
    profile_class = models.get_model(*auth_profile_module.split('.'))
    profile_field_names = [f.name for f in profile_class._meta.fields]
    required_field_names = ('twitter_access_token','twitter_screen_name')
    if not len(set(required_field_names) - set(profile_field_names)) == 0: # required fields present
        return http.HttpResponseRedirect(referer)


    # find or create the profile/user that matches this twitter access_token
    user = None

    try:
        # try to authenticate with this twitter account
        profile = profile_class.objects.get(twitter_access_token=access_token, twitter_screen_name=screen_name)
        user = profile.user
    except profile_class.DoesNotExist as e:
        # no account existed,

        # are we associating with an existing account?
        if request.user.is_authenticated():
            user = request.user
            profile = user.get_profile()
            profile.twitter_access_token = access_token
            profile.twitter_screen_name = screen_name
        else:
            # we'll just create a new account
            user, user_created = auth.models.User.objects.get_or_create(username=screen_name)
            if not user_created:
                raise NotImplementedError("trying to create account from twitter of existing username...")
            profile = profile_class(twitter_access_token=access_token, twitter_screen_name=screen_name, user=user)


    # check and see if there are any fields on the profile that should be populated from twitter
    for field_name in filter(lambda f: f.startswith('twitter_'), profile_field_names):
        real_field_name = field_name[8:]
        if real_field_name in credentials and not getattr(profile, field_name, ''):
            setattr(profile, field_name, credentials[real_field_name])

    profile.save()

    if not user:
        return http.HttpResponseRedirect(referer)

    # log in the user
    # set the user backend manually since we didnt use authenticate()
    backend = auth.get_backends()[0]
    user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
    auth.login(request, user)

    return http.HttpResponseRedirect(referer)










