from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Artist, BankAccount, ArtistStorage, CustomUser, UserPhoto, StaffProfile
from .forms import (ArtistChangeForm, ArtistCreationForm)

admin.site.site_header = 'GoCreate Administration'
admin.site.site_title = 'GoCreate'


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    ordering = ('email', 'first_name', 'last_name')
    list_display_links = ['username', 'email']
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "date_joined",
        "last_login",
        "is_superuser",
        "is_staff",
    ]
    fieldsets = (
        (None, {"fields": ("password",)}),
        (
            _("Personal info"),
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "mobile_no",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
@admin.register(UserPhoto)
class UserPhotoAdmin(admin.ModelAdmin):
    pass


@admin.register(ArtistStorage)
class ArtistStorageAdmin(admin.ModelAdmin):
    pass


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('user__is_active', 'user__is_staff', 'user__groups')
    search_fields = ('user__first_name', 'user__last_name')


@admin.register(Artist)
class ArtistAdmin(BaseUserAdmin):

    form = ArtistChangeForm
    add_form = ArtistCreationForm

    list_display = (
        'email',
        'first_name',
        'last_name',
        'phone',
        'lga'
    )

    list_filter = (
        'is_active',
        'last_login',
        'date_joined',
        'sor',
        'lga',

    )

    search_fields = (
        'email',
        'first_name',
        'last_name',
        'other_names',
        'phone'
    )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (
            'first_name',
            'last_name',
            'other_names',
            'phone'
        )}),
        ('Residence', {'fields': ('sor', 'lga')}),
        (None, {'fields': ('is_active', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'other_names',
                'phone',
                'sor',
                'lga',
                'password1',
                'password2'
            ),
        }),
    )

    ordering = ('email', 'first_name', 'last_name', 'phone')

    filter_horizontal = ()
