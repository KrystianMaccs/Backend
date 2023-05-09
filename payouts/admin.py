from django.contrib import admin
from .models import Charge, PayoutHistory, PayoutDue, Payout


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        'amount',
        'pay_due',
        'triggered',
        'payment_approved',
        'confirm_by'
    )

    list_filter = (
        'confirm_by',
        'payment_approved',
        'triggered'
    )

    search_fields = (
        'confirm_by__first_name',
        'confirm_by__last_name',
    )


@admin.register(PayoutDue)
class PayoutDueAdmin(admin.ModelAdmin):
    list_display = (
        'due_date',
    )


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'amount',
        'charge_type',
        'max_fee'
    )


@admin.register(PayoutHistory)
class PayoutHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'payout',
        'total_paid',
        'paid_artists',
        'gross',
        'artists_count'
    )

    list_filter = (
        'payout',
    )
