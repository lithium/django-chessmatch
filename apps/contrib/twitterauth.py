import oauth
import urllib
import httplib


class TwitterAuth(object):
    REQUEST_TOKEN_URL= "https://twitter.com/oauth/request_token"
    AUTHORIZATION_URL="https://twitter.com/oauth/authorize"
    ACCESS_TOKEN_URL="https://twitter.com/oauth/access_token"
    VERIFY_CREDENTIALS_URL="https://api.twitter.com/1/account/verify_credentials.json"  

    def __init__(self, consumer_key, secret_key):
        self.consumer_key = consumer_key
        self.secret_key = secret_key
        self.consumer = oauth.OAuthConsumer(self.consumer_key, self.secret_key)
        self.sig_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.connection = httplib.HTTPSConnection("twitter.com")

    def _fetch_response(self, request):
        url = request.to_url()
        self.connection.request(request.http_method, url)
        response = self.connection.getresponse()
        return response.read()


    def get_request_token(self, **oauth_params):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, 
        													 http_url=TwitterAuth.REQUEST_TOKEN_URL,
                                                             parameters=oauth_params)
        request.sign_request(self.sig_method, self.consumer, None)
        response = self._fetch_response(request)
        token = oauth.OAuthToken.from_string(response)
        return token

    def get_authorization_url(self, request_token=None):
        if request_token is None:
            token = self.get_request_token()
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, 
					     http_url=TwitterAuth.AUTHORIZATION_URL,
                         token=request_token)
        request.sign_request(self.sig_method, self.consumer, request_token)
        return request.to_url()

    def get_access_token(self, request_token, verifier=None):
        oauth_params = {}
        if verifier is not None:
            oauth_params['oauth_verifier'] = verifier
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, 
        												     http_url=TwitterAuth.ACCESS_TOKEN_URL,
                                                             token=request_token, 
                                                             parameters=oauth_params)
        request.sign_request(self.sig_method, self.consumer, request_token)
        uh = urllib.urlopen(request.to_url())
        response = uh.read()
        uh.close()
        token = oauth.OAuthToken.from_string(response)
        return token

    def get_resource(access_token, url, http_method='GET', **oauth_params):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=url,
                                                             token=access_token, 
                                                             http_method=http_method,
                                                             parameters=oauth_params)
        request.sign_rAequest(self.sig_method, self.consumer, request_token)
        data = self._fetch_response(url)
        resource = json.loads(data)
        return resource

    def verify_credentials(self, access_token):
        return self.get_resource(access_token, TwitterAuth.VERIFY_CREDENTIALS_URL)
