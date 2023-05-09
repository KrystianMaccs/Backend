from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from django_q.tasks import async_task

from .models import Payout, PayoutDue, PayoutHistory
from utils.helper import get_next_month_ending

User = get_user_model()


@receiver(post_save, sender=PayoutDue)
def trigger_payout(sender, **kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created')

    if created:
        payout = Payout()
        payout.pay_due = instance
        payout.save()


@receiver(post_save, sender=Payout)
def new_pay_due(sender, **kwargs):
    instance = kwargs.get('instance')
    created = kwargs.get('created')

    if not created:
        paid = instance.payment_approved
        if paid:
            pay_due = PayoutDue()
            pay_due.due_date = get_next_month_ending(
                instance.approval_timestamp)
            pay_due.save()
    else:
        history, created = PayoutHistory.objects.get_or_create(payout=instance)
