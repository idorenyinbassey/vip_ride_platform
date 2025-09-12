class User {
  final String id;
  final String name;
  final String email;
  final String? phone;
  final String role;
  final String? profileImage;
  final DateTime createdAt;
  final DateTime? lastLogin;
  final bool isActive;
  final UserPreferences preferences;
  final VipMembership? vipMembership;
  final String? memberSince;
  final String? tierLevel;
  final String? renewalDate;

  const User({
    required this.id,
    required this.name,
    required this.email,
    this.phone,
    required this.role,
    this.profileImage,
    required this.createdAt,
    this.lastLogin,
    this.isActive = true,
    required this.preferences,
    this.vipMembership,
    this.memberSince,
    this.tierLevel,
    this.renewalDate,
  });

  // Getter for fullName (same as name for now)
  String get fullName => name;

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      phone: json['phone'],
      role: json['role'],
      profileImage: json['profile_image'],
      createdAt: DateTime.parse(json['created_at']),
      lastLogin: json['last_login'] != null
          ? DateTime.parse(json['last_login'])
          : null,
      isActive: json['is_active'] ?? true,
      preferences: UserPreferences.fromJson(json['preferences'] ?? {}),
      vipMembership: json['vip_membership'] != null
          ? VipMembership.fromJson(json['vip_membership'])
          : null,
      memberSince: json['member_since'],
      tierLevel: json['tier_level'],
      renewalDate: json['renewal_date'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'phone': phone,
      'role': role,
      'profile_image': profileImage,
      'created_at': createdAt.toIso8601String(),
      'last_login': lastLogin?.toIso8601String(),
      'is_active': isActive,
      'preferences': preferences.toJson(),
      'vip_membership': vipMembership?.toJson(),
      'member_since': memberSince,
      'tier_level': tierLevel,
      'renewal_date': renewalDate,
    };
  }

  bool get isVipPremium => vipMembership?.tier == 'vip_premium';
  bool get isVip => vipMembership?.tier == 'vip' || isVipPremium;
  bool get hasActiveVipMembership => vipMembership?.isActive == true;

  User copyWith({
    String? id,
    String? name,
    String? email,
    String? phone,
    String? role,
    String? profileImage,
    DateTime? createdAt,
    DateTime? lastLogin,
    bool? isActive,
    UserPreferences? preferences,
    VipMembership? vipMembership,
    String? memberSince,
    String? tierLevel,
    String? renewalDate,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      role: role ?? this.role,
      profileImage: profileImage ?? this.profileImage,
      createdAt: createdAt ?? this.createdAt,
      lastLogin: lastLogin ?? this.lastLogin,
      isActive: isActive ?? this.isActive,
      preferences: preferences ?? this.preferences,
      vipMembership: vipMembership ?? this.vipMembership,
      memberSince: memberSince ?? this.memberSince,
      tierLevel: tierLevel ?? this.tierLevel,
      renewalDate: renewalDate ?? this.renewalDate,
    );
  }
}

class VipMembership {
  final String id;
  final String userId;
  final String tier; // vip, vip_premium
  final DateTime startDate;
  final DateTime endDate;
  final bool isActive;
  final double monthlyFee;
  final List<String> benefits;
  final VipMembershipSettings settings;
  final int ridesThisMonth;
  final double discountPercentage;

  const VipMembership({
    required this.id,
    required this.userId,
    required this.tier,
    required this.startDate,
    required this.endDate,
    required this.isActive,
    required this.monthlyFee,
    required this.benefits,
    required this.settings,
    this.ridesThisMonth = 0,
    this.discountPercentage = 0.0,
  });

  factory VipMembership.fromJson(Map<String, dynamic> json) {
    return VipMembership(
      id: json['id'],
      userId: json['user_id'],
      tier: json['tier'],
      startDate: DateTime.parse(json['start_date']),
      endDate: DateTime.parse(json['end_date']),
      isActive: json['is_active'] ?? true,
      monthlyFee: json['monthly_fee']?.toDouble() ?? 0.0,
      benefits: List<String>.from(json['benefits'] ?? []),
      settings: VipMembershipSettings.fromJson(json['settings'] ?? {}),
      ridesThisMonth: json['rides_this_month'] ?? 0,
      discountPercentage: json['discount_percentage']?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'tier': tier,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate.toIso8601String(),
      'is_active': isActive,
      'monthly_fee': monthlyFee,
      'benefits': benefits,
      'settings': settings.toJson(),
      'rides_this_month': ridesThisMonth,
      'discount_percentage': discountPercentage,
    };
  }

  bool get isVipPremium => tier == 'vip_premium';
  bool get isExpiringSoon => endDate.difference(DateTime.now()).inDays <= 30;
}

class VipMembershipSettings {
  final bool discreetModeEnabled;
  final bool encryptedTrackingEnabled;
  final bool conciergeNotifications;
  final bool hotelPartnershipEnabled;
  final bool emergencyContactsEnabled;
  final bool priorityBookingEnabled;
  final List<String> emergencyContacts;

