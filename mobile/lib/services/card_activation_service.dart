import 'dart:async';
import '../models/card_models.dart';
import 'api_service.dart';

class CardActivationService {
  static final CardActivationService _instance =
      CardActivationService._internal();
  factory CardActivationService() => _instance;
  CardActivationService._internal();

  final ApiService _apiService = ApiService();

  /// Activate a digital card using the new Flutter endpoint
  Future<CardActivationResult> activateCard({
    required String serialNumber,
    required String activationCode,
    required String userId,
  }) async {
    try {
      // Validate input format
      final validationErrors = _validateCardInputs(
        serialNumber,
        activationCode,
      );
      if (validationErrors.isNotEmpty) {
        return CardActivationResult(
          success: false,
          message: validationErrors.first.message,
          errorCode: validationErrors.first.code,
        );
      }

      // Use new Flutter activation endpoint
      final response = await _apiService.post(
        '/api/v1/accounts/flutter/activate-card/',
        data: {
          'card_number': serialNumber.replaceAll('-', '').replaceAll(' ', ''),
          'verification_code': activationCode,
          'device_name': 'Flutter Mobile App',
        },
      );

      if (response.statusCode == 200 && response.data['success'] == true) {
        final responseData = response.data;

        final result = CardActivationResult(
          success: true,
          message: responseData['message'] ?? 'Card activated successfully!',
          card: responseData['card'] != null
              ? DigitalCard.fromJson(responseData['card'])
              : null,
          newTier: responseData['user']['tier'],
          tierDisplay: responseData['user']['tier_display'],
          requiresMfaSetup:
              responseData['next_steps']['requires_mfa_setup'] ?? false,
          shouldRefreshSession:
              responseData['next_steps']['should_refresh_session'] ?? false,
          redirectTo: responseData['next_steps']['redirect_to'],
        );

        return result;
      } else {
        return CardActivationResult(
          success: false,
          message: response.data['error'] ?? 'Card activation failed',
          errorCode: 'ACTIVATION_FAILED',
        );
      }
    } catch (e) {
      return CardActivationResult(
        success: false,
        message: 'Network error during activation: $e',
        errorCode: 'NETWORK_ERROR',
      );
    }
  }

  /// Check current tier status using Flutter endpoint
  Future<Map<String, dynamic>?> getTierStatus() async {
    try {
      final response = await _apiService.get(
        '/api/v1/accounts/flutter/tier-status/',
      );
      if (response.statusCode == 200) {
        return response.data;
      }
    } catch (e) {
      print('Failed to get tier status: $e');
    }
    return null;
  }

  /// Get all cards associated with a user
  Future<List<DigitalCard>> getUserCards(String userId) async {
    try {
      final response = await _apiService.get(
        '/api/accounts/cards/user/$userId/',
      );
      final cardsList = response.data['cards'] as List;
      return cardsList.map((card) => DigitalCard.fromJson(card)).toList();
    } catch (e) {
      throw Exception('Failed to load user cards: $e');
    }
  }

  /// Get card details by serial number (for preview before activation)
  Future<DigitalCard?> getCardDetails(String serialNumber) async {
    try {
      final formattedSerial = CardUtils.formatSerialNumber(serialNumber);
      final response = await _apiService.get(
        '/api/accounts/cards/details/$formattedSerial/',
      );

      if (response.data['found'] == true) {
        return DigitalCard.fromJson(response.data['card']);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  /// Validate card activation inputs
  List<CardValidationError> _validateCardInputs(
    String serialNumber,
    String activationCode,
  ) {
    List<CardValidationError> errors = [];

    // Validate serial number format
    if (!CardUtils.isValidSerialNumber(serialNumber)) {
      errors.add(
        CardValidationError(
          field: 'serial_number',
          message:
              'Invalid serial number format. Use VIP-XXXX-XXXX-XXXX or VIPR-XXXX-XXXX-XXXX',
          code: 'INVALID_SERIAL_FORMAT',
        ),
      );
    }

    // Validate activation code format
    if (!CardUtils.isValidActivationCode(activationCode)) {
      errors.add(
        CardValidationError(
          field: 'activation_code',
          message:
              'Invalid activation code. Must be 8-12 alphanumeric characters',
          code: 'INVALID_ACTIVATION_CODE',
        ),
      );
    }

    return errors;
  }

  /// Check if a card can be activated
  Future<bool> canActivateCard(String serialNumber) async {
    try {
      final card = await getCardDetails(serialNumber);
      return card?.canBeActivated ?? false;
    } catch (e) {
      return false;
    }
  }

  /// Deactivate a card (for security purposes)
  Future<bool> deactivateCard(String cardId, String reason) async {
    try {
      final response = await _apiService.post(
        '/api/accounts/cards/$cardId/deactivate/',
        data: {'reason': reason},
      );
      return response.data['success'] ?? false;
    } catch (e) {
      return false;
    }
  }

  /// Get user's current tier level
  Future<String> getUserTierLevel(String userId) async {
    try {
      final response = await _apiService.get(
        '/api/accounts/users/$userId/tier/',
      );
      return response.data['tier_level'] ?? 'regular';
    } catch (e) {
      return 'regular';
    }
  }

  /// Update user tier after successful card activation
  Future<bool> updateUserTier(String userId, String newTier) async {
    try {
      final response = await _apiService.post(
        '/api/accounts/users/$userId/update-tier/',
        data: {'tier_level': newTier},
      );
      return response.data['success'] ?? false;
    } catch (e) {
      return false;
    }
  }

  /// Get tier upgrade benefits
  Map<String, List<String>> getTierBenefits() {
    return {
      'vip': [
        'Priority ride matching with top-rated drivers',
        'Discrete booking mode for privacy',
        'Access to premium vehicle fleet',
        'VIP-exclusive driver network',
        '24/7 concierge support',
        'Enhanced SOS emergency system',
        'Priority customer support',
        'Exclusive ride discounts',
      ],
      'vip_premium': [
        'All VIP tier benefits included',
        'Exclusive hotel partnership access',
        'Encrypted GPS tracking for security',
        'High-security armored vehicles',
        'Direct hotel staff integration',
        'Advanced SOS with live GPS feed',
        'VIP lounge access at partner hotels',
        'Complimentary hotel upgrades',
        'Priority airport transfers',
        'Personal concierge at partner properties',
      ],
    };
  }

  /// Mock card generation for development (remove in production)
  DigitalCard generateMockCard(CardTier tier) {
    final now = DateTime.now();
    final serialPrefix = tier == CardTier.vip ? 'VIP' : 'VIPR';
    final serialNumbers = List.generate(
      3,
      (i) => (1000 + (now.millisecond + i) % 9000).toString(),
    );

    return DigitalCard(
      id: 'mock_${now.millisecondsSinceEpoch}',
      serialNumber:
          '$serialPrefix-${serialNumbers[0]}-${serialNumbers[1]}-${serialNumbers[2]}',
      activationCode: 'MOCK${now.millisecond.toString().padLeft(4, '0')}AB',
      tier: tier,
      status: CardStatus.inactive,
      issuedDate: now,
      cardFeatures: {},
      design: CardDesign(
        primaryColor: CardUtils.getTierColor(tier).value.toRadixString(16),
        secondaryColor: CardUtils.getTierSecondaryColor(
          tier,
        ).value.toRadixString(16),
        backgroundImage: '',
        hologramPattern: 'diamond',
        logoUrl: '',
      ),
    );
  }
}
