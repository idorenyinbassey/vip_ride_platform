class Constants {
  // App Configuration
  static const String appName = 'VIP Ride Platform';
  static const String appVersion = '1.0.0';

  // API Configuration
  static const String baseUrl = 'https://api.vipride.com';
  static const String apiVersion = 'v1';

  // Payment Configuration
  static const String stripePublicKey = 'pk_test_your_stripe_public_key';
  static const String paystackPublicKey = 'pk_test_your_paystack_public_key';

  // Premium Card Pricing
  static const Map<String, double> premiumCardPricing = {
    'vip': 50000.0,
    'premium': 100000.0,
  };

  // Premium Card Features
  static const Map<String, List<String>> premiumCardFeatures = {
    'vip': [
      'Priority booking',
      'Premium vehicles',
      'Dedicated support',
      '24/7 concierge service',
    ],
    'premium': [
      'All VIP features',
      'Luxury vehicle access',
      'Hotel partnerships',
      'Emergency assistance',
      'Personal concierge',
      'Encrypted tracking',
    ],
  };

  // Colors
  static const int primaryColor = 0xFF1A237E;
  static const int secondaryColor = 0xFFFFD700;
  static const int accentColor = 0xFF3F51B5;

  // Animation Durations
  static const int shortAnimationDuration = 300;
  static const int mediumAnimationDuration = 500;
  static const int longAnimationDuration = 1000;

  // Network Timeouts
  static const int connectionTimeout = 30000; // 30 seconds
  static const int receiveTimeout = 30000; // 30 seconds

  // Validation Rules
  static const int minPasswordLength = 8;
  static const int maxPasswordLength = 128;
  static const String emailPattern =
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
  static const String phonePattern = r'^\+?[1-9]\d{1,14}$';

  // Storage Keys
  static const String userTokenKey = 'user_token';
  static const String userIdKey = 'user_id';
  static const String premiumStatusKey = 'premium_status';
  static const String biometricEnabledKey = 'biometric_enabled';

  // Error Messages
  static const String networkErrorMessage =
      'Please check your internet connection';
  static const String serverErrorMessage =
      'Server error occurred. Please try again';
  static const String unauthorizedMessage =
      'Session expired. Please login again';
  static const String validationErrorMessage =
      'Please check your input and try again';
}
