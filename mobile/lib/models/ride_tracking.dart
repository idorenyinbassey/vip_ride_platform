import 'package:latlong2/latlong.dart' as geo;

class RideTracking {
  final String rideId;
  final geo.LatLng driverLocation;
  final geo.LatLng passengerLocation;
  final List<geo.LatLng> routePoints;
  final DateTime? estimatedArrival;
  final double distance;
  final int duration;
  final String? status;
  final String? eta;
  final String? driverName;
  final String? encryptedData;

  RideTracking({
    required this.rideId,
    required this.driverLocation,
    required this.passengerLocation,
    required this.routePoints,
    this.estimatedArrival,
    required this.distance,
    required this.duration,
    this.status,
    this.eta,
    this.driverName,
    this.encryptedData,
  });

  // Getters for backward compatibility
  double get userLat => passengerLocation.latitude;
  double get userLng => passengerLocation.longitude;
  double get driverLat => driverLocation.latitude;
  double get driverLng => driverLocation.longitude;
  List<geo.LatLng> get route => routePoints;

  factory RideTracking.fromJson(Map<String, dynamic> json) {
    return RideTracking(
      rideId: json['ride_id'] ?? '',
      driverLocation: geo.LatLng(
        json['driver_latitude']?.toDouble() ?? 0.0,
        json['driver_longitude']?.toDouble() ?? 0.0,
      ),
      passengerLocation: geo.LatLng(
        json['passenger_latitude']?.toDouble() ?? 0.0,
        json['passenger_longitude']?.toDouble() ?? 0.0,
      ),
      routePoints: _parseRoutePoints(json['route_points']),
      estimatedArrival: json['estimated_arrival'] != null
          ? DateTime.tryParse(json['estimated_arrival'])
          : null,
      distance: json['distance']?.toDouble() ?? 0.0,
      duration: json['duration']?.toInt() ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'ride_id': rideId,
      'driver_latitude': driverLocation.latitude,
      'driver_longitude': driverLocation.longitude,
      'passenger_latitude': passengerLocation.latitude,
      'passenger_longitude': passengerLocation.longitude,
      'route_points': routePoints
          .map(
            (point) => {
              'latitude': point.latitude,
              'longitude': point.longitude,
            },
          )
          .toList(),
      'estimated_arrival': estimatedArrival?.toIso8601String(),
      'distance': distance,
      'duration': duration,
    };
  }

  static List<geo.LatLng> _parseRoutePoints(dynamic routeData) {
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
}
