from django.contrib.sites.models import Site


def get_canonical_url(url,https=False):
    site = Site.objects.get_current()
    return ''.join((
        'https' if https else 'http',
        '://',
        site.domain,
        url
    ))
    return '%s%s%s' % (site.domain, url)
