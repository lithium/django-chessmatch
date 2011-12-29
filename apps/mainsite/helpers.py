import jingo
from hashlib import md5
import urllib


@jingo.register.function
def gravatar_image_url(email, size=80, default=None):
    hash = md5(email.strip().lower()).hexdigest()
    args = {
        's': size
    }
    if default:
        args['d'] = default
    return "//www.gravatar.com/avatar/%s?%s" % (hash,urllib.urlencode(args))
