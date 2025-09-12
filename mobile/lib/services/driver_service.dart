import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/ride_models.dart';
import '../config/api_config.dart';
import 'api_service.dart';

class DriverService {
  static final DriverService _instance = DriverService._internal();
  factory DriverService() => _instance;
  DriverService._internal();

  final ApiService _apiService = ApiService();

  /// Get available rides for drivers to accept
  Future<List<Ride>> getAvailableRides() async {
    try {
      final response = await _apiService.get(
        '/api/v1/rides/matching/matching/active_offers/',
      );

      if (response.statusCode == 200) {
        final List<dynamic> ridesData = response.data['results'] ?? [];
        return ridesData.map((data) => Ride.fromJson(data)).toList();
      }
    } catch (e) {
      debugPrint('❌ Failed to get available rides: $e');
    }
    return [];
  }

  /// Accept a ride request
  Future<bool> acceptRide(String rideId) async {
    try {
      final response = await _apiService.post(
        '/api/v1/rides/workflow/$rideId/accept/',
        data: {
          'driver_response': 'accept',
          'timestamp': DateTime.now().toIso8601String(),
        },
      );

      if (response.statusCode == 200) {
        debugPrint('✅ Ride accepted: $rideId');
        return true;
      }
    } catch (e) {
      debugPrint('❌ Failed to accept ride: $e');
    }
    return false;
  }

  /// Decline a ride request
  Future<bool> declineRide(String rideId, String reason) async {
    try {
      final response = await _apiService.post(
        '/api/v1/rides/workflow/$rideId/decline/',
        data: {
          'driver_response': 'decline',
          'reason': reason,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );

      if (response.statusCode == 200) {
        debugPrint('✅ Ride declined: $rideId');
        return true;
      }
    } catch (e) {
      debugPrint('❌ Failed to decline ride: $e');
    }
    return false;
  }

  /// Complete a ride
  Future<bool> completeRide(String rideId, {String? notes}) async {
    try {
      final response = await _apiService.post(
        '/api/v1/rides/workflow/$rideId/complete/',
        data: {
          'status': 'completed',
          'completion_notes': notes,
          'completion_time': DateTime.now().toIso8601String(),
        },
      );

      if (response.statusCode == 200) {
        debugPrint('✅ Ride completed: $rideId');
        return true;
      }
    } catch (e) {
      debugPrint('❌ Failed to complete ride: $e');
    }
    return false;
  }

  /// Start a ride (driver arrived and picked up passenger)
  Future<bool> startRide(String rideId) async {
    try {
      final response = await _apiService.post(
        '/api/v1/rides/workflow/$rideId/start/',
        data: {
          'status': 'in_progress',
          'pickup_time': DateTime.now().toIso8601String(),
        },
      );

      if (response.statusCode == 200) {
        debugPrint('✅ Ride started: $rideId');
        return true;
      }
    } catch (e) {
      debugPrint('❌ Failed to start ride: $e');
    }
    return false;
  }

  /// Update driver status (online/offline)
  Future<bool> updateDriverStatus(bool isOnline) async {
    try {
      final response = await _apiService.post(
        '/api/v1/rides/matching/matching/driver_status/',
        data: {
          'status': isOnline ? 'online' : 'offline',
          'timestamp': DateTime.now().toIso8601String(),
        },
      );

      return response.statusCode == 200;
    } catch (e) {
      debugPrint('❌ Failed to update driver status: $e');
      return false;
    }
  }

  /// Update driver location
  Future<bool> updateDriverLocation(double latitude, double longitude) async {
    try {
      final response = await _apiService.post(
        '/api/v1/gps/locations/',
        data: {
          'latitude': latitude,
          'longitude': longitude,
          'timestamp': DateTime.now().toIso8601String(),
          'accuracy': 'high',
        },
      );

      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      debugPrint('❌ Failed to update driver location: $e');
      return false;
    }
  }

  /// Get driver's active rides
  Future<List<Ride>> getActiveRides() async {
    try {
      final response = await _apiService.get('/api/v1/rides/workflow/active/');

      if (response.statusCode == 200) {
        final List<dynamic> ridesData = response.data['results'] ?? [];
        return ridesData.map((data) => Ride.fromJson(data)).toList();
      }
    } catch (e) {
      debugPrint('❌ Failed to get active rides: $e');
    }
    return [];
  }

  /// Get driver's ride history
  Future<List<Ride>> getRideHistory({int page = 1, int limit = 20}) async {
    try {
      final response = await _apiService.get(
        '/api/v1/rides/workflow/history/',
        queryParameters: {'page': page, 'limit': limit, 'driver_view': true},
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

  /// Get driver earnings
  Future<Map<String, dynamic>?> getDriverEarnings({
    String period = 'week', // day, week, month, year
  }) async {
    try {
      final response = await _apiService.get(
        '/api/v1/payments/driver-payouts/earnings_summary/',
        queryParameters: {'period': period},
      );

      if (response.statusCode == 200) {
        return response.data;
      }
    } catch (e) {
      debugPrint('❌ Failed to get driver earnings: $e');
    }
    return null;
  }

  /// Get fleet information (for fleet drivers)
  Future<Map<String, dynamic>?> getFleetInfo() async {
    try {
      final response = await _apiService.get(
        '/api/v1/fleet/api/companies/my_fleet/',
      );

      if (response.statusCode == 200) {
        return response.data;
      }
    } catch (e) {
      debugPrint('❌ Failed to get fleet info: $e');
    }
    return null;
  }

  /// Get assigned vehicle (for fleet drivers)
  Future<Map<String, dynamic>?> getAssignedVehicle() async {
    try {
      final response = await _apiService.get(
        '/api/v1/fleet/api/vehicles/my_vehicles/',
      );

      if (response.statusCode == 200) {
        final List vehicles = response.data['results'] ?? [];
        if (vehicles.isNotEmpty) {
          return vehicles.first;
        }
      }
    } catch (e) {
      debugPrint('❌ Failed to get assigned vehicle: $e');
    }
    return null;
  }

  /// Get lease information (for leased drivers)
  Future<Map<String, dynamic>?> getLeaseInfo() async {
    try {
      final response = await _apiService.get(
        '/api/v1/leasing/leases/my_lease/',
      );

      if (response.statusCode == 200) {
        return response.data;
      }
    } catch (e) {
      debugPrint('❌ Failed to get lease info: $e');
    }
    return null;
  }

  /// Report an incident or emergency
  Future<bool> reportIncident({
    required String rideId,
    required String incidentType,
    required String description,
    double? latitude,
    double? longitude,
  }) async {
    try {
      final response = await _apiService.post(
        '/api/v1/control-center/api/incidents/',
        data: {
          'ride_id': rideId,
          'incident_type': incidentType,
          'description': description,
          'reporter_type': 'driver',
          'timestamp': DateTime.now().toIso8601String(),
          if (latitude != null) 'latitude': latitude,
          if (longitude != null) 'longitude': longitude,
        },
      );

      if (response.statusCode == 201) {
        debugPrint('🚨 Incident reported successfully');
        return true;
      }
    } catch (e) {
      debugPrint('❌ Failed to report incident: $e');
    }
    return false;
  }
}
