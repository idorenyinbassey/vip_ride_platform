import 'dart:async';
import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import '../models/ride_models.dart';

abstract class BaseLocationService {
  Future<Position?> getCurrentLocation();
  Stream<Position> get locationStream;
  Future<bool> requestLocationPermission();
  Future<void> startLocationTracking();
  void stopLocationTracking();
}

class LocationService implements BaseLocationService {
  static final LocationService _instance = LocationService._internal();
  factory LocationService() => _instance;
  LocationService._internal();

  StreamSubscription<Position>? _positionStreamSubscription;
  Position? _currentPosition;

  // Stream controller for location updates
  final StreamController<Position> _locationController =
      StreamController<Position>.broadcast();
  @override
  Stream<Position> get locationStream => _locationController.stream;

  Position? get currentPosition => _currentPosition;

  // Request location permissions
  @override
  Future<bool> requestLocationPermission() async {
    try {
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        return false;
      }

      // Check current permission status
      LocationPermission permission = await Geolocator.checkPermission();

      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          return false;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        // Show dialog to open app settings
        await openAppSettings();
        return false;
      }

      return true;
    } catch (e) {
      print('Error requesting location permission: $e');
      return false;
    }
  }

  // Get current location once
  @override
  Future<Position?> getCurrentLocation() async {
    try {
      bool hasPermission = await requestLocationPermission();
      if (!hasPermission) {
        return null;
      }

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );

      _currentPosition = position;
      return position;
    } catch (e) {
      print('Error getting current location: $e');
      return null;
    }
  }

  // Start real-time location tracking
  @override
  Future<bool> startLocationTracking() async {
    try {
      bool hasPermission = await requestLocationPermission();
      if (!hasPermission) {
        return false;
      }

      // Configure location settings
      const LocationSettings locationSettings = LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10, // Update every 10 meters
      );

      // Start listening to position stream
      _positionStreamSubscription =
          Geolocator.getPositionStream(
            locationSettings: locationSettings,
          ).listen(
            (Position position) {
              _currentPosition = position;
              _locationController.add(position);
            },
            onError: (error) {
              print('Location stream error: $error');
            },
          );

      return true;
    } catch (e) {
      print('Error starting location tracking: $e');
      return false;
    }
  }

  // Stop location tracking
  @override
  void stopLocationTracking() {
    _positionStreamSubscription?.cancel();
    _positionStreamSubscription = null;
  }

  // Calculate distance between two points
  double calculateDistance(
    double startLat,
    double startLng,
    double endLat,
    double endLng,
  ) {
    return Geolocator.distanceBetween(startLat, startLng, endLat, endLng);
  }

  // Calculate bearing between two points
  double calculateBearing(
    double startLat,
    double startLng,
    double endLat,
    double endLng,
  ) {
    return Geolocator.bearingBetween(startLat, startLng, endLat, endLng);
  }

  // Check if user is within a certain radius of a location
  bool isWithinRadius(
    Position userPosition,
    double targetLat,
    double targetLng,
    double radiusInMeters,
  ) {
    double distance = calculateDistance(
      userPosition.latitude,
      userPosition.longitude,
      targetLat,
      targetLng,
    );
    return distance <= radiusInMeters;
  }

  // Convert Position to LocationData
  LocationData positionToLocationData(Position position, {String? address}) {
    return LocationData(
      address: address ?? 'Current Location',
      latitude: position.latitude,
      longitude: position.longitude,
      placeId: null,
    );
  }

  // Get readable address from coordinates (requires geocoding service)
  Future<String> getAddressFromCoordinates(double lat, double lng) async {
    try {
      // This would require a geocoding service like Google Geocoding API
      // For now, return formatted coordinates
      return '${lat.toStringAsFixed(6)}, ${lng.toStringAsFixed(6)}';
    } catch (e) {
      print('Error getting address: $e');
      return 'Unknown Location';
    }
  }

  // Cleanup
  void dispose() {
    stopLocationTracking();
    _locationController.close();
  }
}

// Location permission helper
class LocationPermissionHelper {
  static Future<bool> hasLocationPermission() async {
    LocationPermission permission = await Geolocator.checkPermission();
    return permission == LocationPermission.always ||
        permission == LocationPermission.whileInUse;
  }

  static Future<bool> isLocationServiceEnabled() async {
    return await Geolocator.isLocationServiceEnabled();
  }

  static Future<void> openLocationSettings() async {
    await Geolocator.openLocationSettings();
  }

  static Future<void> openAppSettings() async {
    await Geolocator.openAppSettings();
  }
}

// Mock location service for testing
class MockLocationService implements BaseLocationService {
  Position? _currentPosition;
  Timer? _locationTimer;

  final StreamController<Position> _mockLocationController =
      StreamController<Position>.broadcast();

  @override
  Stream<Position> get locationStream => _mockLocationController.stream;

  @override
  Future<bool> requestLocationPermission() async {
    return true; // Always return true for mock
  }

  @override
  Future<Position?> getCurrentLocation() async {
    // Return mock Lagos location
    await Future.delayed(const Duration(seconds: 1));

    final mockPosition = Position(
      longitude: 3.3792,
      latitude: 6.5244,
      timestamp: DateTime.now(),
      accuracy: 5.0,
      altitude: 0.0,
      heading: 0.0,
      speed: 0.0,
      speedAccuracy: 0.0,
      altitudeAccuracy: 0.0,
      headingAccuracy: 0.0,
    );

    _currentPosition = mockPosition;
    return mockPosition;
  }

  @override
  Future<void> startLocationTracking() async {
    // Simulate location updates around Lagos
    _locationTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      final random = DateTime.now().millisecondsSinceEpoch % 1000;
      final latOffset = (random - 500) / 100000; // Small random offset
      final lngOffset = (random - 500) / 100000;

      final mockPosition = Position(
        longitude: 3.3792 + lngOffset,
        latitude: 6.5244 + latOffset,
        timestamp: DateTime.now(),
        accuracy: 5.0,
        altitude: 0.0,
        heading: 0.0,
        speed: 0.0,
        speedAccuracy: 0.0,
        altitudeAccuracy: 0.0,
        headingAccuracy: 0.0,
      );

      _currentPosition = mockPosition;
      _mockLocationController.add(mockPosition);
    });
  }

  @override
  void stopLocationTracking() {
    _locationTimer?.cancel();
    _locationTimer = null;
  }
}

class LatLng {
  final double latitude;
  final double longitude;

  const LatLng(this.latitude, this.longitude);
}
