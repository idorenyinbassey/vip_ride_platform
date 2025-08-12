from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods


def dashboard_home(request):
    return render(request, 'portal/home.html')


# Client dashboard
def client_profile(request):
    return render(request, 'portal/client/profile.html')


def client_book_ride(request):
    return render(request, 'portal/client/book.html')


def client_ride_history(request):
    return render(request, 'portal/client/rides.html')


def client_payments(request):
    return render(request, 'portal/client/payments.html')


def client_vip_features(request):
    return render(request, 'portal/client/vip.html')


def client_premium_features(request):
    return render(request, 'portal/client/premium.html')


def client_wallet(request):
    return render(request, 'portal/client/wallet.html')


def client_support(request):
    return render(request, 'portal/client/support.html')


# Driver dashboard
def driver_onboarding(request):
    return render(request, 'portal/driver/onboarding.html')


def driver_documents(request):
    return render(request, 'portal/driver/documents.html')


def driver_earnings(request):
    return render(request, 'portal/driver/earnings.html')


def driver_vehicles(request):
    return render(request, 'portal/driver/vehicles.html')


def driver_subscription(request):
    return render(request, 'portal/driver/subscription.html')


def driver_performance(request):
    return render(request, 'portal/driver/performance.html')


def driver_fleet_integration(request):
    return render(request, 'portal/driver/fleet.html')


@never_cache
@require_http_methods(["GET"])
def logout_view(request):
    """
    Server-side session logout; client JS also clears JWTs
    and then we redirect.
    """
    try:
        logout(request)
    finally:
        next_url = request.GET.get('next') or '/login/'
        return redirect(next_url)
