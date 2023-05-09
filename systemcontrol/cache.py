
from django.core.cache import CacheHandler, cache

from .models import Country

DEFAULT_TIMEOUT = 60 * 60 * 24 * 7


def get_countries():
    key = 'countries'

    country_data = cache.get_or_set(key, None, DEFAULT_TIMEOUT)

    if country_data is None:
        country_data = Country.objects.all()

        cache.set(key, country_data, DEFAULT_TIMEOUT)

    return country_data
