class ApiConfig {
  // Environment Configuration
  static const bool useMockApi = false; // Set to false for production Django
  static const bool debugMode = true;

  // API URLs
  static const String mockApiUrl = 'http://localhost:8000';
  static const String realApiUrl =
      'http://127.0.0.1:8001'; // Your Django backend
  static const String prodApiUrl = 'https://your-production-domain.com';

  // Dynamic base URL based on environment
  static String get baseUrl {
    if (useMockApi) {
      return mockApiUrl;
    }
    return debugMode ? realApiUrl : prodApiUrl;
  }

  // Authentication endpoints
  static const String loginEndpoint = '/api/v1/accounts/login/';
  static const String registerEndpoint = '/api/v1/accounts/register/';
  static const String refreshTokenEndpoint = '/api/v1/accounts/token/refresh/';
  static const String logoutEndpoint = '/api/v1/accounts/logout/';
  static const String profileEndpoint = '/api/v1/accounts/profile/';

  // MFA endpoints
  static const String mfaVerifyEndpoint = '/api/v1/accounts/auth/mfa/verify/';
  static const String mfaSmsEndpoint = '/api/v1/accounts/auth/mfa/sms/';
  static const String mfaEmailEndpoint = '/api/v1/accounts/auth/mfa/email/';
  static const String mfaTotpSetupEndpoint =
      '/api/v1/accounts/auth/mfa/totp/setup/';
  static const String mfaSetupEndpoint = '/api/v1/accounts/auth/mfa/setup/';

  // Card endpoints
  static const String premiumCardsEndpoint = '/api/v1/accounts/premium-cards/';
  static const String cardActivationEndpoint =
      '/api/v1/accounts/cards/activate/';

  // Ride endpoints
  static const String ridesEndpoint = '/api/v1/rides/';
  static const String rideRequestEndpoint = '/api/v1/rides/workflow/request/';
  static const String rideStatusEndpoint = '/api/v1/rides/status/';
  static const String rideHistoryEndpoint = '/api/v1/rides/history/';
  static const String rideCancelEndpoint = '/api/v1/rides/cancel/';
  static const String activeRidesEndpoint = '/api/v1/rides/workflow/active/';

  // Driver endpoints
  static const String driversEndpoint = '/api/v1/drivers/';
  static const String driverStatusEndpoint = '/api/v1/drivers/status/';
  static const String driverLocationEndpoint = '/api/v1/drivers/location/';
  static const String driverEarningsEndpoint = '/api/v1/drivers/earnings/';

  // Vehicle endpoints
  static const String vehiclesEndpoint = '/api/v1/fleet-management/vehicles/';
  static const String vehicleTypesEndpoint =
      '/api/v1/fleet-management/vehicle-types/';

  // Fleet endpoints
  static const String fleetEndpoint = '/api/v1/fleet-management/companies/';
  static const String fleetDriversEndpoint =
      '/api/v1/fleet-management/drivers/';
  static const String fleetVehiclesEndpoint = '/api/v1/fleet/api/vehicles/';
  static const String fleetCompaniesEndpoint = '/api/v1/fleet/api/companies/';

  // Lease endpoints
  static const String leaseEndpoint = '/api/v1/leasing/contracts/';
  static const String leaseCalculateEndpoint =
      '/api/v1/leasing/calculate-lease/';
  static const String leaseApplicationEndpoint =
      '/api/v1/leasing/applications/';

  // Hotel endpoints (for VIP Premium)
  static const String hotelsEndpoint = '/api/v1/hotel-partnerships/hotels/';
  static const String nearbyHotelsEndpoint =
      '/api/v1/hotel-partnerships/hotels/nearby/';
  static const String hotelBookingsEndpoint =
      '/api/v1/hotel-partnerships/bookings/';
  static const String hotelOffersEndpoint =
      '/api/v1/hotel-partnerships/offers/';

  // Payment endpoints
  static const String paymentsEndpoint = '/api/v1/payments/';
  static const String paymentMethodsEndpoint = '/api/v1/payments/methods/';
  static const String paymentHistoryEndpoint = '/api/v1/payments/history/';
  static const String transactionsEndpoint = '/api/v1/payments/transactions/';

  // GPS and location endpoints
  static const String gpsTrackingEndpoint = '/api/v1/gps/locations/';
  static const String encryptedGpsEndpoint = '/api/v1/gps/encrypt/';
  static const String gpsDecryptEndpoint = '/api/v1/gps/decrypt/';
  static const String gpsKeyExchangeEndpoint = '/api/v1/gps/key-exchange/';
  static const String gpsSessionStatusEndpoint = '/api/v1/gps/sessions/';
  static const String gpsTerminateSessionEndpoint =
      '/api/v1/gps/sessions/terminate/';
  static const String gpsStatsEndpoint = '/api/v1/gps/stats/';
  static const String gpsRealtimeEndpoint = '/api/v1/gps-tracking/realtime/';

