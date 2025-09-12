import 'dart:async';
import 'package:dio/dio.dart';
import 'package:geolocator/geolocator.dart';
import 'package:flutter/foundation.dart';
import '../models/ride_models.dart';
import '../services/api_service.dart';

class RideService {
  static final RideService _instance = RideService._internal();
  factory RideService() => _instance;
  RideService._internal();

  final ApiService _apiService = ApiService();

  // Stream controllers for real-time updates
  final StreamController<Ride> _rideUpdatesController =
      StreamController<Ride>.broadcast();
  final StreamController<String> _driverLocationController =
      StreamController<String>.broadcast();
  final Map<String, Timer> _activeRideTimers = {};

  Stream<Ride> get rideUpdates => _rideUpdatesController.stream;
  Stream<String> get driverLocationUpdates => _driverLocationController.stream;

  /// Book a new ride with real backend integration
  Future<RideResponse> bookRide(RideRequest request) async {
    try {
      debugPrint('🚗 Booking ride: ${request.toJson()}');

      // Prepare ride data for backend
      final rideData = {
        'pickup_location': {
          'latitude': request.pickup.latitude,
          'longitude': request.pickup.longitude,
          'address': request.pickup.address,
        },
        'destination_location': {
          'latitude': request.destination.latitude,
          'longitude': request.destination.longitude,
          'address': request.destination.address,
        },
        'vehicle_type': request.vehicleType,
        'service_level': request.serviceLevel,
        'payment_method': request.paymentMethod,
        'special_requests': request.specialRequests,
        'estimated_fare': request.estimatedFare,
        'is_scheduled': request.isScheduled,
        'scheduled_time': request.scheduledTime?.toIso8601String(),
        'passenger_count': request.passengerCount,
        'luggage_count': request.luggageCount,
        'vip_features': request.vipFeatures,
      };

      final response = await _apiService.post(
        '/api/v1/rides/workflow/request/',
        data: rideData,
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final rideData = response.data;
        final ride = Ride.fromJson(rideData);

        // Start real-time tracking for this ride
        _startRideTracking(ride.id);

        debugPrint('✅ Ride booked successfully: ${ride.id}');

        return RideResponse(
          success: true,
          rideId: ride.id,
          message: 'Ride booked successfully! Finding nearby drivers...',
          data: rideData,
          ride: ride,
        );
      } else {
        throw Exception('Failed to book ride: ${response.statusMessage}');
      }
    } catch (e) {
      debugPrint('❌ Ride booking failed: $e');
      return RideResponse(success: false, message: _getErrorMessage(e));
    }
  }

  /// Get real-time ride status and updates
  Future<Ride?> getRideDetails(String rideId) async {
    try {
      final response = await _apiService.get(
        '/api/v1/rides/workflow/$rideId/status/',
      );

      if (response.statusCode == 200) {
        final ride = Ride.fromJson(response.data);

        // Emit update to stream
        _rideUpdatesController.add(ride);

        return ride;
      }
    } catch (e) {
      debugPrint('❌ Failed to get ride details: $e');
    }
    return null;
  }

  /// Start real-time tracking for a ride
  void _startRideTracking(String rideId) {
    // Poll for ride updates every 5 seconds
    _activeRideTimers[rideId] = Timer.periodic(const Duration(seconds: 5), (
      timer,
    ) async {
      try {
        final ride = await getRideDetails(rideId);
        if (ride != null) {
          // Stop tracking if ride is completed
          if (ride.status == 'completed' || ride.status == 'cancelled') {
            _stopRideTracking(rideId);
          }
        }
      } catch (e) {
        debugPrint('❌ Error updating ride $rideId: $e');
      }
    });
  }

  /// Stop real-time tracking for a ride
  void _stopRideTracking(String rideId) {
    _activeRideTimers[rideId]?.cancel();
    _activeRideTimers.remove(rideId);
  }

  /// Cancel a ride
  Future<bool> cancelRide(String rideId, String reason) async {
    try {
      final response = await _apiService.post(
        '/api/v1/rides/workflow/$rideId/cancel/',
        data: {'reason': reason, 'cancelled_by': 'passenger'},
      );

      if (response.statusCode == 200) {
        _stopRideTracking(rideId);
        debugPrint('✅ Ride cancelled successfully: $rideId');
        return true;
      }
    } catch (e) {
      debugPrint('❌ Failed to cancel ride: $e');
    }
    return false;
  }

