import 'user_model.dart';
import 'mfa_models.dart';

class LoginResult {
  final bool isSuccess;
  final bool requiresMfa;
  final bool requiresMfaSetup;
  final MfaRequirement? mfaRequirement;
  final String? error;

  LoginResult._({
    required this.isSuccess,
    required this.requiresMfa,
    required this.requiresMfaSetup,
    this.mfaRequirement,
    this.error,
  });

  factory LoginResult.success() {
    return LoginResult._(
      isSuccess: true,
      requiresMfa: false,
      requiresMfaSetup: false,
    );
  }

  factory LoginResult.mfaRequired(MfaRequirement mfaRequirement) {
    return LoginResult._(
      isSuccess: false,
      requiresMfa: true,
      requiresMfaSetup: false,
      mfaRequirement: mfaRequirement,
    );
  }

  factory LoginResult.mfaSetupRequired() {
    return LoginResult._(
      isSuccess: true,
      requiresMfa: false,
      requiresMfaSetup: true,
    );
  }

  factory LoginResult.error(String error) {
    return LoginResult._(
      isSuccess: false,
      requiresMfa: false,
      requiresMfaSetup: false,
      error: error,
    );
  }
}

class LoginRequest {
  final String email;
  final String password;

  LoginRequest({required this.email, required this.password});

  Map<String, dynamic> toJson() {
    return {'email': email, 'password': password};
  }
}

class RegisterRequest {
  final String email;
  final String password;
  final String firstName;
  final String lastName;
  final String? phoneNumber;
  final String userType;
  final String tier;
  final String? driverType;

  RegisterRequest({
    required this.email,
    required this.password,
    required this.firstName,
    required this.lastName,
    this.phoneNumber,
    required this.userType,
    required this.tier,
    this.driverType,
  });

  Map<String, dynamic> toJson() {
    final data = {
      'email': email,
      'password': password,
      'password_confirm': password, // Django requires password confirmation
      'first_name': firstName,
      'last_name': lastName,
      'tier': tier, // This should be 'normal', 'premium', or 'vip'
    };

    if (phoneNumber != null && phoneNumber!.isNotEmpty) {
      data['phone_number'] = phoneNumber!;
    }

    if (driverType != null && driverType!.isNotEmpty) {
      data['driver_type'] = driverType!;
    }

    return data;
  }
}

class AuthTokens {
  final String accessToken;
  final String refreshToken;
  final int? expiresIn;

  AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    this.expiresIn,
  });

  factory AuthTokens.fromJson(Map<String, dynamic> json) {
    return AuthTokens(
      accessToken:
          json['access'] ?? json['access_token'] ?? json['accessToken'] ?? '',
      refreshToken:
          json['refresh'] ??
          json['refresh_token'] ??
          json['refreshToken'] ??
          '',
      expiresIn: json['expires_in'] ?? json['expiresIn'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access': accessToken,
      'refresh': refreshToken,
      if (expiresIn != null) 'expires_in': expiresIn,
    };
  }
}

class LoginResponse {
  final User? user;
  final AuthTokens? tokens;
  final MfaRequirement? mfaRequirement;

  LoginResponse({this.user, this.tokens, this.mfaRequirement});

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    // Check if this is an MFA requirement response
    if (json.containsKey('mfa_required') || json.containsKey('mfa_methods')) {
      return LoginResponse(mfaRequirement: MfaRequirement.fromJson(json));
    }

    // Normal login response with tokens
    return LoginResponse(
      user: User.fromJson(json['user'] ?? json),
      tokens: AuthTokens.fromJson(json['tokens'] ?? json),
    );
  }

  Map<String, dynamic> toJson() {
    if (mfaRequirement != null) {
      return {
        'mfa_required': mfaRequirement!.mfaRequired,
        'mfa_methods': mfaRequirement!.mfaMethods,
        if (mfaRequirement!.message != null) 'message': mfaRequirement!.message,
        if (mfaRequirement!.tempToken != null)
          'temp_token': mfaRequirement!.tempToken,
      };
    }

    return {
      if (user != null) 'user': user!.toJson(),
      if (tokens != null) 'tokens': tokens!.toJson(),
    };
  }
}
