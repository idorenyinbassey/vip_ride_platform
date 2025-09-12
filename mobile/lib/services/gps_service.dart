import 'dart:async';
import 'dart:math';
import 'package:latlong2/latlong.dart' as geo;
import '../models/ride_tracking.dart';
import '../config/api_config.dart';
import 'api_service.dart';
import 'location_service.dart';

class GpsService {
  static final GpsService _instance = GpsService._internal();
  factory GpsService() => _instance;
  GpsService._internal();

  final ApiService _apiService = ApiService();
  StreamController<RideTracking>? _trackingController;
  Timer? _locationTimer;
  String? _currentRideId;
  String? _encryptionSessionId;
  bool _isTracking = false;

  Stream<RideTracking> get trackingStream =>
      _trackingController?.stream ?? const Stream.empty();

  Future<bool> startEncryptedTracking(
    String rideId, {
    bool isVip = false,
  }) async {
    try {
      await stopTracking();
      _currentRideId = rideId;
      _trackingController = StreamController<RideTracking>.broadcast();

      if (isVip) {
        await _initializeEncryptionSession();
      }

      final location = await getCurrentLocation();
      if (location == null) {
        throw Exception('Could not get current location');
      }

      await _startBackendTracking(rideId, location);

      _isTracking = true;
      _locationTimer = Timer.periodic(const Duration(seconds: 5), (
        timer,
      ) async {
        if (_isTracking) {
          await _sendLocationUpdate();
        }
      });

      print('Started GPS tracking for ride: $rideId');
      return true;
    } catch (e) {
      print('Error starting GPS tracking: $e');
      return false;
    }
  }

  Future<void> stopTracking() async {
    if (_isTracking) {
      _isTracking = false;
      _locationTimer?.cancel();
      _locationTimer = null;

      if (_currentRideId != null) {
        try {
          await _terminateEncryptionSession();
        } catch (e) {
          print('Error terminating tracking: $e');
        }
      }

      _currentRideId = null;
      _encryptionSessionId = null;
      await _trackingController?.close();
      _trackingController = null;
    }
  }

  Future<void> _initializeEncryptionSession() async {
    try {
      final clientPublicKey = _generateClientPublicKey();
      final response = await _apiService.post(
        ApiConfig.gpsKeyExchangeEndpoint,
        data: {'client_public_key': clientPublicKey},
      );

      _encryptionSessionId = response.data['session_id'];
      print('Encryption session initialized: $_encryptionSessionId');
    } catch (e) {
      print('Error initializing encryption session: $e');
      throw e;
    }
  }

  Future<void> _startBackendTracking(String rideId, geo.LatLng location) async {
    try {
      await _apiService.post(
        '${ApiConfig.gpsLocationsEndpoint}start/',
        data: {
          'ride_id': rideId,
          'latitude': location.latitude,
          'longitude': location.longitude,
          'session_id': _encryptionSessionId,
        },
      );
    } catch (e) {
      print('Error starting backend tracking: $e');
      throw e;
    }
  }

  Future<void> _sendLocationUpdate() async {
    try {
      final location = await getCurrentLocation();
      if (location == null) return;

      Map<String, dynamic> locationData = {
        'ride_id': _currentRideId,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'timestamp': DateTime.now().toIso8601String(),
        'accuracy': 10.0,
        'speed': 0.0,
      };

      if (_encryptionSessionId != null) {
        final encryptedResponse = await _apiService.post(
          ApiConfig.gpsEncryptEndpoint,
          data: {'session_id': _encryptionSessionId, 'data': locationData},
        );
        locationData = encryptedResponse.data['encrypted_data'];
      }

      final response = await _apiService.post(
        ApiConfig.gpsLocationsEndpoint,
        data: locationData,
      );

      final tracking = _parseTrackingResponse(response.data);
      _trackingController?.add(tracking);
    } catch (e) {
      print('Error sending location update: $e');
    }
  }

  Future<void> _terminateEncryptionSession() async {
    try {
      if (_encryptionSessionId != null) {
        await _apiService.post(
          ApiConfig.gpsTerminateSessionEndpoint,
          data: {'session_id': _encryptionSessionId},
        );
      }
    } catch (e) {
      print('Error terminating encryption session: $e');
    }
  }

  String _generateClientPublicKey() {
    final random = Random();
    return List.generate(
      32,
      (index) => random.nextInt(256).toRadixString(16).padLeft(2, '0'),
    ).join();
  }

  RideTracking _parseTrackingResponse(Map<String, dynamic> data) {
    return RideTracking(
      rideId: data['ride_id'] ?? _currentRideId ?? '',
      driverLocation: geo.LatLng(
        data['driver_latitude']?.toDouble() ?? 0.0,
        data['driver_longitude']?.toDouble() ?? 0.0,
      ),
      passengerLocation: geo.LatLng(
        data['passenger_latitude']?.toDouble() ?? 0.0,
        data['passenger_longitude']?.toDouble() ?? 0.0,
      ),
      routePoints: _parseRoutePoints(data['route_points']),
      estimatedArrival: data['estimated_arrival'] != null
          ? DateTime.tryParse(data['estimated_arrival'])
          : null,
      distance: data['distance']?.toDouble() ?? 0.0,
      duration: data['duration']?.toInt() ?? 0,
    );
  }

  List<geo.LatLng> _parseRoutePoints(dynamic routeData) {
    if (routeData == null) return [];

    if (routeData is List) {
      return routeData.map((point) {
        if (point is Map<String, dynamic>) {
          return geo.LatLng(
            point['latitude']?.toDouble() ?? 0.0,
            point['longitude']?.toDouble() ?? 0.0,
          );
        }
        return geo.LatLng(0.0, 0.0);
      }).toList();
    }

    return [];
  }

  Future<geo.LatLng?> getCurrentLocation() async {
    try {
      final position = await LocationService().getCurrentLocation();
      if (position != null) {
        return geo.LatLng(position.latitude, position.longitude);
      }
      return null;
    } catch (e) {
      print('Error getting current location: $e');
      return null;
    }
  }

  Future<bool> checkLocationPermission() async {
    return await LocationPermissionHelper.hasLocationPermission();
  }

  Future<bool> requestLocationPermission() async {
    return await LocationService().requestLocationPermission();
  }

  Future<double> getLocationAccuracy() async {
    return 10.0;
  }

  Future<void> setLocationAccuracy(double accuracy) async {
    // Implementation for setting GPS accuracy
  }

  bool get isTracking => _isTracking;
  String? get currentRideId => _currentRideId;
  String? get encryptionSessionId => _encryptionSessionId;
}