  const VipMembershipSettings({
    this.discreetModeEnabled = true,
    this.encryptedTrackingEnabled = true,
    this.conciergeNotifications = true,
    this.hotelPartnershipEnabled = true,
    this.emergencyContactsEnabled = true,
    this.priorityBookingEnabled = true,
    this.emergencyContacts = const [],
  });

  factory VipMembershipSettings.fromJson(Map<String, dynamic> json) {
    return VipMembershipSettings(
      discreetModeEnabled: json['discreet_mode_enabled'] ?? true,
      encryptedTrackingEnabled: json['encrypted_tracking_enabled'] ?? true,
      conciergeNotifications: json['concierge_notifications'] ?? true,
      hotelPartnershipEnabled: json['hotel_partnership_enabled'] ?? true,
      emergencyContactsEnabled: json['emergency_contacts_enabled'] ?? true,
      priorityBookingEnabled: json['priority_booking_enabled'] ?? true,
      emergencyContacts: List<String>.from(json['emergency_contacts'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'discreet_mode_enabled': discreetModeEnabled,
      'encrypted_tracking_enabled': encryptedTrackingEnabled,
      'concierge_notifications': conciergeNotifications,
      'hotel_partnership_enabled': hotelPartnershipEnabled,
      'emergency_contacts_enabled': emergencyContactsEnabled,
      'priority_booking_enabled': priorityBookingEnabled,
      'emergency_contacts': emergencyContacts,
    };
  }
}

class UserPreferences {
  final String language;
  final String currency;
  final bool darkModeEnabled;
  final bool notificationsEnabled;
  final bool locationServicesEnabled;
  final String preferredVehicleType;
  final Map<String, dynamic> customSettings;

  const UserPreferences({
    this.language = 'en',
    this.currency = 'NGN',
    this.darkModeEnabled = true,
    this.notificationsEnabled = true,
    this.locationServicesEnabled = true,
    this.preferredVehicleType = 'standard',
    this.customSettings = const {},
  });

  factory UserPreferences.fromJson(Map<String, dynamic> json) {
    return UserPreferences(
      language: json['language'] ?? 'en',
      currency: json['currency'] ?? 'NGN',
      darkModeEnabled: json['dark_mode_enabled'] ?? true,
      notificationsEnabled: json['notifications_enabled'] ?? true,
      locationServicesEnabled: json['location_services_enabled'] ?? true,
      preferredVehicleType: json['preferred_vehicle_type'] ?? 'standard',
      customSettings: json['custom_settings'] ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'language': language,
      'currency': currency,
      'dark_mode_enabled': darkModeEnabled,
      'notifications_enabled': notificationsEnabled,
      'location_services_enabled': locationServicesEnabled,
      'preferred_vehicle_type': preferredVehicleType,
      'custom_settings': customSettings,
    };
  }
}

class EmergencyContact {
  final String id;
  final String name;
  final String phone;
  final String relationship;
  final bool isPrimary;
  final bool canReceiveSosAlerts;

  const EmergencyContact({
    required this.id,
    required this.name,
    required this.phone,
    required this.relationship,
    this.isPrimary = false,
    this.canReceiveSosAlerts = true,
  });

  factory EmergencyContact.fromJson(Map<String, dynamic> json) {
    return EmergencyContact(
      id: json['id'],
      name: json['name'],
      phone: json['phone'],
      relationship: json['relationship'],
      isPrimary: json['is_primary'] ?? false,
      canReceiveSosAlerts: json['can_receive_sos_alerts'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'phone': phone,
      'relationship': relationship,
      'is_primary': isPrimary,
      'can_receive_sos_alerts': canReceiveSosAlerts,
    };
  }
}

class UserStats {
  final int totalRides;
  final int vipRides;
  final double totalSpent;
  final double averageRating;
  final int conciergeChats;
  final DateTime memberSince;
  final Map<String, int> monthlyRides;

  const UserStats({
    required this.totalRides,
    required this.vipRides,
    required this.totalSpent,
    required this.averageRating,
    required this.conciergeChats,
    required this.memberSince,
    required this.monthlyRides,
  });

  factory UserStats.fromJson(Map<String, dynamic> json) {
    return UserStats(
      totalRides: json['total_rides'] ?? 0,
      vipRides: json['vip_rides'] ?? 0,
      totalSpent: json['total_spent']?.toDouble() ?? 0.0,
      averageRating: json['average_rating']?.toDouble() ?? 0.0,
      conciergeChats: json['concierge_chats'] ?? 0,
      memberSince: DateTime.parse(json['member_since']),
      monthlyRides: Map<String, int>.from(json['monthly_rides'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_rides': totalRides,
      'vip_rides': vipRides,
      'total_spent': totalSpent,
      'average_rating': averageRating,
      'concierge_chats': conciergeChats,
      'member_since': memberSince.toIso8601String(),
      'monthly_rides': monthlyRides,
    };
  }
}
