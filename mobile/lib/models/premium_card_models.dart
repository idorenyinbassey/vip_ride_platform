// Premium Digital Card Models
class PremiumDigitalCard {
  final String id;
  final String cardNumber;
  final String? verificationCode; // Only shown for sold but unactivated cards
  final String tier; // 'premium' or 'vip'
  final String status; // 'available', 'sold', 'active', 'expired', 'suspended'
  final double price;
  final int validityMonths;
  final DateTime? purchasedAt;
  final DateTime? activatedAt;
  final DateTime? expiresAt;
  final int? daysUntilExpiry;
  final bool isActive;

  PremiumDigitalCard({
    required this.id,
    required this.cardNumber,
    this.verificationCode,
    required this.tier,
    required this.status,
    required this.price,
    required this.validityMonths,
    this.purchasedAt,
    this.activatedAt,
    this.expiresAt,
    this.daysUntilExpiry,
    required this.isActive,
  });

  factory PremiumDigitalCard.fromJson(Map<String, dynamic> json) {
    return PremiumDigitalCard(
      id: json['id'] ?? '',
      cardNumber: json['card_number'] ?? '',
      verificationCode: json['verification_code'],
      tier: json['tier'] ?? 'premium', // Default to premium if not specified
      status: json['status'] ?? 'available',
      price: double.parse((json['price'] ?? 0).toString()),
      validityMonths: json['validity_months'] ?? 12,
      purchasedAt: json['purchased_at'] != null
          ? DateTime.parse(json['purchased_at'])
          : null,
      activatedAt: json['activated_at'] != null
          ? DateTime.parse(json['activated_at'])
          : null,
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'])
          : null,
      daysUntilExpiry: json['days_until_expiry'],
      isActive: json['is_active'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'card_number': cardNumber,
      'verification_code': verificationCode,
      'tier': tier,
      'status': status,
      'price': price,
      'validity_months': validityMonths,
      'purchased_at': purchasedAt?.toIso8601String(),
      'activated_at': activatedAt?.toIso8601String(),
      'expires_at': expiresAt?.toIso8601String(),
      'days_until_expiry': daysUntilExpiry,
      'is_active': isActive,
    };
  }

  // Getters for status checks
  bool get isPending => status == 'sold';
  bool get isExpired => status == 'expired';
  bool get isSuspended => status == 'suspended';

  // Display helpers
  String get maskedCardNumber {
    if (cardNumber.length >= 4) {
      return '**** **** **** ${cardNumber.substring(cardNumber.length - 4)}';
    }
    return cardNumber;
  }

  String get tierDisplayName {
    switch (tier) {
      case 'premium':
        return 'Premium';
      case 'vip':
        return 'VIP';
      default:
        return tier.toUpperCase();
    }
  }

  String get statusDisplayName {
    switch (status) {
      case 'available':
        return 'Available';
      case 'sold':
        return 'Pending Activation';
      case 'active':
        return 'Active';
      case 'expired':
        return 'Expired';
      case 'suspended':
        return 'Suspended';
      default:
        return status.toUpperCase();
    }
  }
}

class PremiumCardPurchaseRequest {
  final String tier;
  final String paymentMethod;

  PremiumCardPurchaseRequest({required this.tier, required this.paymentMethod});

  Map<String, dynamic> toJson() {
    return {'tier': tier, 'payment_method': paymentMethod};
  }
}

class PremiumCardActivationRequest {
  final String verificationCode;

  PremiumCardActivationRequest({required this.verificationCode});

  Map<String, dynamic> toJson() {
    return {'verification_code': verificationCode};
  }
}

class PremiumStatus {
  final bool hasPremium;
  final String tier;
  final PremiumDigitalCard? activeCard;

  PremiumStatus({
    required this.hasPremium,
    required this.tier,
    this.activeCard,
  });

  factory PremiumStatus.fromJson(Map<String, dynamic> json) {
    return PremiumStatus(
      hasPremium: json['has_premium'] ?? false,
      tier: json['tier'] ?? 'normal',
      activeCard: json['active_card'] != null
          ? PremiumDigitalCard.fromJson(json['active_card'])
          : null,
    );
  }
}
