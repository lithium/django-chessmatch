import jingo
from hashlib import md5


@jingo.register.function
def gravatar_image_url(email):
	hash = md5(email.strip().lower()).hexdigest()
	return "//www.gravatar.com/avatar/%s" % (hash,)