from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from django_q.tasks import async_task
from django_q.models import Schedule

from dateutil import relativedelta
from datetime import datetime

from .models import Advert


def delete_advert(advert_id):
    try:
        adv = Advert.objects.get(id=advert_id)
        adv.file.delete()
        adv.delete()
    except:
        pass


def schedule_expiry(instance):
    plan = instance.plan
    expiry_month = 1

    if plan is not None:
        expiry_month = plan.expiry_month

    date_created = instance.timestamp
    dd = date_created.date() + relativedelta.relativedelta(months=expiry_month)
    expiry_date = datetime(year=dd.year, month=dd.month, day=dd.day)

    Schedule.objects.create(
        name=f'Advert ({instance.short_text})',
        func='advert.signals.delete_advert',
        args=str(instance.id),
        next_run=expiry_date,
        schedule_type="O",
    )


@receiver(post_save, sender=Advert)
def advert_save_receiver(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        schedule_expiry(instance)
