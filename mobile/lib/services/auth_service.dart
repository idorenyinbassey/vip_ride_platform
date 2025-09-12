import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/user_models.dart';
import '../config/api_config.dart';
import 'api_service.dart';

class AuthService extends ChangeNotifier {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  User? _currentUser;
  bool _isLoading = false;
  String? _error;

  User? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _currentUser != null;

  // Mock API service instance
  final ApiService _apiService = ApiService();

  /// Initialize auth service - check for existing session
  Future<void> initialize() async {
    _setLoading(true);
    try {
      // Check for stored authentication token
      await _checkStoredAuth();
    } catch (e) {
      _setError('Failed to initialize authentication');
    } finally {
      _setLoading(false);
    }
  }

  /// Check for stored authentication
  Future<void> _checkStoredAuth() async {
    try {
      // In a real app, you would check secure storage for tokens
      // For now, we'll simulate this
      final token = await _getStoredToken();
      if (token != null) {
        // Validate token with API and get user info
        final user = await _validateTokenAndGetUser(token);
        if (user != null) {
          _setCurrentUser(user);
        }
      }
    } catch (e) {
      debugPrint('Error checking stored auth: $e');
    }
  }

  /// Get stored authentication token
  Future<String?> _getStoredToken() async {
    try {
      final storage = FlutterSecureStorage();
      return await storage.read(key: 'access_token') ?? _currentAccessToken;
    } catch (e) {
      debugPrint('Token retrieval error: $e');
      return _currentAccessToken;
    }
  }

  /// Validate token and get user information
  Future<User?> _validateTokenAndGetUser(String token) async {
    try {
      // In a real app, make API call to validate token
      // For demo purposes, return null
      return null;
    } catch (e) {
      debugPrint('Error validating token: $e');
      return null;
    }
  }

