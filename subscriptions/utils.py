from django.db.models import F, Prefetch
from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from django_q.models import Schedule
from django.utils import timezone
import calendar
import time

from django_q.tasks import async_task

from rest_framework import serializers

from accounts.models import Artist

from .models import ArtistSubscription, SubscriptionTransaction, Package
from songs.models import RoyaltySplit, Song, SongSubscription

from utils.api.paystack import verify_transactions
from accounts.tasks import send_email


WARNING_DAY_COUNT = 1


def is_leap_year(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


def add_year(date, years):
    if years > 0:
        if is_leap_year(date.year):
            delta = timedelta(days=(366 * years))
        else:
            delta = timedelta(days=(365 * years))

        return date + delta
    return date


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(int(year), int(month), int(day))


def planIsValid(plan):
    status, message = False, 'Plan has expired'
    if plan is not None:
        package = plan.package

        eta = plan.last_renewed if plan.last_renewed is not None else plan.timestamp
        package_month_eta = add_months(eta, package.eta_months)
        package_year_eta = add_year(package_month_eta, package.eta_years)
        today = timezone.now()
        today = date(today.year, today.month, today.day)

        if package.eta_months > 0 or package.eta_years > 0:
            if package_year_eta > today:
                status, message = True, "Plan is valid"
    else:
        status = 'Plan is not valid.'

    return status, message


def add_expiry_timestamp(plan: ArtistSubscription) -> ArtistSubscription:
    package = plan.package
    eta = plan.last_renewed if plan.last_renewed is not None else timezone.now()
    package_month_eta = add_months(eta, package.eta_months)
    package_year_eta = add_year(package_month_eta, package.eta_years)

    plan.expired_timestamp = package_year_eta

    warning_days = WARNING_DAY_COUNT
    expiry_date = datetime(year=package_year_eta.year,
                           month=package_year_eta.month, day=package_year_eta.day)
    warning_date = expiry_date - timedelta(days=warning_days)

    Schedule.objects.create(
        name=f'Subscription Warning Scheduler',
        func='subscriptions.utils.warning_sub_expire',
        args=str(plan.id),
        next_run=warning_date,
        schedule_type="O"
    )

    Schedule.objects.create(
        name=f'Subscription Expiration Scheduler',
        func='subscriptions.utils.sub_expiration_hanlder',
        args=str(plan.id),
        next_run=expiry_date,
        schedule_type="O",
    )
    plan.save()
    return plan


def create_potential_artistsub(artist: Artist, package: Package, session_id: str) -> None:
    asub: ArtistSubscription = ArtistSubscription.objects.create(
        package=package, artist=artist)

    subTran: SubscriptionTransaction = SubscriptionTransaction.objects.create(
        subscription=asub, transaction_reference=session_id)


def activate_potential_artistsub(session_id: str, gateway: str = None):
    result = None
    subTrans_query = SubscriptionTransaction.objects.select_related(
        'subscription', 'subscription__package').filter(transaction_reference=session_id)

    if subTrans_query.exists():
        subTrans: SubscriptionTransaction = subTrans_query.first()
        subTrans.is_successful = True

        if gateway is not None:
            subTrans.payment_gateway = gateway

        subTrans.save()

        artistSub: ArtistSubscription = subTrans.subscription
        package: Package = artistSub.package

        artistSub = add_expiry_timestamp(artistSub)
        artistSub.eveara_id = package.eveara_id
        artistSub.provisioned = True
        artistSub.activated = True
        artistSub.last_renewed = timezone.now()
        artistSub.save()

        result = artistSub

    return result


def cancel_potential_artistsub(session_id: str) -> None:
    subTrans_query = SubscriptionTransaction.objects.filter(
        transaction_reference=session_id)

    if subTrans_query.exists():
        subTrans: SubscriptionTransaction = subTrans_query.first()
        sub_id: str = subTrans.subscription_id
        subTrans.is_successful = False

        artistSub_qeury = ArtistSubscription.objects.filter(id=sub_id)
        if artistSub_qeury.exists():
            artistSub: ArtistSubscription = artistSub_qeury.first()
            artistSub.provisioned = False

            subTrans.save()
            artistSub.save()


def create_or_renew_plan(validated_data, instance=None):
    package_id = validated_data.get('package', None)
    reference = validated_data.pop('reference')

    try:
        if isinstance(package_id, Package):
            package = package_id
        else:
            package = Package.objects.get(id=package_id)

            if instance is not None:
                if package != instance.package:
                    raise serializers.ValidationError(
                        'Invalid Package. You can change a package, you have to create a new subscription.')

    except Package.DoesNotExist:
        raise serializers.ValidationError('Invalid Package')

    # Validate Transaction
    sub = SubscriptionTransaction.objects.filter(
        transaction_reference=reference)
    if sub.exists():
        raise serializers.ValidationError('Transaction is invalid')

    # payment_valid, message = True, None
    payment_valid, message = verify_transactions(reference, package.price)
    is_new = False
    if payment_valid:

        if instance is not None:
            subscription = instance
        else:
            is_new = True
            subscription: ArtistSubscription = ArtistSubscription.objects.create(
                **validated_data)

        SubscriptionTransaction.objects.get_or_create(
            transaction_reference=reference,
            subscription=subscription
        )

        subscription = add_expiry_timestamp(subscription)
        subscription.expired = False
        subscription.provisioned = True
        subscription.eveara_id = package.eveara_id
        subscription.last_renewed = timezone.now()
        subscription.save()

        package =subscription.package

        if package.feature == Package.GO_DISTRO:

            if not is_new:
                async_task('subscriptions.utils.reactivate_songs', subscription)
                async_task('utils.api.eveara.reactivate_artist_subscription',
                        artist_sub=subscription)

            else:
                async_task('utils.api.eveara.create_artist_subscription',
                        artist_sub=subscription)
        return subscription

    raise serializers.ValidationError(message)


def reactivate_songs(subscription):
    songs = subscription.song_set.all()
    for song in songs:
        async_task('utils.api.eveara.redistribute', song)


def deactivate_expired_plans():
    expired_plans = ArtistSubscription.objects.filter(
        expired_timestamp__lt=timezone.now(),
        expired=False
    )
    expired_plans.update(expired=True)


def get_active_plan(feature=Package.GO_DISTRO):
    plans = ArtistSubscription.objects.prefetch_related(
        Prefetch('songsubscription_set',
                 SongSubscription.objects.prefetch_related(Prefetch('song', Song.objects.select_related(
                     'songmeta').prefetch_related(
                     'songsales_set',
                     'royaltysplit_set').all())).all())
    ).select_related('artist').filter(
        expired_timestamp__gte=timezone.now(),
        package__feature=feature,
        expired=False
    )
    return plans


def get_artist_active_plan(artist, feature=Package.GO_DISTRO):
    plans = ArtistSubscription.objects.prefetch_related(
        Prefetch('songsubscription_set',
                 SongSubscription.objects.prefetch_related(Prefetch('song', Song.objects.select_related(
                     'songmeta').prefetch_related(
                     'songsales_set',
                     'royaltysplit_set').all())).all())
    ).select_related('artist').filter(
        expired_timestamp__gte=timezone.now(),
        package__feature=feature,
        expired=False,
        artist=artist
    )
    return plans


def warning_sub_expire(plan_id):

    plan = ArtistSubscription.objects.prefetch_related(
        Prefetch('song_set', Song.objects.select_related(
            'songmeta').all())
    ).select_related('package', 'artist').filter(pk=plan_id)

    if not plan.exists():
        return None

    plan = plan.first()

    warning_date = plan.expired_timestamp - timedelta(days=WARNING_DAY_COUNT)
    days_left = plan.expired_timestamp - timezone.now()
    days_left = days_left.days

    if days_left <= warning_date.day:
        package = plan.package
        song_titles = ''

        songs = plan.song_set.all()

        for s in songs:
            song_titles += f'{s.title}, '

        song_titles = song_titles.strip()[:-1]
        artist = plan.artist

        mail_subject = 'Gocreate Subscription Expiration'
        message = render_to_string('subscriptions/warning.html', {
            'title': mail_subject,
            'artist': artist,
            'package': package,
            "songs": song_titles
        })

        send_email(mail_subject, message, artist.email)


def sub_expiration_hanlder(plan_id):
    plan = ArtistSubscription.objects.prefetch_related(
        Prefetch('song_set', Song.objects.select_related(
            'songmeta').all())
    ).select_related('package', 'artist').filter(pk=plan_id)

    if plan.exists():
        plan = plan.first()

        expiry_date = timezone.now() - plan.expired_timestamp

        if expiry_date.days <= 0:
            plan.expired = True
            plan.save()

            async_task('utils.api.eveara.deactivate_artist_subscription',
                       artist_sub=plan)

            songs = plan.song_set.all()
            song_titles = ''
            for song in songs:
                song_titles += f'{song.title}, '
                async_task('utils.api.eveara.takedown_album',
                           song=song)

            package = plan.package

            song_titles = song_titles.strip()[:-1]
            artist = plan.artist

            mail_subject = 'Gocreate Subscription Expiration'
            message = render_to_string('subscriptions/expire.html', {
                'title': mail_subject,
                'artist': artist,
                'package': package,
                "songs": song_titles
            })

            send_email(mail_subject, message, artist.email)
