from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def dashboard_home(request):
    return render(request, 'portal/home.html')


# Client dashboard
@login_required
def client_profile(request):
    return render(request, 'portal/client/profile.html')


@login_required
def client_book_ride(request):
    return render(request, 'portal/client/book.html')


@login_required
def client_ride_history(request):
    return render(request, 'portal/client/rides.html')


@login_required
def client_payments(request):
    return render(request, 'portal/client/payments.html')


@login_required
def client_vip_features(request):
    return render(request, 'portal/client/vip.html')


@login_required
def client_premium_features(request):
    return render(request, 'portal/client/premium.html')


@login_required
def client_wallet(request):
    return render(request, 'portal/client/wallet.html')


@login_required
def client_support(request):
    return render(request, 'portal/client/support.html')


# Driver dashboard
@login_required
def driver_onboarding(request):
    return render(request, 'portal/driver/onboarding.html')


@login_required
def driver_documents(request):
    return render(request, 'portal/driver/documents.html')


@login_required
def driver_earnings(request):
    return render(request, 'portal/driver/earnings.html')


@login_required
def driver_vehicles(request):
    return render(request, 'portal/driver/vehicles.html')


@login_required
def driver_subscription(request):
    return render(request, 'portal/driver/subscription.html')


@login_required
def driver_performance(request):
    return render(request, 'portal/driver/performance.html')


@login_required
def driver_fleet_integration(request):
    return render(request, 'portal/driver/fleet.html')
