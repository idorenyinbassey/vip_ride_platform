// Premium Digital Card Service with Payment Processing
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';
import '../models/premium_card_models.dart';

class PremiumCardService {
  final Dio _dio = Dio();
  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  PremiumCardService() {
    _dio.options.baseUrl = '${ApiConfig.baseUrl}/api/v1/accounts';
    _dio.options.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    // Add authentication interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _getAuthToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
      ),
    );
  }

  Future<String?> _getAuthToken() async {
    final token = await _storage.read(key: 'access_token');
    debugPrint(
      'Auth token retrieved: ${token != null ? 'Token found (${token.length} chars)' : 'No token found'}',
    );
    return token;
  }

  /// Create Stripe Payment Intent for secure payment processing
  Future<Map<String, dynamic>> createPaymentIntent({
    required String tier,
  }) async {
    try {
      final response = await _dio.post(
        '/premium-cards/payment-intent/',
        data: {'tier': tier},
      );
      if (response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception('Failed to create payment intent');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to create payment intent: $e');
    }
  }

  /// Unified purchase method for Premium/VIP (Black-Tier) Digital Card
  /// Supports Stripe, Google Pay, Flutterwave, and Paystack
  Future<PremiumDigitalCard> purchasePremiumCard({
    required String tier,
    required String paymentMethod,
    String? paymentToken,
    String? paymentIntentId,
  }) async {
    try {
      debugPrint('PremiumCardService.purchasePremiumCard called with:');
      debugPrint('  - tier: $tier');
      debugPrint('  - paymentMethod: $paymentMethod');
      debugPrint('  - paymentToken: $paymentToken');
      debugPrint('  - paymentIntentId: $paymentIntentId');

      if (paymentMethod == 'stripe') {
        if (paymentIntentId == null || paymentToken == null) {
          final missingParams = <String>[];
          if (paymentIntentId == null) missingParams.add('paymentIntentId');
          if (paymentToken == null) missingParams.add('paymentToken');
          throw Exception(
            'Stripe payment requires both paymentIntentId and paymentToken. Missing: ${missingParams.join(', ')}',
          );
        }
        debugPrint('Calling purchasePremiumCardWithStripe...');
        return await purchasePremiumCardWithStripe(
          tier: tier,
          paymentIntentId: paymentIntentId,
          paymentMethodId: paymentToken,
        );
      } else if (paymentMethod == 'google_pay') {
        if (paymentToken == null) {
          throw Exception('Google Pay requires paymentToken');
        }
        debugPrint('Calling purchasePremiumCardWithGooglePay...');
        return await purchasePremiumCardWithGooglePay(
          tier: tier,
          paymentToken: paymentToken,
        );
      } else if (paymentMethod == 'paystack') {
        if (paymentToken == null) {
          throw Exception('Paystack requires paymentToken');
        }
        debugPrint('Calling purchasePremiumCardWithPaystack...');
        return await purchasePremiumCardWithPaystack(
          tier: tier,
          paymentToken: paymentToken,
        );
      } else if (paymentMethod == 'flutterwave') {
        if (paymentToken == null) {
          throw Exception('Flutterwave requires paymentToken');
        }
        debugPrint('Calling purchasePremiumCardWithFlutterwave...');
        return await purchasePremiumCardWithFlutterwave(
          tier: tier,
          paymentToken: paymentToken,
        );
      } else {
        throw Exception('Unsupported payment method: $paymentMethod');
      }
    } on DioException catch (e) {
      debugPrint(
        'DioException caught: ${e.response?.statusCode} - ${e.message}',
      );
      debugPrint('Response data: ${e.response?.data}');

      if (e.response?.statusCode == 401) {
        throw Exception('Authentication failed. Please login again.');
      } else if (e.response?.data != null &&
          e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      } else if (e.response?.data != null &&
          e.response!.data['detail'] != null) {
        throw Exception(e.response!.data['detail']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      debugPrint('General exception: $e');
      throw Exception('Failed to purchase premium card: $e');
    }
  }

  /// Purchase Premium Digital Card with Stripe payment
  Future<PremiumDigitalCard> purchasePremiumCardWithStripe({
    required String tier,
    required String paymentIntentId,
    required String paymentMethodId,
  }) async {
    try {
      debugPrint('purchasePremiumCardWithStripe called with:');
      debugPrint('  - tier: $tier');
      debugPrint('  - paymentIntentId: $paymentIntentId');
      debugPrint('  - paymentMethodId: $paymentMethodId');

      final response = await _dio.post(
        '/premium-cards/purchase/',
        data: {
          'tier': tier,
          'payment_method': 'stripe',
          'payment_intent_id': paymentIntentId,
          'payment_token': paymentMethodId,
        },
      );

      debugPrint('Stripe purchase response status: ${response.statusCode}');
      debugPrint('Stripe purchase response data: ${response.data}');

      if (response.statusCode == 201) {
        return PremiumDigitalCard.fromJson(response.data['card']);
      } else {
        throw Exception(
          'Failed to purchase premium card with Stripe. Status: ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      debugPrint('DioException in purchasePremiumCardWithStripe: $e');
      debugPrint('Response data: ${e.response?.data}');
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to purchase premium card with Stripe: $e');
    }
  }

  /// Purchase Premium Digital Card with Google Pay
  Future<PremiumDigitalCard> purchasePremiumCardWithGooglePay({
    required String tier,
    required String paymentToken,
  }) async {
    try {
      final response = await _dio.post(
        '/premium-cards/purchase/',
        data: {
          'tier': tier,
          'payment_method': 'google_pay',
          'payment_token': paymentToken,
        },
      );
      if (response.statusCode == 201) {
        return PremiumDigitalCard.fromJson(response.data['card']);
      } else {
        throw Exception('Failed to purchase premium card with Google Pay');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to purchase premium card with Google Pay: $e');
    }
  }

  /// Purchase Premium Digital Card with Flutterwave payment
  Future<PremiumDigitalCard> purchasePremiumCardWithFlutterwave({
    required String tier,
    required String paymentToken,
  }) async {
    try {
      final response = await _dio.post(
        '/premium-cards/purchase/',
        data: {
          'tier': tier,
          'payment_method': 'flutterwave',
          'payment_token': paymentToken,
        },
      );
      if (response.statusCode == 201) {
        return PremiumDigitalCard.fromJson(response.data['card']);
      } else {
        throw Exception('Failed to purchase premium card with Flutterwave');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to purchase premium card with Flutterwave: $e');
    }
  }

  /// Purchase Premium Digital Card with Paystack payment
  Future<PremiumDigitalCard> purchasePremiumCardWithPaystack({
    required String tier,
    required String paymentToken,
  }) async {
    try {
      final response = await _dio.post(
        '/premium-cards/purchase/',
        data: {
          'tier': tier,
          'payment_method': 'paystack',
          'payment_token': paymentToken,
        },
      );
      if (response.statusCode == 201) {
        return PremiumDigitalCard.fromJson(response.data['card']);
      } else {
        throw Exception('Failed to purchase premium card with Paystack');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to purchase premium card with Paystack: $e');
    }
  }

  /// Activate Premium Digital Card with verification code
  Future<PremiumDigitalCard> activatePremiumCard({
    required String verificationCode,
  }) async {
    try {
      final response = await _dio.post(
        '/premium-cards/activate/',
        data: {'verification_code': verificationCode},
      );
      if (response.statusCode == 200) {
        return PremiumDigitalCard.fromJson(response.data['card']);
      } else {
        throw Exception('Failed to activate premium card');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to activate premium card: $e');
    }
  }

  /// Get list of user's premium cards
  Future<List<PremiumDigitalCard>> getPremiumCards() async {
    try {
      final response = await _dio.get('/premium-cards/');
      if (response.statusCode == 200) {
        final List<dynamic> cardsJson = response.data['cards'];
        return cardsJson
            .map((cardJson) => PremiumDigitalCard.fromJson(cardJson))
            .toList();
      } else {
        throw Exception('Failed to fetch premium cards');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to fetch premium cards: $e');
    }
  }

  /// Get active premium card for user
  Future<PremiumDigitalCard?> getActiveCard() async {
    try {
      final response = await _dio.get('/premium-cards/active/');
      if (response.statusCode == 200 && response.data['card'] != null) {
        return PremiumDigitalCard.fromJson(response.data['card']);
      } else {
        return null; // No active card
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return null; // No active card found
      }
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to fetch active card: $e');
    }
  }

  /// Get user's premium status
  Future<PremiumStatus> getPremiumStatus() async {
    try {
      final response = await _dio.get('/premium-status/');
      if (response.statusCode == 200) {
        return PremiumStatus.fromJson(response.data);
      } else {
        throw Exception('Failed to fetch premium status');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to fetch premium status: $e');
    }
  }

  /// Verify payment status
  Future<Map<String, dynamic>> verifyPaymentStatus({
    required String transactionId,
    required String paymentMethod,
  }) async {
    try {
      final response = await _dio.post(
        '/premium-cards/verify-payment/',
        data: {
          'transaction_id': transactionId,
          'payment_method': paymentMethod,
        },
      );
      if (response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception('Failed to verify payment status');
      }
    } on DioException catch (e) {
      if (e.response?.data != null && e.response!.data['error'] != null) {
        throw Exception(e.response!.data['error']);
      }
      throw Exception('Network error: ${e.message}');
    } catch (e) {
      throw Exception('Failed to verify payment status: $e');
    }
  }
}
