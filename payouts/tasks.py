from django_q.tasks import async_task
from django.utils import timezone
from django.db.models import Sum
from subscriptions.models import Package

from utils.api.paystack import initiate_bulk
from subscriptions.utils import (get_active_plan, get_artist_active_plan)
from royalty.utils import get_or_create_royalty

import random
import time

from .utils import get_trans_id
from .models import (SongSales, Payout, ArtistPayout,
                     RoyaltyPayout, Charge, PayoutHistory)
from .cache import get_song_update_in_progress_status, set_song_update_in_progress_status

song_update_in_progress = False


def count_slipter(count):
    result = 10

    if count >= 1000:
        result = 100

    elif count >= 10000:
        result = 1000

    elif count >= 1000000:
        result = 10000

    return result


def calculate_percent(total, percent):
    return (total * percent) / 100


def plan_report_handler(plan, pay_due):
    songs = plan.song_set.all()
    for song in songs:
        sales, created = SongSales.objects.get_or_create(
            song=song,
            pay_due=pay_due
        )
        async_task('utils.api.eveara.test_song_report', song, sales)


def track_plans(plans, pay_due):
    set_song_update_in_progress_status(True)
    for plan in plans:
        async_task('payouts.tasks.plan_report_handler', plan, pay_due)
    set_song_update_in_progress_status(False)


def update_song_payment_history(pay_due):
    song_update_in_progress = get_song_update_in_progress_status()
    if not song_update_in_progress:
        plans = get_active_plan()
        track_plans(plans, pay_due)


def populate_artist_payout(payout, admin):
    plans = get_active_plan(feature=Package.GO_DISTRO)
    percent_charges = Charge.objects.values(
        'amount',).filter(charge_type="PERCENTAGE")
    flat_charges = Charge.objects.values('amount',).filter(charge_type="FLAT")

    percent_charges = sum([obj['amount'] for obj in percent_charges])
    flat_charges = sum([obj['amount'] for obj in flat_charges])

    royaltys_payout = {}
    artist_payout_data = {}
    plans_completed = []

    total_payable = 0
    pay_due = payout.pay_due

    for plan in plans:
        if plan.id not in plans_completed:
            song_subs = plan.songsubscription_set.all()
            songs = (song_sub.song for song_sub in song_subs)

            for song in songs:

                artist = song.artist

                artist_payout, created = ArtistPayout.objects.get_or_create(
                    artist=artist,
                    pay_due=pay_due
                )

                if not artist_payout.paid and not artist_payout.is_processing or artist_payout.failed:
                    active_plans = get_artist_active_plan(
                        artist, feature=Package.GO_DISTRO)

                    total_amount = 0
                    artist_songs = []
                    artist_royalties = []
                    artist_royalties_payout = {}

                    for p in active_plans:

                        active_song_subs = p.songsubscription_set.all()
                        active_songs = (
                            song_sub.song for song_sub in active_song_subs)

                        for s in active_songs:
                            royalties = s.royaltysplit_set.all()
                            sales, created = SongSales.objects.get_or_create(
                                song=song,
                                pay_due=pay_due
                            )
                            sales_revenue = sales.revenue

                            artist_royalties = [
                                {'split': split, 'song_revenue': sales_revenue} for split in royalties]

                            total_amount += sales_revenue
                            artist_songs.append(s.id)

                        plans_completed.append(p.id)

                    percent_deduction = calculate_percent(
                        total_amount, percent_charges)

                    total_deduction = percent_deduction + flat_charges
                    avg_deduction = total_deduction / len(artist_songs)

                    artist_royalties_payout, total_royalty_revenue = populate_royalty_payout(
                        royaltys_payout, artist_royalties, avg_deduction)
                    artist_payout.total_deduction = total_deduction
                    artist_payout.gross_profit = total_amount - \
                        total_deduction - total_royalty_revenue
                    artist_payout.royalty_cut = total_royalty_revenue
                    artist_payout.net_profit = total_amount
                    artist_payout.approved_by = admin
                    artist_payout.save()

                    payout.confirm_by = admin
                    payout.save()

                    artist_payout_data[artist.email] = {
                        'artist': artist,
                        "bankaccount": artist.bankaccount,
                        'artist_payout': artist_payout
                    }

                    SongSales.objects.filter(song__in=artist_songs, pay_due=pay_due).update(
                        deduction=avg_deduction)

                    royaltys_payout = artist_royalties_payout

                    total_payable += total_amount - total_royalty_revenue

                    print("Net: ", total_amount)
                    print("Song count: ", len(artist_songs))
                    print("Gross: ", artist_payout.gross_profit)
                    print("Royalty count: ", len(royaltys_payout))
                    print("Total Deduction: ", artist_payout.total_deduction)

    royalty_payouts_rp = update_royalty_payout(royaltys_payout, payout, admin)
    transformed_artist, transformed_royalty = transform_payout_data(
        royalty_payouts_rp, artist_payout_data, royaltys_payout)

    # async_task('payouts.tasks.pay', payout,
    #            transformed_artist, transformed_royalty)

    # async_task('payouts.tasks.pay_bulk', payout,
    #            transformed_artist, transformed_royalty)

    # pay(payout, transformed_artist, transformed_royalty)