  /// Get available drivers near pickup location
  Future<List<Driver>> getNearbyDrivers(
    double latitude,
    double longitude,
    String vehicleType,
  ) async {
    try {
      final response = await _apiService.get(
        '/api/v1/rides/matching/matching/active_offers/',
        queryParameters: {
          'latitude': latitude,
          'longitude': longitude,
          'vehicle_type': vehicleType,
          'radius': 5000, // 5km radius
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> driversData = response.data['drivers'] ?? [];
        return driversData.map((data) => Driver.fromJson(data)).toList();
      }
    } catch (e) {
      debugPrint('❌ Failed to get nearby drivers: $e');
    }
    return [];
  }

  /// Get estimated fare for a ride
  Future<FareEstimate?> getEstimatedFare(RideRequest request) async {
    try {
      final response = await _apiService.post(
        '/api/v1/pricing/quote/',
        data: {
          'pickup_latitude': request.pickup.latitude,
          'pickup_longitude': request.pickup.longitude,
          'destination_latitude': request.destination.latitude,
          'destination_longitude': request.destination.longitude,
          'vehicle_type': request.vehicleType,
          'service_level': request.serviceLevel,
          'time_of_day': DateTime.now().hour,
          'day_of_week': DateTime.now().weekday,
        },
      );

      if (response.statusCode == 200) {
        return FareEstimate.fromJson(response.data);
      }
    } catch (e) {
      debugPrint('❌ Failed to get fare estimate: $e');
    }
    return null;
  }

  /// Get user's ride history
  Future<List<Ride>> getRideHistory({int page = 1, int limit = 20}) async {
    try {
      final response = await _apiService.get(
        '/api/v1/rides/workflow/history/',
        queryParameters: {'page': page, 'limit': limit},
      );

      if (response.statusCode == 200) {
        final List<dynamic> ridesData = response.data['results'] ?? [];
        return ridesData.map((data) => Ride.fromJson(data)).toList();
      }
    } catch (e) {
      debugPrint('❌ Failed to get ride history: $e');
    }
    return [];
  }

  /// Get active rides for the user
  Future<List<Ride>> getActiveRides() async {
    try {
      final response = await _apiService.get('/api/v1/rides/workflow/active/');

      if (response.statusCode == 200) {
        final List<dynamic> ridesData = response.data['results'] ?? [];
        final rides = ridesData.map((data) => Ride.fromJson(data)).toList();

        // Start tracking for any active rides
        for (final ride in rides) {
          if (!_activeRideTimers.containsKey(ride.id)) {
            _startRideTracking(ride.id);
          }
        }

        return rides;
      }
    } catch (e) {
      debugPrint('❌ Failed to get active rides: $e');
    }
    return [];
  }

  /// Rate a completed ride
  Future<bool> rateRide(String rideId, double rating, String? comment) async {
    try {
      final response = await _apiService.post(
        '/api/v1/rides/workflow/$rideId/rate/',
        data: {'rating': rating, 'comment': comment},
      );

      return response.statusCode == 200;
    } catch (e) {
      debugPrint('❌ Failed to rate ride: $e');
      return false;
    }
  }

  /// Send SOS for VIP users
  Future<bool> sendSOS(String rideId, String? message) async {
    try {
      final position = await Geolocator.getCurrentPosition();

      final response = await _apiService.post(
        '/api/v1/rides/workflow/$rideId/sos/',
        data: {
          'ride_id': rideId,
          'message': message ?? 'Emergency assistance needed',
          'latitude': position.latitude,
          'longitude': position.longitude,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );

      if (response.statusCode == 200) {
        debugPrint('🚨 SOS sent successfully for ride: $rideId');
        return true;
      }
    } catch (e) {
      debugPrint('❌ Failed to send SOS: $e');
    }
    return false;
  }

  /// Get ride tracking data (for VIP users with GPS encryption)
  Future<List<LocationPoint>> getRideTracking(String rideId) async {
    try {
      final response = await _apiService.get(
        '/api/v1/gps/locations/',
        queryParameters: {'ride_id': rideId},
      );

      if (response.statusCode == 200) {
        final List<dynamic> trackingData = response.data['results'] ?? [];
        return trackingData
            .map((data) => LocationPoint.fromJson(data))
            .toList();
      }
    } catch (e) {
      debugPrint('❌ Failed to get ride tracking: $e');
    }
    return [];
  }

  /// Search for addresses/places
  Future<List<PlaceSearchResult>> searchPlaces(String query) async {
    try {
      final response = await _apiService.get(
        '/api/v1/places/search/',
        queryParameters: {'q': query, 'limit': 10},
      );

      if (response.statusCode == 200) {
        final List<dynamic> placesData = response.data['results'] ?? [];
        return placesData
            .map((data) => PlaceSearchResult.fromJson(data))
            .toList();
      }
    } catch (e) {
      debugPrint('❌ Failed to search places: $e');
    }
    return [];
  }

  /// Get user's rides (alias for getRideHistory for compatibility)
  Future<List<Ride>> getUserRides({String? userId}) async {
    return await getRideHistory();
  }

  /// Helper method to get user-friendly error messages
  String _getErrorMessage(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return 'Connection timeout. Please check your internet connection.';
        case DioExceptionType.badResponse:
          if (error.response?.statusCode == 400) {
            return 'Invalid ride request. Please check your details.';
          } else if (error.response?.statusCode == 401) {
            return 'Please log in again.';
          } else if (error.response?.statusCode == 404) {
            return 'Service not available in your area.';
          } else if (error.response?.statusCode == 500) {
            return 'Server error. Please try again later.';
          }
          return 'Failed to book ride. Please try again.';
        case DioExceptionType.cancel:
          return 'Request was cancelled.';
        case DioExceptionType.unknown:
          return 'Network error. Please check your connection.';
        default:
          return 'Something went wrong. Please try again.';
      }
    }
    return 'Failed to book ride. Please try again.';
  }

  /// Dispose resources
  void dispose() {
    _rideUpdatesController.close();
    _driverLocationController.close();
    for (final timer in _activeRideTimers.values) {
      timer.cancel();
    }
    _activeRideTimers.clear();
  }
}
