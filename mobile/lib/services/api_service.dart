import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';
import '../models/user_model.dart';
import '../models/auth_models.dart';
import '../models/mfa_models.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  late final Dio _dio;
  static const _storage = FlutterSecureStorage();

  void initialize() {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConfig.baseUrl,
        connectTimeout: const Duration(
          milliseconds: ApiConfig.connectionTimeout,
        ),
        receiveTimeout: const Duration(milliseconds: ApiConfig.receiveTimeout),
        sendTimeout: const Duration(milliseconds: ApiConfig.sendTimeout),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add interceptors
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.read(key: 'access_token');
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) {
          if (kDebugMode) {
            print('API Error: ${error.message}');
          }
          handler.next(error);
        },
      ),
    );

    _dio.interceptors.add(
      LogInterceptor(
        requestBody: kDebugMode,
        responseBody: kDebugMode,
        error: kDebugMode,
      ),
    );
  }

  // Authentication methods
  Future<LoginResponse> login(LoginRequest request) async {
    try {
      final response = await _dio.post(
        '/api/v1/accounts/login/',
        data: request.toJson(),
      );
      return LoginResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> register(RegisterRequest request) async {
    try {
      await _dio.post('/api/v1/accounts/register/', data: request.toJson());
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<LoginResponse> verifyMfa(MfaVerificationRequest request) async {
    try {
      final response = await _dio.post(
        '/api/v1/accounts/auth/mfa/verify/',
        data: request.toJson(),
      );
      return LoginResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> logout() async {
    try {
      await _storage.delete(key: 'access_token');
      await _storage.delete(key: 'refresh_token');
      await _storage.delete(key: 'user_data');
    } catch (e) {
      // Continue with logout even if storage clearing fails
      if (kDebugMode) {
        print('Error clearing storage during logout: $e');
      }
    }
  }

  Future<User?> getStoredUser() async {
    try {
      final userData = await _storage.read(key: 'user_data');
      if (userData != null) {
        final json = jsonDecode(userData);
        return User.fromJson(json);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<User> getProfile() async {
    try {
      final response = await _dio.get('/api/v1/accounts/profile/');
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // MFA Methods
  Future<Map<String, dynamic>> getMfaStatus() async {
    try {
      final response = await _dio.get('/api/v1/accounts/auth/mfa/status/');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> setupMfa(
    String method, {
    String? phoneNumber,
    String? email,
  }) async {
    try {
      final data = <String, dynamic>{'method': method};

      if (phoneNumber != null) {
        data['phone_number'] = phoneNumber;
      }
      if (email != null) {
        data['email_address'] = email;
      }

      final response = await _dio.post(
        '/api/v1/accounts/auth/mfa/setup/',
        data: data,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> confirmMfa({
    required String method,
    required String code,
    String? qrSecret,
  }) async {
    try {
      final data = <String, dynamic>{'method': method, 'code': code};

      if (qrSecret != null) {
        data['qr_secret'] = qrSecret;
      }

      final response = await _dio.post(
        '/api/v1/accounts/auth/mfa/confirm/',
        data: data,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> completeMfaSetup() async {
    try {
      final response = await _dio.post('/api/v1/accounts/auth/mfa/confirm/');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<bool> sendMfaSms(String tempToken) async {
    try {
      final response = await _dio.post(
        '/api/v1/accounts/auth/mfa/setup/',
        data: {'temp_token': tempToken},
      );
      return response.statusCode == 200;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<bool> sendMfaEmail(String tempToken) async {
    try {
      final response = await _dio.post(
        '/api/v1/accounts/auth/mfa/setup/',
        data: {'temp_token': tempToken},
      );
      return response.statusCode == 200;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<MfaSetupResponse?> setupMfaTotp() async {
    try {
      final response = await _dio.post('/api/v1/accounts/auth/mfa/setup/');
      return MfaSetupResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<bool> enableMfaTotp(String totpCode) async {
    try {
      final response = await _dio.post(
        '/api/v1/accounts/auth/mfa/confirm/',
        data: {'totp_code': totpCode},
      );
      return response.statusCode == 200;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<User> updateProfile(Map<String, dynamic> data) async {
    try {
      final response = await _dio.patch(
        '/api/v1/accounts/profile/',
        data: data,
      );
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Basic HTTP methods
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.get(path, queryParameters: queryParameters);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.put(path, data: data, queryParameters: queryParameters);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response> delete(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.delete(path, queryParameters: queryParameters);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // VIP Card activation
  Future<Map<String, dynamic>> activateVipCard({
    required String cardNumber,
    required String pinCode,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/accounts/premium-cards/activate/',
        data: {'card_number': cardNumber, 'pin_code': pinCode},
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Error handling
  String _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'Connection timeout. Please check your internet connection.';
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode;
        final data = e.response?.data;

        if (statusCode == 400 && data is Map && data.containsKey('detail')) {
          return data['detail'].toString();
        } else if (statusCode == 401) {
          return 'Authentication failed. Please login again.';
        } else if (statusCode == 403) {
          return 'Access denied.';
        } else if (statusCode == 404) {
          return 'Resource not found.';
        } else if (statusCode == 500) {
          return 'Server error. Please try again later.';
        }
        return 'Request failed with status code: $statusCode';
      case DioExceptionType.cancel:
        return 'Request cancelled.';
      case DioExceptionType.unknown:
        if (e.error is SocketException) {
          return 'No internet connection.';
        }
        return 'An unexpected error occurred.';
      default:
        return 'An error occurred.';
    }
  }
}
