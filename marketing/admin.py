from django.contrib import admin
from .models import Lead, HotelPartnership


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "lead_type", "created_at")
    list_filter = ("lead_type", "created_at")
    search_fields = ("full_name", "email", "company")


@admin.register(HotelPartnership)
class HotelPartnershipAdmin(admin.ModelAdmin):
    list_display = ("hotel_name", "contact_name", "email", "created_at")
    search_fields = ("hotel_name", "contact_name", "email")
