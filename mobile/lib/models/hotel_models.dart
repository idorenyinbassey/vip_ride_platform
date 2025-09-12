class Hotel {
  final String id;
  final String name;
  final String address;
  final int starRating;
  final String? imageUrl;
  final List<String> vipPerks;
  final double latitude;
  final double longitude;
  final bool isPartner;
  final String partnerLevel;

  const Hotel({
    required this.id,
    required this.name,
    required this.address,
    required this.starRating,
    this.imageUrl,
    required this.vipPerks,
    required this.latitude,
    required this.longitude,
    this.isPartner = true,
    this.partnerLevel = 'premium',
  });

  factory Hotel.fromJson(Map<String, dynamic> json) {
    return Hotel(
      id: json['id'],
      name: json['name'],
      address: json['address'],
      starRating: json['star_rating'] ?? 5,
      imageUrl: json['image_url'],
      vipPerks: List<String>.from(json['vip_perks'] ?? []),
      latitude: json['latitude']?.toDouble() ?? 0.0,
      longitude: json['longitude']?.toDouble() ?? 0.0,
      isPartner: json['is_partner'] ?? true,
      partnerLevel: json['partner_level'] ?? 'premium',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'address': address,
      'star_rating': starRating,
      'image_url': imageUrl,
      'vip_perks': vipPerks,
      'latitude': latitude,
      'longitude': longitude,
      'is_partner': isPartner,
      'partner_level': partnerLevel,
    };
  }
}

class HotelBooking {
  final String id;
  final String hotelId;
  final String hotelName;
  final String userId;
  final String pickupTime;
  final String destination;
  final String status;
  final DateTime bookingDate;
  final String? specialRequests;
  final bool conciergeBooked;

  const HotelBooking({
    required this.id,
    required this.hotelId,
    required this.hotelName,
    required this.userId,
    required this.pickupTime,
    required this.destination,
    required this.status,
    required this.bookingDate,
    this.specialRequests,
    this.conciergeBooked = false,
  });

  factory HotelBooking.fromJson(Map<String, dynamic> json) {
    return HotelBooking(
      id: json['id'],
      hotelId: json['hotel_id'],
      hotelName: json['hotel_name'],
      userId: json['user_id'],
      pickupTime: json['pickup_time'],
      destination: json['destination'],
      status: json['status'],
      bookingDate: DateTime.parse(json['booking_date']),
      specialRequests: json['special_requests'],
      conciergeBooked: json['concierge_booked'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'hotel_id': hotelId,
      'hotel_name': hotelName,
      'user_id': userId,
      'pickup_time': pickupTime,
      'destination': destination,
      'status': status,
      'booking_date': bookingDate.toIso8601String(),
      'special_requests': specialRequests,
      'concierge_booked': conciergeBooked,
    };
  }
}

class HotelPartnership {
  final String id;
  final String hotelId;
  final String partnerLevel;
  final List<String> benefits;
  final double discountPercentage;
  final DateTime startDate;
  final DateTime? endDate;
  final bool isActive;

  const HotelPartnership({
    required this.id,
    required this.hotelId,
    required this.partnerLevel,
    required this.benefits,
    required this.discountPercentage,
    required this.startDate,
    this.endDate,
    this.isActive = true,
  });

  factory HotelPartnership.fromJson(Map<String, dynamic> json) {
    return HotelPartnership(
      id: json['id'],
      hotelId: json['hotel_id'],
      partnerLevel: json['partner_level'],
      benefits: List<String>.from(json['benefits'] ?? []),
      discountPercentage: json['discount_percentage']?.toDouble() ?? 0.0,
      startDate: DateTime.parse(json['start_date']),
      endDate: json['end_date'] != null
          ? DateTime.parse(json['end_date'])
          : null,
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'hotel_id': hotelId,
      'partner_level': partnerLevel,
      'benefits': benefits,
      'discount_percentage': discountPercentage,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate?.toIso8601String(),
      'is_active': isActive,
    };
  }
}
