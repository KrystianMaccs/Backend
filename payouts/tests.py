from django.test import TestCase
from django.contrib.auth import get_user_model

from payouts.models import Payout
from payouts.tasks import *

User = get_user_model()

admin = User.objects.first()
payout = Payout.objects.first()

populate_artist_payout(payout, admin)
