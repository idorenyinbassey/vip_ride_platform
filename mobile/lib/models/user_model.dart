class User {
  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String? phoneNumber;
  final String userType; // 'client' or 'driver'
  final String tier; // For clients: 'NORMAL', 'PREMIUM', 'VIP'
  final String?
  driverType; // For drivers: 'independent_driver', 'fleet_owner', etc.
  final bool isActive;
  final bool isVerified;
  final String? profilePicture;
  final DateTime? dateJoined;
  final DateTime? lastLogin;

  // Additional fields for different user types
  final Map<String, dynamic>? additionalData;

  // VIP Premium Profile fields
  final String? memberSince;
  final String? tierLevel;
  final String? renewalDate;

  User({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    this.phoneNumber,
    required this.userType,
    required this.tier,
    this.driverType,
    required this.isActive,
    required this.isVerified,
    this.profilePicture,
    this.dateJoined,
    this.lastLogin,
    this.additionalData,
    this.memberSince,
    this.tierLevel,
    this.renewalDate,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'].toString(),
      email: json['email'],
      firstName: json['first_name'] ?? json['firstName'] ?? '',
      lastName: json['last_name'] ?? json['lastName'] ?? '',
      phoneNumber: json['phone_number'] ?? json['phoneNumber'],
      userType: json['user_type'] ?? json['userType'] ?? 'client',
      tier: json['tier'] ?? 'normal',
      driverType: json['driver_type'] ?? json['driverType'],
      isActive: json['is_active'] ?? json['isActive'] ?? true,
      isVerified: json['is_verified'] ?? json['isVerified'] ?? false,
      profilePicture: json['profile_picture'] ?? json['profilePicture'],
      dateJoined: json['date_joined'] != null
          ? DateTime.parse(json['date_joined'])
          : null,
      lastLogin: json['last_login'] != null
          ? DateTime.parse(json['last_login'])
          : null,
      additionalData: json['additional_data'] ?? json['additionalData'],
      memberSince:
          json['member_since'] ??
          json['dateJoined']?.toString().substring(0, 7),
      tierLevel: json['tier_level'] ?? json['tier'],
      renewalDate: json['renewal_date'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'phone_number': phoneNumber,
      'user_type': userType,
      'tier': tier,
      'driver_type': driverType,
      'is_active': isActive,
      'is_verified': isVerified,
      'profile_picture': profilePicture,
      'date_joined': dateJoined?.toIso8601String(),
      'last_login': lastLogin?.toIso8601String(),
      'additional_data': additionalData,
      'member_since': memberSince,
      'tier_level': tierLevel,
      'renewal_date': renewalDate,
    };
  }

  String get fullName => '$firstName $lastName';

  bool get isClient => userType == 'client' || userType == 'customer';
  bool get isDriver => userType == 'driver';

  // Client tier getters - corrected architecture
  bool get isRegularClient => isClient && tier == 'normal';
  bool get isPremiumClient => isClient && tier == 'premium';
  bool get isVipClient => isClient && tier == 'vip';

  // Black-Tier includes both Premium and VIP users
  bool get isBlackTierClient =>
      isClient && (tier == 'premium' || tier == 'vip');

  bool get isIndependentDriver =>
      isDriver && driverType == 'independent_driver';
  bool get isFleetOwner => isDriver && driverType == 'fleet_owner';
  bool get isFleetDriver => isDriver && driverType == 'fleet_driver';
  bool get isLeasedDriver => isDriver && driverType == 'leased_driver';

  // Display name getters
  String get name => '$firstName $lastName'.trim();

  User copyWith({
    String? id,
    String? email,
    String? firstName,
    String? lastName,
    String? phoneNumber,
    String? userType,
    String? tier,
    String? driverType,
    bool? isActive,
    bool? isVerified,
    String? profilePicture,
    DateTime? dateJoined,
    DateTime? lastLogin,
    Map<String, dynamic>? additionalData,
    String? memberSince,
    String? tierLevel,
    String? renewalDate,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      userType: userType ?? this.userType,
      tier: tier ?? this.tier,
      driverType: driverType ?? this.driverType,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      profilePicture: profilePicture ?? this.profilePicture,
      dateJoined: dateJoined ?? this.dateJoined,
      lastLogin: lastLogin ?? this.lastLogin,
      additionalData: additionalData ?? this.additionalData,
      memberSince: memberSince ?? this.memberSince,
      tierLevel: tierLevel ?? this.tierLevel,
      renewalDate: renewalDate ?? this.renewalDate,
    );
  }
}
