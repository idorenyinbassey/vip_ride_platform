from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid


class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Lead(TimeStampedModel):
    class LeadType(models.TextChoices):
        CONTACT = 'contact', _('Contact')
        DRIVER_PRIVATE = 'driver_private', _('Private Driver')
        DRIVER_FLEET = 'driver_fleet', _('Fleet Company')
        VEHICLE_OWNER = 'vehicle_owner', _('Vehicle Owner')
        HOTEL_PARTNER = 'hotel_partner', _('Hotel Partner')

    lead_type = models.CharField(max_length=40, choices=LeadType.choices)
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    company = models.CharField(max_length=160, blank=True)
    country = models.CharField(max_length=80, blank=True)
    message = models.TextField(blank=True)
    consent = models.BooleanField(
        default=False,
        help_text=_('I agree to be contacted.')
    )
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    page = models.CharField(max_length=160, blank=True)
    language = models.CharField(
        max_length=8,
        default='en',
        choices=[
            (code, name)
            for code, name in getattr(
                settings, 'LANGUAGES', [('en', 'English')]
            )
        ]
    )

    class Meta:
        indexes = [
            models.Index(fields=["lead_type", "created_at"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.lead_type}"


class HotelPartnership(TimeStampedModel):
    hotel_name = models.CharField(max_length=160)
    contact_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=80, blank=True)
    rooms_count = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.hotel_name
