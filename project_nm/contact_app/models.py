import uuid
from datetime import timedelta
from model_utils import Choices
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from .managers import AppUserManager
from .mixins import (
    TimeStampMixin,
    SoftDeleteMixin
)
from django.conf import settings



# LOGIN_TYPE = Choices(
#         ("Apple", "Apple"),
#         ("Google", "Google"),
#         ("Simple", "Simple"),
#     )

class LoginType(models.TextChoices):
    APPLE = "Apple", "Apple"
    GOOGLE = "Google", "Google"
    SIMPLE = "Simple", "Simple"

class AppUser(
    AbstractBaseUser,
    PermissionsMixin,
    TimeStampMixin,
    SoftDeleteMixin
):
    username_validator = UnicodeUsernameValidator()
    uuid = models.UUIDField(
        verbose_name=_('uuid'),
        unique=True,
        help_text=_('Required. A 32 hexadecimal digits number as specified in RFC 4122.'),
        error_messages={
            'unique': _('A user with that uuid already exists.'),
        },
        default=uuid.uuid4,
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    # full_name = models.CharField(max_length=2048, blank=True, null=True)
    email = models.EmailField(_('email address'), null=True, blank=True, unique=True,
                              error_messages={'unique': _('A user with that email already exists.')}, )
    full_name = models.CharField(_('full name'),max_length=2048, blank=True, null=True)
    mobile_number = models.CharField(_('mobile number'),max_length=20, blank=True, null=True)
    is_email_verified = models.BooleanField(_('email verified'), default=True)
    emp_id = models.CharField(_('employee id'), max_length=30, unique=True, null=True, blank=True)

    # Social Login Fields
    login_type = models.CharField(choices=LoginType.choices, default=LoginType.SIMPLE, max_length=7)
    social_key = models.CharField(max_length=2048, blank=True, null=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_modified = models.DateTimeField(_('last modified'), auto_now=True)
    last_user_activity = models.DateTimeField(_('last activity'), default=timezone.now)

    objects = AppUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "app_users"
        verbose_name = "App User"
        verbose_name_plural = "App Users"

    def __str__(self):
        return self.email or str(self.uuid)

# class UserSetting(models.Model):
#     user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='user_settings')
#
#     theme_setting = models.BooleanField(_('theme setting'), default=False)
#     card_pre_sort = models.BooleanField(_('card pre sort'), default=False)
#     card_slide = models.BooleanField(_('card slide'), default=False)
#     show_stack_in_big_blind = models.BooleanField(_('show stack in big blind'), default=False)
#     time_bank = models.BooleanField(_('time bank'), default=False)
#     enhanced_view = models.BooleanField(_('enhanced view'), default=False)
#     sound_setting = models.BooleanField(_('sound setting'), default=False)
#
#     class Meta:
#         verbose_name = _('Table Settings')
#         verbose_name_plural = _('Table Settings')
#
#     def __str__(self):
#         return str(self.user)



class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,)
    is_active = models.BooleanField(default=True,)
    is_deleted = models.BooleanField(default=False,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
    )

    class Meta:
        abstract = True


class City(BaseModel):
    name = models.CharField(max_length=255, unique=True,)

    class Meta:
        db_table = "city_master"
        ordering = ("name",)

    def __str__(self):
        return self.name


class CountryCode(BaseModel):
    country_name = models.CharField(max_length=255,)
    country_code = models.CharField(max_length=10,unique=True,)
    iso_code = models.CharField(max_length=10,unique=True,)
    is_default = models.BooleanField(default=False,)

    class Meta:
        db_table = "country_code_master"
        ordering = ("country_name",)

    def __str__(self):
        return f"{self.country_name} ({self.country_code})"


class Festival(BaseModel):
    name = models.CharField(max_length=255,unique=True,)
    festival_date = models.DateField()
    description = models.TextField(null=True,blank=True,)
    reminder_days_before = models.PositiveIntegerField(
        default=1,
        help_text="How many days before reminder should trigger",
    )
    is_public_holiday = models.BooleanField(default=False,)
    is_national_holiday = models.BooleanField(default=False,)

    class Meta:
        db_table = "festival_master"
        ordering = ("festival_date",)

    def __str__(self):
        return f"{self.name} - {self.festival_date}"


class Contact(BaseModel):
    full_name = models.CharField(max_length=255,)
    mobile_number = models.CharField(max_length=20,)
    email = models.EmailField(null=True,blank=True,)
    full_address = models.TextField(null=True,blank=True,)
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="contacts",
    )
    country_code = models.ForeignKey(
        CountryCode,
        on_delete=models.PROTECT,
        related_name="contacts",
        default=1,
    )
    festivals = models.ManyToManyField(
        Festival,
        blank=True,
        related_name="contacts",
    )
    is_gift_reminder = models.BooleanField(default=False,)

    class Meta:
        db_table = "contact"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["mobile_number"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.full_name


class ContactPhoto(BaseModel):
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    image = models.ImageField(
        upload_to="contact/photos/",
    )

    class Meta:
        db_table = "contact_photo"

    def __str__(self):
        return f"{self.contact.full_name} Photo"