def populate_royalty_payout(old_royalties, royalty_slipts, avg_deduction):
    royalties_obj = old_royalties
    for obj in royalty_slipts:
        r = obj['split']
        song_revenue = obj['song_revenue']
        email = r.email
        royalty = get_or_create_royalty(email)

        try:
            if royalty is not None:
                init_royalty = royalties_obj.get(email, None)

                if init_royalty is None:
                    royalties_obj[email] = {
                        'royalty': royalty,
                        'profile': royalty.royaltyprofile,
                        'royalty_split': [r],
                        'amount': 0,
                        'song_revenue': song_revenue
                    }

                else:
                    init_royalty['royalty_split'].append(r)
                    royalties_obj[email] = init_royalty
        except Exception as e:
            print('Populate Royalty payout failed ')
            print(e)
            pass

    royalties_obj, total_revenue = calc_royalty_gross(
        royalties_obj, avg_deduction)
    return royalties_obj, total_revenue


def calc_royalty_gross(royalties, avg_deduction=0):
    update_royalties = {}

    total_revenue = 0
    for k, v in royalties.items():
        for rs in v['royalty_split']:
            song_revenue = v['song_revenue'] - avg_deduction
            percent_value = calculate_percent(song_revenue, rs.share)
            v['amount'] += percent_value
            total_revenue += percent_value

        update_royalties[k] = v

    return update_royalties, total_revenue


def update_royalty_payout(royalties, payout, admin):
    royalty_payouts = {}
    for k, v in royalties.items():
        print(f"Royalty ({k}): ", v['amount'])
        rp, created = RoyaltyPayout.objects.select_related('royalty').get_or_create(
            pay_due=payout.pay_due, royalty=v['royalty'])

        rp.amount = v['amount']
        rp.deduction = 0
        rp.approved_by = admin
        rp.transaction_id = get_trans_id(rp)
        rp.is_processing = True
        rp.royalty_split.set([*v['royalty_split']])
        rp.save()

        royalty_payouts[str(rp.royalty_id)] = rp

    return royalty_payouts


def transform_payout_data(royalty_payouts, artist, royalty):
    artists = []
    royalties = []

    date = ''
    for k, v in artist.items():
        artist_payout: ArtistPayout = v['artist_payout']
        artist_payout.is_processing = True
        artist_payout.transaction_id = get_trans_id(artist_payout)
        date = f"{artist_payout.pay_due.due_date.month}/{artist_payout.pay_due.due_date.year}"
        new_data = {
            # "source": "balance",
            # "reason":  f"Gocreate Royalty for  {date}",
            "amount": artist_payout.gross_profit * 100,
            "recipient": v["bankaccount"].recipient_code,
            "reference": artist_payout.transaction_id,
            # "artist_payout": artist_payout
        }

        print(artist_payout.transaction_id)
        artist_payout.save()
        artists.append(new_data)

    for k, v in royalty.items():
        rp = royalty_payouts.get(str(v["profile"].royalty_id))
        new_data = {
            # "source": "balance",
            # "reason":  f"Gocreate Royalty for {date}",
            "amount": v['amount'] * 100,
            "reference": rp.transaction_id,
            "recipient": v["profile"].recipient_code,
            # "rp": rp
        }

        royalties.append(new_data)

    # total_payable = artists + royalties
    return artists, royalties


def pay_bulk(payout: Payout, payable_artist, payable_royalty):
    PayoutHistory.objects.get_or_create(payout=payout)
    transfer_data = payable_artist + payable_royalty
    payload = {
        "currency": "NGN",
        "source": "balance",
        "transfers": transfer_data
    }
    status, result = initiate_bulk(payload)

    if status:
        for response in result:
            account_number = response.get('recipient')
            transfer_code = response.get('transfer_code')

            ap = ArtistPayout.objects.filter(
                pay_due=payout.pay_due, artist__bankaccount__recipient_code=account_number)
            rp = RoyaltyPayout.objects.filter(
                pay_due=payout.pay_due, royalty__royaltyprofile__recipient_code=account_number)

            if ap.exists():
                confirm_ap: ArtistPayout = ap.first()
                confirm_ap.is_processing = True
                confirm_ap.transaction_reference = transfer_code
                confirm_ap.save()

            elif rp.exists():
                confirm_rp: RoyaltyPayout = rp.first()
                confirm_rp.is_processing = True
                confirm_rp.transaction_id = transfer_code
                confirm_rp.save()
    else:
        raise RuntimeError(result)


