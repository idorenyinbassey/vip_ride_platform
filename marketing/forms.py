from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Lead, HotelPartnership


class BaseLeadForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        label=_('I agree to be contacted'),
    )

    class Meta:
        model = Lead
        fields = [
            'full_name', 'email', 'phone', 'company', 'country',
            'message', 'consent'
        ]


class ContactLeadForm(BaseLeadForm):
    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.lead_type = Lead.LeadType.CONTACT
        if commit:
            obj.save()
        return obj


class PrivateDriverLeadForm(BaseLeadForm):
    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.lead_type = Lead.LeadType.DRIVER_PRIVATE
        if commit:
            obj.save()
        return obj


class FleetDriverLeadForm(BaseLeadForm):
    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.lead_type = Lead.LeadType.DRIVER_FLEET
        if commit:
            obj.save()
        return obj


class VehicleOwnerLeadForm(BaseLeadForm):
    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.lead_type = Lead.LeadType.VEHICLE_OWNER
        if commit:
            obj.save()
        return obj


class HotelPartnerForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        label=_('I agree to be contacted'),
    )

    class Meta:
        model = HotelPartnership
        fields = [
            'hotel_name', 'contact_name', 'email', 'phone', 'city',
            'country', 'rooms_count', 'notes'
        ]
