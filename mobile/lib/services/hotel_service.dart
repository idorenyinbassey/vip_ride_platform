import 'dart:async';
import '../models/hotel_models.dart';

class HotelService {
  static final HotelService _instance = HotelService._internal();
  factory HotelService() => _instance;
  HotelService._internal();

  // Mock data for development
  final List<Hotel> _mockPartnerHotels = [
    Hotel(
      id: '1',
      name: 'Eko Hotel & Suites',
      address: 'Plot 1415, Adetokunbo Ademola Street, Victoria Island, Lagos',
      starRating: 5,
      imageUrl: 'https://example.com/eko_hotel.jpg',
      vipPerks: [
        'Free Upgrade',
        'Priority Check-in',
        'Complimentary Breakfast',
        'Airport Transfer',
      ],
      latitude: 6.4265,
      longitude: 3.4256,
      partnerLevel: 'premium',
    ),
    Hotel(
      id: '2',
      name: 'Radisson Blu Anchorage Hotel',
      address: 'Plot 1A, Ozumba Mbadiwe Avenue, Victoria Island, Lagos',
      starRating: 4,
      imageUrl: 'https://example.com/radisson_blu.jpg',
      vipPerks: [
        'Late Checkout',
        'VIP Lounge Access',
        'Spa Discount',
        'Premium WiFi',
      ],
      latitude: 6.4284,
      longitude: 3.4219,
      partnerLevel: 'gold',
    ),
    Hotel(
      id: '3',
      name: 'Four Points by Sheraton Lagos',
      address: 'Plot 8A, Ahmadu Bello Way, Victoria Island, Lagos',
      starRating: 4,
      imageUrl: 'https://example.com/four_points.jpg',
      vipPerks: [
        'Room Upgrade',
        'Welcome Drink',
        'Fitness Center',
        'Business Lounge',
      ],
      latitude: 6.4302,
      longitude: 3.4274,
      partnerLevel: 'silver',
    ),
  ];

  final List<HotelBooking> _mockBookings = [
    HotelBooking(
      id: 'booking_1',
      hotelId: '1',
      hotelName: 'Eko Hotel & Suites',
      userId: 'user_123',
      pickupTime: '2024-01-20 14:30',
      destination: 'Murtala Muhammed Airport',
      status: 'Confirmed',
      bookingDate: DateTime.now().subtract(const Duration(days: 1)),
      specialRequests: 'VIP terminal access requested',
      conciergeBooked: true,
    ),
  ];

  /// Get all partner hotels
  Future<List<Hotel>> getPartnerHotels() async {
    // Simulate API call delay
    await Future.delayed(const Duration(milliseconds: 800));
    return List.from(_mockPartnerHotels);
  }

  /// Get upcoming hotel bookings for user
  Future<List<HotelBooking>> getUpcomingBookings() async {
    // Simulate API call delay
    await Future.delayed(const Duration(milliseconds: 600));
    return List.from(_mockBookings);
  }

  /// Get hotel details by ID
  Future<Hotel?> getHotelById(String hotelId) async {
    await Future.delayed(const Duration(milliseconds: 300));
    try {
      return _mockPartnerHotels.firstWhere((hotel) => hotel.id == hotelId);
    } catch (e) {
      return null;
    }
  }

  /// Book a ride from a hotel
  Future<bool> bookHotelRide({
    required String hotelId,
    required String destination,
    required DateTime pickupTime,
    String? specialRequests,
  }) async {
    // Simulate API call delay
    await Future.delayed(const Duration(seconds: 2));

    // Mock booking creation
    final newBooking = HotelBooking(
      id: 'booking_${DateTime.now().millisecondsSinceEpoch}',
      hotelId: hotelId,
      hotelName: _mockPartnerHotels.firstWhere((h) => h.id == hotelId).name,
      userId: 'current_user',
      pickupTime:
          '${pickupTime.hour}:${pickupTime.minute.toString().padLeft(2, '0')}',
      destination: destination,
      status: 'Pending',
      bookingDate: DateTime.now(),
      specialRequests: specialRequests,
      conciergeBooked: true,
    );

    _mockBookings.add(newBooking);
    return true; // Success
  }

  /// Get hotel perks for VIP Premium users
  Future<List<String>> getVipPremiumPerks(String hotelId) async {
    await Future.delayed(const Duration(milliseconds: 200));

    final hotel = _mockPartnerHotels.where((h) => h.id == hotelId).firstOrNull;
    if (hotel != null) {
      return List.from(hotel.vipPerks);
    }

    return [];
  }

  /// Check availability for hotel pickup
  Future<bool> checkPickupAvailability({
    required String hotelId,
    required DateTime pickupTime,
  }) async {
    await Future.delayed(const Duration(milliseconds: 500));

    // Mock availability check - always return true for demo
    // In real implementation, this would check driver availability,
    // hotel partnerships, and time constraints
    return true;
  }

  /// Get estimated fare for hotel ride
  Future<double> getEstimatedFare({
    required String hotelId,
    required String destination,
    required String vehicleType,
  }) async {
    await Future.delayed(const Duration(milliseconds: 400));

    // Mock fare calculation
    double baseFare;
    switch (vehicleType) {
      case 'luxury_sedan':
        baseFare = 15000;
        break;
      case 'luxury_suv':
        baseFare = 25000;
        break;
      case 'armored_vehicle':
        baseFare = 50000;
        break;
      default:
        baseFare = 10000;
    }

    // Add distance factor (mock)
    final distanceFactor = 1.2; // Simulated distance multiplier
    return baseFare * distanceFactor;
  }

  /// Cancel hotel booking
  Future<bool> cancelHotelBooking(String bookingId) async {
    await Future.delayed(const Duration(milliseconds: 600));

    _mockBookings.removeWhere((booking) => booking.id == bookingId);
    return true;
  }

  /// Get hotels near location
  Future<List<Hotel>> getHotelsNearLocation({
    required double latitude,
    required double longitude,
    double radiusKm = 10.0,
  }) async {
    await Future.delayed(const Duration(milliseconds: 700));

    // In real implementation, this would calculate distance
    // For now, return all partner hotels
    return List.from(_mockPartnerHotels);
  }
}
