import 'package:flutter/material.dart';

class DigitalCard {
  final String id;
  final String serialNumber;
  final String activationCode;
  final CardTier tier;
  final CardStatus status;
  final DateTime issuedDate;
  final DateTime? activatedDate;
  final DateTime? expiryDate;
  final String? activatedBy; // User ID who activated the card
  final Map<String, dynamic> cardFeatures;
  final CardDesign design;

  DigitalCard({
    required this.id,
    required this.serialNumber,
    required this.activationCode,
    required this.tier,
    required this.status,
    required this.issuedDate,
    this.activatedDate,
    this.expiryDate,
    this.activatedBy,
    required this.cardFeatures,
    required this.design,
  });

  factory DigitalCard.fromJson(Map<String, dynamic> json) {
    return DigitalCard(
      id: json['id'] ?? '',
      serialNumber: json['serial_number'] ?? '',
      activationCode: json['activation_code'] ?? '',
      tier: CardTier.values.firstWhere(
        (t) => t.name == json['tier'],
        orElse: () => CardTier.vip,
      ),
      status: CardStatus.values.firstWhere(
        (s) => s.name == json['status'],
        orElse: () => CardStatus.inactive,
      ),
      issuedDate: DateTime.parse(
        json['issued_date'] ?? DateTime.now().toIso8601String(),
      ),
      activatedDate: json['activated_date'] != null
          ? DateTime.parse(json['activated_date'])
          : null,
      expiryDate: json['expiry_date'] != null
          ? DateTime.parse(json['expiry_date'])
          : null,
      activatedBy: json['activated_by'],
      cardFeatures: Map<String, dynamic>.from(json['card_features'] ?? {}),
      design: CardDesign.fromJson(json['design'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'serial_number': serialNumber,
      'activation_code': activationCode,
      'tier': tier.name,
      'status': status.name,
      'issued_date': issuedDate.toIso8601String(),
      'activated_date': activatedDate?.toIso8601String(),
      'expiry_date': expiryDate?.toIso8601String(),
      'activated_by': activatedBy,
      'card_features': cardFeatures,
      'design': design.toJson(),
    };
  }

  bool get isActive => status == CardStatus.active;
  bool get isExpired =>
      expiryDate != null && DateTime.now().isAfter(expiryDate!);
  bool get canBeActivated => status == CardStatus.inactive && !isExpired;

  String get displaySerialNumber {
    // Format: VIP-XXXX-XXXX-XXXX
    final prefix = tier == CardTier.vip ? 'VIP' : 'VIPR';
    final numbers = serialNumber.replaceAll(RegExp(r'[^0-9]'), '');
    if (numbers.length >= 12) {
      return '$prefix-${numbers.substring(0, 4)}-${numbers.substring(4, 8)}-${numbers.substring(8, 12)}';
    }
    return '$prefix-$serialNumber';
  }

  List<String> get tierFeatures {
    switch (tier) {
      case CardTier.vip:
        return [
          'Priority ride matching',
          'Discrete booking mode',
          'Premium vehicle access',
          'VIP driver network',
          'Concierge support',
          'Enhanced SOS',
        ];
      case CardTier.vipPremium:
        return [
          'All VIP features',
          'Hotel partnerships',
          'Encrypted tracking',
          'High-security vehicles',
          'Hotel staff integration',
          'Advanced SOS with GPS',
          'Partnership perks',
          'VIP lounge access',
        ];
    }
  }
}

enum CardTier {
  vip('VIP'),
  vipPremium('VIP Premium');

  const CardTier(this.displayName);
  final String displayName;
}

enum CardStatus {
  inactive('Inactive'),
  active('Active'),
  suspended('Suspended'),
  expired('Expired'),
  revoked('Revoked');

  const CardStatus(this.displayName);
  final String displayName;
}

class CardDesign {
  final String primaryColor;
  final String secondaryColor;
  final String backgroundImage;
  final String hologramPattern;
  final String logoUrl;

  CardDesign({
    required this.primaryColor,
    required this.secondaryColor,
    required this.backgroundImage,
    required this.hologramPattern,
    required this.logoUrl,
  });

  factory CardDesign.fromJson(Map<String, dynamic> json) {
    return CardDesign(
      primaryColor: json['primary_color'] ?? '#FFD700',
      secondaryColor: json['secondary_color'] ?? '#FF8C00',
      backgroundImage: json['background_image'] ?? '',
      hologramPattern: json['hologram_pattern'] ?? 'default',
      logoUrl: json['logo_url'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'primary_color': primaryColor,
      'secondary_color': secondaryColor,
      'background_image': backgroundImage,
      'hologram_pattern': hologramPattern,
      'logo_url': logoUrl,
    };
  }
}

class CardActivationRequest {
  final String serialNumber;
  final String activationCode;
  final String userId;
  final DateTime requestTime;

  CardActivationRequest({
    required this.serialNumber,
    required this.activationCode,
    required this.userId,
    required this.requestTime,
  });

  Map<String, dynamic> toJson() {
    return {
      'serial_number': serialNumber,
      'activation_code': activationCode,
      'user_id': userId,
      'request_time': requestTime.toIso8601String(),
    };
  }
}

class CardActivationResult {
  final bool success;
  final String message;
  final DigitalCard? card;
  final String? newTierLevel;
  final List<String>? unlockedFeatures;
  final String? errorCode;
  final String? newTier;
  final String? tierDisplay;
  final bool requiresMfaSetup;
  final bool shouldRefreshSession;
  final String? redirectTo;

  CardActivationResult({
    required this.success,
    required this.message,
    this.card,
    this.newTierLevel,
    this.unlockedFeatures,
    this.errorCode,
    this.newTier,
    this.tierDisplay,
    this.requiresMfaSetup = false,
    this.shouldRefreshSession = false,
    this.redirectTo,
  });

  factory CardActivationResult.fromJson(Map<String, dynamic> json) {
    return CardActivationResult(
      success: json['success'] ?? false,
      message: json['message'] ?? '',
      card: json['card'] != null ? DigitalCard.fromJson(json['card']) : null,
      newTierLevel: json['new_tier_level'],
      unlockedFeatures: json['unlocked_features'] != null
          ? List<String>.from(json['unlocked_features'])
          : null,
      errorCode: json['error_code'],
      newTier: json['new_tier'],
      tierDisplay: json['tier_display'],
      requiresMfaSetup: json['requires_mfa_setup'] ?? false,
      shouldRefreshSession: json['should_refresh_session'] ?? false,
      redirectTo: json['redirect_to'],
    );
  }
}

class CardValidationError {
  final String field;
  final String message;
  final String code;

  CardValidationError({
    required this.field,
    required this.message,
    required this.code,
  });

  factory CardValidationError.fromJson(Map<String, dynamic> json) {
    return CardValidationError(
      field: json['field'] ?? '',
      message: json['message'] ?? '',
      code: json['code'] ?? '',
    );
  }
}

// Helper class for card utilities
class CardUtils {
  static bool isValidSerialNumber(String serialNumber) {
    // VIP cards: VIP-XXXX-XXXX-XXXX format
    // VIP Premium cards: VIPR-XXXX-XXXX-XXXX format
    final regex = RegExp(r'^(VIP|VIPR)-\d{4}-\d{4}-\d{4}$');
    return regex.hasMatch(serialNumber.toUpperCase());
  }

  static bool isValidActivationCode(String activationCode) {
    // Activation codes: 8-12 character alphanumeric
    final regex = RegExp(r'^[A-Z0-9]{8,12}$');
    return regex.hasMatch(activationCode.toUpperCase());
  }

  static CardTier? getTierFromSerialNumber(String serialNumber) {
    if (serialNumber.toUpperCase().startsWith('VIP-')) {
      return CardTier.vip;
    } else if (serialNumber.toUpperCase().startsWith('VIPR-')) {
      return CardTier.vipPremium;
    }
    return null;
  }

  static String formatSerialNumber(String input) {
    // Remove any existing formatting
    final cleaned = input.replaceAll(RegExp(r'[^A-Z0-9]'), '');

    if (cleaned.length >= 16) {
      final prefix = cleaned.substring(0, 4);
      final numbers = cleaned.substring(4);
      if (numbers.length >= 12) {
        return '$prefix-${numbers.substring(0, 4)}-${numbers.substring(4, 8)}-${numbers.substring(8, 12)}';
      }
    }

    return input;
  }

  static String formatActivationCode(String input) {
    // Convert to uppercase and remove spaces
    return input.toUpperCase().replaceAll(' ', '');
  }

  static Color getTierColor(CardTier tier) {
    switch (tier) {
      case CardTier.vip:
        return const Color(0xFFFFD700); // Gold
      case CardTier.vipPremium:
        return const Color(0xFF9932CC); // Dark Orchid
    }
  }

  static Color getTierSecondaryColor(CardTier tier) {
    switch (tier) {
      case CardTier.vip:
        return const Color(0xFFFF8C00); // Dark Orange
      case CardTier.vipPremium:
        return const Color(0xFF4B0082); // Indigo
    }
  }
}
