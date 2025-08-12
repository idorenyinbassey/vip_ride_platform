from django.urls import path
from . import views

app_name = 'marketing'

urlpatterns = [
    path('', views.home, name='home'),
    path('pricing/', views.pricing, name='pricing'),
    path('drivers/', views.driver_signup, name='drivers'),
    path('hotels/', views.hotels, name='hotels'),
    path('contact/', views.contact, name='contact'),
    # Auth pages (marketing-facing)
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path(
        'submit/forgot-password/',
        views.submit_forgot_password,
        name='submit_forgot_password'
    ),

    # submissions
    path('submit/contact/', views.submit_contact, name='submit_contact'),
    path(
        'submit/drivers/private/',
        views.submit_private_driver,
        name='submit_private_driver'
    ),
    path(
        'submit/drivers/fleet/',
        views.submit_fleet_driver,
        name='submit_fleet_driver'
    ),
    path(
        'submit/drivers/owner/',
        views.submit_vehicle_owner,
        name='submit_vehicle_owner'
    ),
    path(
        'submit/hotels/',
        views.submit_hotel_partner,
        name='submit_hotel_partner'
    ),

    path('thank-you/', views.thank_you, name='thank_you'),
]
