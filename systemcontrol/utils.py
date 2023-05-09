from utils.api.eveara.accounts import get_countries
from .models import Country, SupportedMonitor
from accounts.models import Artist


def is_free_monitor(artist: Artist):
    query = SupportedMonitor.objects.filter(
        country__country_code=artist.country_code)
    return query.exists()


def update_country():
    country_data = get_countries()
    data = country_data['data']

    countries = list(map(lambda d: Country(
        country_name=d['countryName'], country_code=d['countryCode']), data))

    return countries
