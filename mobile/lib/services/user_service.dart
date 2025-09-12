import '../models/user_model.dart';
import 'api_service.dart';

class UserService {
  static final UserService _instance = UserService._internal();
  factory UserService() => _instance;
  UserService._internal();

  final ApiService _apiService = ApiService();

  Future<User?> getCurrentUser() async {
    try {
      // Use the new Flutter tier status endpoint for comprehensive user data
      final response = await _apiService.get(
        '/api/v1/accounts/flutter/tier-status/',
      );
      if (response.statusCode == 200) {
        // Extract user data from the enhanced response
        final data = response.data;
        final userData = data['user'];
        final tierInfo = data['tier_info'];

        // Create user with enhanced tier information
        return User.fromJson({
          ...userData,
          'tier_info': tierInfo,
          'premium_cards': data['premium_cards'],
          'device': data['device'],
          'requirements': data['requirements'],
        });
      }
    } catch (e) {
      // Fallback to old endpoint if new one fails
      try {
        final response = await _apiService.get('/api/v1/accounts/profile/');
        if (response.statusCode == 200) {
          return User.fromJson(response.data);
        }
      } catch (fallbackError) {
        // Handle error
      }
    }
    return null;
  }

  Future<User?> getUserProfile() async {
    return getCurrentUser();
  }

  Future<String?> getUserTier() async {
    try {
      final user = await getCurrentUser();
      return user?.tier;
    } catch (e) {
      // Handle error
    }
    return null;
  }

  Future<bool> updateUserProfile(Map<String, dynamic> data) async {
    try {
      final response = await _apiService.put(
        '/api/v1/accounts/profile/',
        data: data,
      );
      return response.statusCode == 200;
    } catch (e) {
      // Handle error
    }
    return false;
  }

  /// Register device as trusted during login for admin tracking
  Future<bool> registerTrustedDevice({String? deviceName}) async {
    try {
      final response = await _apiService.post(
        '/api/v1/accounts/devices/',
        data: {
          'action': 'register',
          'device_name': deviceName ?? 'Flutter Mobile App',
        },
      );
      return response.statusCode == 200 && response.data['success'] == true;
    } catch (e) {
      // Handle error - device registration failure shouldn't block login
      print('Device registration failed: $e');
    }
    return false;
  }

  /// Refresh user tier status (call after card activation)
  Future<Map<String, dynamic>?> refreshTierStatus() async {
    try {
      final response = await _apiService.get(
        '/api/v1/accounts/flutter/tier-status/',
      );
      if (response.statusCode == 200) {
        return response.data;
      }
    } catch (e) {
      print('Tier status refresh failed: $e');
    }
    return null;
  }
}
