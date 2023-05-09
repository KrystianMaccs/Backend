from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Artist


class ArtistCreationForm(UserCreationForm):

    class Meta:
        model = Artist
        fields = ('email', 'first_name', 'last_name', 'phone',
                  'sor', 'lga', 'address', 'dob')


class ArtistChangeForm(UserChangeForm):

    class Meta:
        model = Artist
        fields = ('email', 'first_name', 'last_name', 'phone',
                  'sor', 'lga', 'address', 'dob')
