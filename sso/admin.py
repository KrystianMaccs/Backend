from django.contrib import admin

from .models import AppAuthLog, IdentityApp


@admin.register(IdentityApp)
class IdentityAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('last_modified', 'date_created', 'is_active')
    search_fields = ('name','description')


@admin.register(AppAuthLog)
class AppAuthLogAdmin(admin.ModelAdmin):
    list_display = ('artist', 'identity_app')

    list_filter = ('approval_request_count',
    'approval_request_timestamp',
    'last_request_timestamp',
    'date_created')

    search_fields = (
        'identity_app__name',
        'artist__stage_name',
        'artist__email',
        'artist__phone',
        'artist__first_name',
        'artist__last_name',
        'artist__other_names',
        'artist__company',
    )