def transfer_listener(data):
    account_number = data['recipient'].get('recipient_code')
    transfer_ref = data['transfer_code']
    amount = data['amount']

    is_success = data['status'] == 'success'
    failed = data['status'] == 'failed'

    ap = ArtistPayout.objects.filter(
        transaction_reference=transfer_ref, artist__bankaccount__recipient_code=account_number)
    rp = RoyaltyPayout.objects.filter(
        transaction_id=transfer_ref, royalty__royaltyprofile__recipient_code=account_number)

    if ap.exists():
        confirm_ap: ArtistPayout = ap.first()
        confirm_ap.gross_profit = float(amount)
        confirm_ap.paid = is_success or failed
        confirm_ap.is_processing = False
        confirm_ap.save()

        async_task('payouts.tasks.update_payout_history', confirm_ap.pay_due)

    elif rp.exists():
        confirm_rp: RoyaltyPayout = rp.first()
        confirm_rp.paid = is_success or failed
        confirm_rp.amount = float(amount)
        confirm_rp.is_processing = False
        confirm_rp.save()

        async_task('payouts.tasks.update_payout_history', confirm_rp.pay_due)


def verify_transfers(pay_due):
    artist_payouts = pay_due.artistpayout_set.filter(
        is_processing=True, failed=False, paid=False)
    royalty_payouts = pay_due.royaltypayout_set.filter(
        is_processing=True, failed=False, paid=False)

    ap_count = artist_payouts.count()
    rp_count = royalty_payouts.count()

    for ap in artist_payouts:
        ap_count -= 1
        async_task('utils.api.paystack.verify_transfer', ap, index=ap_count)

    for rp in royalty_payouts:
        rp_count -= 1
        async_task('utils.api.paystack.verify_transfer', rp, index=rp_count)


def update_payout_history(pay_due):
    history = PayoutHistory.objects.select_related(
        'payout', 'payout__pay_due').get(payout__pay_due=pay_due)
    payout = history.payout

    artist_gross = ArtistPayout.objects.filter(
        paid=True, pay_due=pay_due).aggregate(Sum("gross_profit"))['gross_profit__sum']
    royalty_gross = RoyaltyPayout.objects.filter(
        paid=True,  pay_due=pay_due).aggregate(Sum("amount"))['amount__sum']

    artist_gross = artist_gross if artist_gross is not None else 0
    royalty_gross = royalty_gross if royalty_gross is not None else 0
    total_paid = artist_gross + royalty_gross

    history.total_paid = total_paid
    history.gross = payout.amount - total_paid
    history.paid_artists = ArtistPayout.objects.filter(
        pay_due=pay_due, paid=True).count()
    history.paid_artist_royalty = RoyaltyPayout.objects.filter(
        pay_due=pay_due, paid=True).count()
    history.artists_count = ArtistPayout.objects.filter(
        pay_due=pay_due).count()
    history.royalty_count = RoyaltyPayout.objects.filter(
        pay_due=pay_due).count()
    history.save()


def pay(payout, payable_artist, payable_royalty):
    history, created = PayoutHistory.objects.get_or_create(payout=payout)
    total_success_paid = 0
    artist_paid_count = 0
    royalty_paid_count = 0

    for p in payable_artist:
        artist_payout = p.pop('artist_payout')
        print("Paying Artist: ", str(artist_payout.artist))
        # status, result = make_transfer(p)
        status, result = True, {'transfer_code': str(
            random.randrange(10000, 90000))}
        if status:
            artist_payout.paid = True
            artist_payout.failed = False
            artist_payout.transaction_reference = result['transfer_code']
            total_success_paid += p['amount']
            artist_paid_count += 1
        else:
            artist_payout.paid = False
            artist_payout.failed = True

        artist_payout.save()

    for p in payable_royalty:
        royalty_payout = p.pop('rp')
        print("Paying royalty ", str(royalty_payout.royalty))
        # status, result = make_transfer, initial(p)
        status, result = True, {'transfer_code': str(
            random.randrange(10000, 90000))}
        if status:
            royalty_payout.paid = True
            royalty_payout.fail = False
            total_success_paid += p['amount']
            royalty_paid_count += 1
        else:
            royalty_payout.paid = False
            royalty_payout.fail = True

        royalty_payout.save()

    history.total_paid += total_success_paid
    history.paid_artists += artist_paid_count
    history.paid_artist_royalty += royalty_paid_count
    history.gross = payout.amount - history.total_paid
    history.artists_count = ArtistPayout.objects.filter(
        pay_due__id=payout.pay_due_id).count()
    history.royalty_count = RoyaltyPayout.objects.filter(
        pay_due__id=payout.pay_due_id).count()
    history.save()
