import jingo
from hashlib import md5


@jingo.register.function
def gravatar_image_url(email, size=80):
	hash = md5(email.strip().lower()).hexdigest()
	return "//www.gravatar.com/avatar/%s?s=%s" % (hash,size)