from .models import Royalty


def get_or_create_royalty(email):
    try:
        royalty = Royalty.objects.select_related(
            'royaltyprofile'
        ).get(username=email)
        return royalty

    except Royalty.DoesNotExist:
        return None
