from typing import List
import uuid
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as  _
from django.contrib.auth.models import User as BaseUser
from django.contrib.auth.models import AbstractBaseUser

from utils.helper import compressImage, redefinedFileName
from .managers import ArtistManager


User = get_user_model()


class StaffProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=45, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    change_password = models.BooleanField(default=False)


class Artist(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    other_names = models.CharField(_('other names'), max_length=30, blank=True)
    stage_name = models.CharField(_('stage name'), blank=True, max_length=35)
    phone = models.CharField(_('phone number'), unique=True, max_length=15)
    bio = models.CharField(max_length=225, blank=True, null=True)
    music_class = models.CharField(max_length=225, blank=True)
    company_name = models.CharField(max_length=55, blank=True)
    sor = models.CharField(_('state of residence'), blank=True, max_length=225)
    # gender = models.CharField(
    #     _('M Male, F Female, O thers'), max_length=1, null=True, blank=True, default='O')
    lga = models.CharField(_('local government area'),
                           max_length=225, null=True, blank=True)
    address = models.CharField(_('address'), blank=True, max_length=225)
    postal_code = models.CharField(
        _('Postal Code'), blank=True, null=True, max_length=8)
    country = models.CharField(
        _("Country"), max_length=35, null=True, blank=True)
    country_code = models.CharField(
        _('Country Code'), blank=True, max_length=5)
    state = models.CharField(
        _("State"), max_length=25, null=True, blank=True)
    city = models.CharField(_("cite"), max_length=75, null=True, blank=True)
    dob = models.DateField(null=True)
    is_active = models.BooleanField(_('active'), default=False)
    change_password = models.BooleanField(_('change password'), default=False)
    verified = models.BooleanField(_('verify email'), default=False)
    phone_verified = models.BooleanField(_('verify phone'), default=False)
    last_login = models.DateTimeField(_('last login'), null=True, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: List[str] = []

    objects = ArtistManager()

    def has_perms(self, perms):
        return False

    def has_perm(self, perm):
        return False

    @property
    def get_full_name(self):
        return f"{self.first_name.capitalize()} {self.last_name.capitalize()} {self.other_names.capitalize()}"

    def __str__(self):
        return self.get_full_name


class UserPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE)
    artist = models.OneToOneField(
        Artist, null=True, blank=True, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=redefinedFileName, null=True, blank=True)

    directory_string_var = 'files/profile-pictures'

    def save(self, *args, **kwargs):
        self.image = compressImage(self.image)
        super(UserPhoto, self).save(*args, **kwargs)


class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.OneToOneField(Artist, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=19, blank=True, null=True)
    bank_name = models.CharField(max_length=75, blank=True, null=True)
    bank_code = models.CharField(max_length=25, null=True, blank=True)
    bank_iban = models.CharField(max_length=25, null=True, blank=True)
    bank_swift = models.CharField(max_length=25, null=True, blank=True)
    route_no = models.CharField(max_length=25, null=True, blank=True)
    bank_branch = models.CharField(max_length=200, null=True, blank=True)
    recipient_code = models.CharField(max_length=25, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return self.artist.get_full_name
        except:
            return self.account_number


class ArtistStorage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.OneToOneField(Artist, on_delete=models.CASCADE)
    used_space = models.FloatField(default=.0)
    total_space = models.FloatField(default=200)
    timestamp = models.DateTimeField(auto_now_add=True)


class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.BigIntegerField(blank=False)
    counter = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    expiry = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.phone)


class ArtistMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.OneToOneField(Artist, on_delete=models.CASCADE)
    eveara_artist_id = models.CharField(max_length=11, null=True, blank=True)
    eveara_user_id = models.CharField(max_length=40, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
