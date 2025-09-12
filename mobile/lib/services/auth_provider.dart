import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../models/auth_models.dart';
import '../models/mfa_models.dart';
import 'api_service.dart';
import 'user_service.dart';
import '../config/api_config.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthProvider extends ChangeNotifier {
  static const _storage = FlutterSecureStorage();
  User? _user;
  bool _isLoading = false;
  String? _error;
  bool _isInitialized = false;

  User? get user => _user;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isLoggedIn => _user != null;
  bool get isInitialized => _isInitialized;

  // User type getters
  bool get isClient => _user?.isClient ?? false;
  bool get isDriver => _user?.isDriver ?? false;
  bool get isRegularClient => _user?.isRegularClient ?? false;
  bool get isVipClient => _user?.isVipClient ?? false;
  bool get isBlackTierClient => _user?.isBlackTierClient ?? false;
  bool get isIndependentDriver => _user?.isIndependentDriver ?? false;
  bool get isFleetOwner => _user?.isFleetOwner ?? false;
  bool get isFleetDriver => _user?.isFleetDriver ?? false;
  bool get isLeasedDriver => _user?.isLeasedDriver ?? false;

  final ApiService _apiService = ApiService();
  final UserService _userService = UserService();

  AuthProvider() {
    _initialize();
  }

  Future<void> _initialize() async {
    _setLoading(true);
    try {
      // Check if user is already logged in
      final storedUser = await _apiService.getStoredUser();
      if (storedUser != null) {
        _user = storedUser;
        // Verify token validity by fetching fresh profile
        try {
          final freshProfile = await _apiService.getProfile();
          _user = freshProfile;
        } catch (e) {
          // Token might be expired, clear stored data
          await _apiService.logout();
          _user = null;
        }
      }
    } catch (e) {
      _setError('Failed to initialize authentication: $e');
    } finally {
      _isInitialized = true;
      _setLoading(false);
    }
  }

  Future<LoginResult> login(String email, String password) async {
    _setLoading(true);
    _clearError();

    try {
      final loginRequest = LoginRequest(
        email: email.trim(),
        password: password,
      );

      final loginResponse = await _apiService.login(loginRequest);

      // Save tokens to secure storage for interceptor
      if (loginResponse.tokens != null) {
        await _storage.write(
          key: 'access_token',
          value: loginResponse.tokens!.accessToken,
        );
        await _storage.write(
          key: 'refresh_token',
          value: loginResponse.tokens!.refreshToken,
        );
      }

      // Check if MFA is required
      if (loginResponse.mfaRequirement != null) {
        return LoginResult.mfaRequired(loginResponse.mfaRequirement!);
      }

      // Normal login success - set user and perform post-login tasks
      _user = loginResponse.user;

      // Register device as trusted for admin tracking (non-blocking)
      _userService
          .registerTrustedDevice()
          .then((success) {
            if (success) {
              print('Device registered as trusted');
            }
          })
          .catchError((error) {
            print('Device registration failed: $error');
          });

      // Refresh user profile with latest tier status
      try {
        final freshProfile = await _userService.getCurrentUser();
        if (freshProfile != null) {
          _user = freshProfile;
        }
      } catch (e) {
        print('Failed to refresh user profile: $e');
      }

      // Check if user needs to set up MFA (for VIP/Premium users)
      final needsSetup = await needsMfaSetup();
      if (needsSetup) {
        notifyListeners();
        return LoginResult.mfaSetupRequired();
      }

      notifyListeners();
      return LoginResult.success();
    } catch (e) {
      _setError(e.toString());
      return LoginResult.error(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<LoginResult> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String? phoneNumber,
    required String userType,
    required String tier,
    String? driverType,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final registerRequest = RegisterRequest(
        email: email.trim(),
        password: password,
        firstName: firstName.trim(),
        lastName: lastName.trim(),
        phoneNumber: phoneNumber?.trim(),
        userType: userType,
        tier: tier,
        driverType: driverType,
      );

      await _apiService.register(registerRequest);

      // After successful registration, automatically login
      final loginResult = await login(email, password);
      return loginResult; // Return the full LoginResult to handle MFA
    } catch (e) {
      _setError(e.toString());
      return LoginResult.error(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  // MFA Methods
  Future<LoginResult> verifyMfa(
    String tempToken,
    String mfaCode,
    String mfaMethod,
  ) async {
    _setLoading(true);
    _clearError();

    try {
      final request = MfaVerificationRequest(
        tempToken: tempToken,
        mfaCode: mfaCode,
        mfaMethod: mfaMethod,
      );

      final loginResponse = await _apiService.verifyMfa(request);
      _user = loginResponse.user;

      // After successful MFA verification, check if user needs to set up MFA
      final needsSetup = await needsMfaSetup();
      if (needsSetup) {
        notifyListeners();
        return LoginResult.mfaSetupRequired();
      }

      notifyListeners();
      return LoginResult.success();
    } catch (e) {
      _setError(e.toString());
      return LoginResult.error(e.toString());
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> sendMfaSms(String tempToken) async {
    try {
      return await _apiService.sendMfaSms(tempToken);
    } catch (e) {
      _setError(e.toString());
      return false;
    }
  }

  Future<bool> sendMfaEmail(String tempToken) async {
    try {
      return await _apiService.sendMfaEmail(tempToken);
    } catch (e) {
      _setError(e.toString());
      return false;
    }
  }

  Future<MfaSetupResponse?> setupMfaTotp() async {
    try {
      return await _apiService.setupMfaTotp();
    } catch (e) {
      _setError(e.toString());
      return null;
    }
  }

  Future<bool> enableMfaTotp(String totpCode) async {
    try {
      return await _apiService.enableMfaTotp(totpCode);
    } catch (e) {
      _setError(e.toString());
      return false;
    }
  }

  // Check MFA status and return whether setup is required
  Future<bool> needsMfaSetup() async {
    try {
      final mfaStatus = await _apiService.getMfaStatus();
      return mfaStatus['needs_setup'] == true;
    } catch (e) {
      _setError(e.toString());
      return false;
    }
  }

  // Complete MFA setup after user finishes setup process
  Future<bool> completeMfaSetup() async {
    try {
      final result = await _apiService.completeMfaSetup();
      return result['success'] == true;
    } catch (e) {
      _setError(e.toString());
      return false;
    }
  }

  Future<void> logout() async {
    _setLoading(true);
    try {
      await _apiService.logout();
    } catch (e) {
      // Continue with logout even if API call fails
      debugPrint('Logout API call failed: $e');
    } finally {
      _user = null;
      _clearError();
      _setLoading(false);
      notifyListeners();
    }
  }

  Future<bool> refreshProfile() async {
    if (!isLoggedIn) return false;

    try {
      final updatedUser = await _apiService.getProfile();
      _user = updatedUser;
      notifyListeners();
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    }
  }

  Future<bool> updateProfile(Map<String, dynamic> data) async {
    if (!isLoggedIn) return false;

    _setLoading(true);
    _clearError();

    try {
      final updatedUser = await _apiService.updateProfile(data);
      _user = updatedUser;
      notifyListeners();
      return true;
    } catch (e) {
      _setError(e.toString());
      return false;
    } finally {
      _setLoading(false);
    }
  }

  String? getUserTierDisplayName() {
    if (_user == null) return null;

    switch (_user!.tier) {
      case AppConstants.tierRegular:
        return 'Regular';
      case AppConstants.tierVip:
        return 'VIP';
      case AppConstants.tierBlackTier:
        return 'Black Tier';
      default:
        return _user!.tier;
    }
  }

  String? getDriverTypeDisplayName() {
    if (_user == null || !_user!.isDriver) return null;

    switch (_user!.driverType) {
      case AppConstants.driverTypeIndependent:
        return 'Independent Driver';
      case AppConstants.driverTypeFleetOwner:
        return 'Fleet Owner';
      case AppConstants.driverTypeFleetDriver:
        return 'Fleet Driver';
      case AppConstants.driverTypeLeased:
        return 'Leased Driver';
      default:
        return _user!.driverType;
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    notifyListeners();
  }

  void clearError() => _clearError();

  /// Refresh user profile data
  Future<void> refreshUserProfile() async {
    if (_user == null) return;

    try {
      // Use new tier status endpoint for comprehensive refresh
      final tierStatus = await _userService.refreshTierStatus();
      if (tierStatus != null) {
        final userData = tierStatus['user'];
        final tierInfo = tierStatus['tier_info'];

        // Update user with latest tier information
        _user = User.fromJson({
          ...userData,
          'tier_info': tierInfo,
          'premium_cards': tierStatus['premium_cards'],
          'device': tierStatus['device'],
          'requirements': tierStatus['requirements'],
        });

        notifyListeners();
        print('✅ User tier refreshed: ${_user?.tier}');
      } else {
        // Fallback to old method
        final freshProfile = await _apiService.getProfile();
        _user = freshProfile;
        notifyListeners();
      }
    } catch (e) {
      // Handle silently or show error as needed
      debugPrint('Failed to refresh user profile: $e');
    }
  }

  /// Force refresh user tier - call after card activation
  Future<bool> refreshUserTier() async {
    if (_user == null) return false;

    try {
      _setLoading(true);
      await refreshUserProfile();
      return true;
    } catch (e) {
      _setError('Failed to refresh user tier: $e');
      return false;
    } finally {
      _setLoading(false);
    }
  }
}
