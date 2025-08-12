from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.conf import settings
from urllib.parse import urlencode
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import (
    ContactLeadForm,
    PrivateDriverLeadForm,
    FleetDriverLeadForm,
    VehicleOwnerLeadForm,
    HotelPartnerForm,
)


def home(request):
    return render(request, 'marketing/home.html')


def pricing(request):
    # Simple pricing estimator by tier and distance
    tier = (request.GET.get('tier') or 'normal').lower()
    try:
        distance = float(request.GET.get('distance') or 10)
    except (TypeError, ValueError):
        distance = 10.0

    per_km = {
        'normal': 1.2,
        'premium': 2.0,
        'vip': 3.0,
    }.get(tier, 1.2)

    estimate = round(distance * per_km, 2)

    commission = settings.COMMISSION_RATES.get(
        tier.upper(), {'min': 0.15, 'max': 0.20}
    )
    ctx = {
        'tier': tier,
        'distance': distance,
        'estimate': estimate,
        'commission_min': commission.get('min'),
        'commission_max': commission.get('max'),
    }

    # HTMX request -> return fragment only
    if request.headers.get('HX-Request'):
        return render(request, 'marketing/_pricing_result.html', ctx)

    # JSON estimate for API clients
    if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
        from django.http import JsonResponse
        return JsonResponse(ctx)

    # Full page
    return render(request, 'marketing/pricing.html', ctx)


def login_page(request):
    """Marketing-facing login page that posts to API JWT login."""
    return render(request, 'marketing/login.html')


def signup_page(request):
    """Marketing-facing signup page that posts to API registration."""
    return render(request, 'marketing/signup.html')


def forgot_password(request):
    """Simple forgot password page to capture email; backend flow can be wired later."""
    return render(request, 'marketing/forgot_password.html')


@require_POST
def submit_forgot_password(request):
    email = request.POST.get('email', '').strip()
    if not email:
        messages.error(request, 'Email is required')
        return redirect(reverse('marketing:forgot_password'))
    # In a future iteration, call a password reset API or send email
    return redirect(f"{reverse('marketing:thank_you')}?"
                    f"{urlencode({'email': email})}")


def driver_signup(request):
    context = {
        'private_form': PrivateDriverLeadForm(),
        'fleet_form': FleetDriverLeadForm(),
        'owner_form': VehicleOwnerLeadForm(),
    }
    return render(request, 'marketing/driver_signup.html', context)


def hotels(request):
    return render(
        request, 'marketing/hotels.html', {'form': HotelPartnerForm()}
    )


def contact(request):
    return render(
        request, 'marketing/contact.html', {'form': ContactLeadForm()}
    )


@require_POST
def submit_contact(request):
    form = ContactLeadForm(request.POST)
    if form.is_valid():
        lead = form.save()
        url = reverse('marketing:thank_you')
        return redirect(f"{url}?{urlencode({'lead': str(lead.id)})}")
    return render(request, 'marketing/contact.html', {'form': form})


@require_POST
def submit_private_driver(request):
    form = PrivateDriverLeadForm(request.POST)
    if form.is_valid():
        lead = form.save()
        url = reverse('marketing:thank_you')
        return redirect(f"{url}?{urlencode({'lead': str(lead.id)})}")
    return render(request, 'marketing/driver_signup.html', {
        'private_form': form,
        'fleet_form': FleetDriverLeadForm(),
        'owner_form': VehicleOwnerLeadForm(),
    })


@require_POST
def submit_fleet_driver(request):
    form = FleetDriverLeadForm(request.POST)
    if form.is_valid():
        lead = form.save()
        url = reverse('marketing:thank_you')
        return redirect(f"{url}?{urlencode({'lead': str(lead.id)})}")
    return render(request, 'marketing/driver_signup.html', {
        'private_form': PrivateDriverLeadForm(),
        'fleet_form': form,
        'owner_form': VehicleOwnerLeadForm(),
    })


@require_POST
def submit_vehicle_owner(request):
    form = VehicleOwnerLeadForm(request.POST)
    if form.is_valid():
        lead = form.save()
        url = reverse('marketing:thank_you')
        return redirect(f"{url}?{urlencode({'lead': str(lead.id)})}")
    return render(request, 'marketing/driver_signup.html', {
        'private_form': PrivateDriverLeadForm(),
        'fleet_form': FleetDriverLeadForm(),
        'owner_form': form,
    })


@require_POST
def submit_hotel_partner(request):
    form = HotelPartnerForm(request.POST)
    if form.is_valid():
        partner = form.save()
        url = reverse('marketing:thank_you')
        return redirect(f"{url}?{urlencode({'hotel': str(partner.id)})}")
    return render(request, 'marketing/hotels.html', {'form': form})


def thank_you(request):
    return render(request, 'marketing/thank_you.html')