  /// Sign in with email and password
  Future<bool> signIn(String email, String password) async {
    _setLoading(true);
    _setError(null);

    try {
      final response = await _apiService.post(
        ApiConfig.loginEndpoint,
        data: {'email': email, 'password': password},
      );

      // Handle Django JWT response format
      if (response.statusCode == 200 && response.data['access'] != null) {
        // Store both access and refresh tokens
        await _storeToken(response.data['access']);
        if (response.data['refresh'] != null) {
          await _storeRefreshToken(response.data['refresh']);
        }

        // Get user profile after successful login
        final userProfile = await _getUserProfile();
        if (userProfile != null) {
          _setCurrentUser(userProfile);
          return true;
        } else {
          _setError('Failed to load user profile');
          return false;
        }
      } else {
        _setError('Invalid login response');
        return false;
      }
    } catch (e) {
      if (e.toString().contains('400')) {
        _setError('Invalid email or password');
      } else {
        _setError('Network error. Please try again.');
      }
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Sign up new user
  Future<bool> signUp({
    required String name,
    required String email,
    required String password,
    String? phone,
  }) async {
    _setLoading(true);
    _setError(null);

    try {
      final response = await _apiService.post(
        ApiConfig.registerEndpoint,
        data: {
          'name': name,
          'email': email,
          'password': password,
          'phone': phone,
        },
      );

      // Handle Django response format
      if (response.statusCode == 201 || response.statusCode == 200) {
        // Check if response contains tokens (auto-login after registration)
        if (response.data['access'] != null) {
          await _storeToken(response.data['access']);
          if (response.data['refresh'] != null) {
            await _storeRefreshToken(response.data['refresh']);
          }

          // Get user profile
          final userProfile = await _getUserProfile();
          if (userProfile != null) {
            _setCurrentUser(userProfile);
          }
        }
        return true;
      } else {
        _setError('Registration failed');
        return false;
      }
    } catch (e) {
      _setError('Network error. Please try again.');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Sign out current user
  Future<void> signOut() async {
    try {
      await _apiService.post(ApiConfig.logoutEndpoint, data: {});
      await _clearStoredToken();
      _setCurrentUser(null);
    } catch (e) {
      debugPrint('Error during sign out: $e');
      // Clear local data even if API call fails
      await _clearStoredToken();
      _setCurrentUser(null);
    }
  }

  /// Update user profile
  Future<bool> updateProfile({
    String? name,
    String? phone,
    String? profileImage,
  }) async {
    if (_currentUser == null) return false;

    _setLoading(true);
    _setError(null);

    try {
      final updateData = <String, dynamic>{};
      if (name != null) updateData['name'] = name;
      if (phone != null) updateData['phone'] = phone;
      if (profileImage != null) updateData['profile_image'] = profileImage;

      final response = await _apiService.put(
        ApiConfig.profileEndpoint,
        data: updateData,
      );

      if (response.data['success'] == true) {
        final userData = response.data['user'];
        final updatedUser = User.fromJson(userData);
        _setCurrentUser(updatedUser);
        return true;
      } else {
        _setError(response.data['message'] ?? 'Profile update failed');
        return false;
      }
    } catch (e) {
      _setError('Network error. Please try again.');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Request password reset
  Future<bool> requestPasswordReset(String email) async {
    _setLoading(true);
    _setError(null);

    try {
      final response = await _apiService.post(
        '/auth/forgot-password/',
        data: {'email': email},
      );

      if (response.data['success'] == true) {
        return true;
      } else {
        _setError(response.data['message'] ?? 'Password reset request failed');
        return false;
      }
    } catch (e) {
      _setError('Network error. Please try again.');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// Store authentication token securely
  Future<void> _storeToken(String token) async {
    _currentAccessToken = token;
    try {
      // Store token for ApiService to use
      final storage = FlutterSecureStorage();
      await storage.write(key: 'access_token', value: token);
    } catch (e) {
      debugPrint('Token storage error: $e');
    }
  }

  /// Store refresh token securely
  Future<void> _storeRefreshToken(String refreshToken) async {
    _currentRefreshToken = refreshToken;
    try {
      final storage = FlutterSecureStorage();
      await storage.write(key: 'refresh_token', value: refreshToken);
    } catch (e) {
      debugPrint('Refresh token storage error: $e');
    }
  }

  // Add token storage variables
  String? _currentAccessToken;
  String? _currentRefreshToken;

  /// Get user profile from API
  Future<User?> _getUserProfile() async {
    try {
      final response = await _apiService.get(ApiConfig.profileEndpoint);
      if (response.statusCode == 200) {
        return User.fromJson(response.data);
      }
      return null;
    } catch (e) {
      debugPrint('Error getting user profile: $e');
      return null;
    }
  }

  /// Clear stored authentication token
  Future<void> _clearStoredToken() async {
    _currentAccessToken = null;
    _currentRefreshToken = null;
    try {
      final storage = FlutterSecureStorage();
      await storage.delete(key: 'access_token');
      await storage.delete(key: 'refresh_token');
    } catch (e) {
      debugPrint('Token clearing error: $e');
    }
  }

  /// Set current user and notify listeners
  void _setCurrentUser(User? user) {
    _currentUser = user;
    notifyListeners();
  }

  /// Set loading state and notify listeners
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  /// Set error message and notify listeners
  void _setError(String? error) {
    _error = error;
    notifyListeners();
  }

  /// Clear error message
  void clearError() {
    _setError(null);
  }

  /// Get current user
  User? getCurrentUser() {
    return _currentUser;
  }

  /// Get user display name
  String getUserDisplayName() {
    return _currentUser?.name ?? 'User';
  }

  /// Check if user has VIP membership
  bool hasVipMembership() {
    return _currentUser?.vipMembership != null;
  }

  /// Get user tier level
  String getUserTier() {
    return _currentUser?.tierLevel ?? 'regular';
  }

  /// Check if user is VIP Premium
  bool isVipPremium() {
    final tier = getUserTier().toLowerCase();
    return tier == 'vip_premium' || tier == 'black_tier';
  }
}