  // SOS endpoints
  static const String sosEndpoint = '/api/v1/control-center/sos/';
  static const String emergencyEndpoint = '/api/v1/control-center/emergency/';

  // Pricing endpoints
  static const String pricingEndpoint = '/api/v1/pricing/estimates/';
  static const String surgePricingEndpoint = '/api/v1/pricing/surge/';

  // Notifications endpoints
  static const String notificationsEndpoint =
      '/api/v1/notifications/notifications/';
  static const String markReadEndpoint =
      '/api/v1/notifications/notifications/{id}/mark_read/';

  // Mock API specific endpoints (for testing)
  static const String mockHealthEndpoint = '/health/';
  static const String mockAdminSessionsEndpoint = '/mock/admin/sessions';
  static const String mockAdminDevicesEndpoint = '/mock/admin/devices';
  static const String mockAdminUsersEndpoint = '/mock/admin/users';

  // WebSocket endpoints
  static const String wsBaseUrl = 'ws://127.0.0.1:8001';
  static const String rideTrackingWs = '/ws/rides/';
  static const String gpsTrackingWs = '/ws/gps/';
  static const String notificationsWs = '/ws/notifications/';

  // Flutter-specific endpoints
  static const String flutterTierStatusEndpoint =
      '/api/v1/accounts/flutter/tier-status/';
  static const String flutterCardActivationEndpoint =
      '/api/v1/accounts/flutter/activate-card/';

  // Environment info
  static String get environmentInfo {
    return useMockApi ? 'Mock API' : (debugMode ? 'Development' : 'Production');
  }

  // Full URL builders
  static String getFullUrl(String endpoint) {
    return '$baseUrl$endpoint';
  }

  static Map<String, String> get defaultHeaders {
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (useMockApi) 'X-Mock-API': 'true',
    };
  }

  static Map<String, String> getAuthHeaders(String token) {
    return {...defaultHeaders, 'Authorization': 'Bearer $token'};
  }

  // Timeout settings
  static const int connectionTimeout = 30000; // 30 seconds
  static const int receiveTimeout = 30000; // 30 seconds
  static const int sendTimeout = 30000; // 30 seconds
}

class AppConstants {
  // App Info
  static const String appName = 'VIP Ride Platform';
  static const String appVersion = '1.0.0';

  // User Types (must match Django UserType choices)
  static const String userTypeClient = 'CUSTOMER';
  static const String userTypeDriver = 'DRIVER';

  // Client Tiers (must match Django UserTier choices)
  static const String tierRegular = 'normal';
  static const String tierVip = 'premium';
  static const String tierBlackTier = 'vip';

  // Driver Types
  static const String driverTypeIndependent = 'independent_driver';
  static const String driverTypeFleetOwner = 'fleet_owner';
  static const String driverTypeFleetDriver = 'fleet_driver';
  static const String driverTypeLeased = 'leased_driver';

  // Ride Status
  static const String rideStatusRequested = 'requested';
  static const String rideStatusDriverSearch = 'driver_search';
  static const String rideStatusDriverFound = 'driver_found';
  static const String rideStatusDriverAccepted = 'driver_accepted';
  static const String rideStatusDriverEnRoute = 'driver_en_route';
  static const String rideStatusDriverArrived = 'driver_arrived';
  static const String rideStatusInProgress = 'in_progress';
  static const String rideStatusCompleted = 'completed';
  static const String rideStatusCancelled = 'cancelled_by_rider';

  // Vehicle Types
  static const String vehicleTypeSedan = 'sedan';
  static const String vehicleTypeSuv = 'suv';
  static const String vehicleTypeLuxury = 'luxury';
  static const String vehicleTypeVan = 'van';
  static const String vehicleTypePremium = 'premium';

  // Map Settings
  static const double defaultZoom = 15.0;
  static const double maxZoom = 18.0;
  static const double minZoom = 3.0;

  // Colors
  static const String primaryColorHex = '#1E3A8A'; // Blue
  static const String secondaryColorHex = '#F59E0B'; // Amber
  static const String vipColorHex = '#7C3AED'; // Purple
  static const String blackTierColorHex = '#1F2937'; // Dark Gray

  // Storage Keys
  static const String keyAccessToken = 'access_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyUserData = 'user_data';
  static const String keyUserType = 'user_type';
  static const String keyUserTier = 'user_tier';
  static const String keyDriverType = 'driver_type';
  static const String keyIsFirstRun = 'is_first_run';

  // Permissions
  static const List<String> requiredPermissions = [
    'location',
    'camera',
    'storage',
    'notification',
  ];
}
