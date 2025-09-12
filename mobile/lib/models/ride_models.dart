import 'package:latlong2/latlong.dart' as geo;

class LocationData {
  final double latitude;
  final double longitude;
  final String address;
  final String? placeId;

  const LocationData({
    required this.latitude,
    required this.longitude,
    required this.address,
    this.placeId,
  });

  factory LocationData.fromJson(Map<String, dynamic> json) {
    return LocationData(
      latitude: json['latitude']?.toDouble() ?? 0.0,
      longitude: json['longitude']?.toDouble() ?? 0.0,
      address: json['address'] ?? '',
      placeId: json['place_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'latitude': latitude,
      'longitude': longitude,
      'address': address,
      'place_id': placeId,
    };
  }

  geo.LatLng get latLng => geo.LatLng(latitude, longitude);
}

class RideTracking {
  final String rideId;
  final double userLat;
  final double userLng;
  final double driverLat;
  final double driverLng;
  final List<geo.LatLng> route;
  final String status;
  final String eta;
  final String distance;
  final String driverName;
  final String? encryptedData;
  final DateTime lastUpdated;

  const RideTracking({
    required this.rideId,
    required this.userLat,
    required this.userLng,
    required this.driverLat,
    required this.driverLng,
    required this.route,
    required this.status,
    required this.eta,
    required this.distance,
    required this.driverName,
    this.encryptedData,
    required this.lastUpdated,
  });

  factory RideTracking.fromJson(Map<String, dynamic> json) {
    return RideTracking(
      rideId: json['ride_id'] ?? '',
      userLat: json['user_lat']?.toDouble() ?? 0.0,
      userLng: json['user_lng']?.toDouble() ?? 0.0,
      driverLat: json['driver_lat']?.toDouble() ?? 0.0,
      driverLng: json['driver_lng']?.toDouble() ?? 0.0,
      route:
          (json['route'] as List<dynamic>?)
              ?.map(
                (point) => geo.LatLng(
                  point['lat']?.toDouble() ?? 0.0,
                  point['lng']?.toDouble() ?? 0.0,
                ),
              )
              .toList() ??
          [],
      status: json['status'] ?? '',
      eta: json['eta'] ?? '',
      distance: json['distance'] ?? '',
      driverName: json['driver_name'] ?? '',
      encryptedData: json['encrypted_data'],
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'])
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'ride_id': rideId,
      'user_lat': userLat,
      'user_lng': userLng,
      'driver_lat': driverLat,
      'driver_lng': driverLng,
      'route': route
          .map((point) => {'lat': point.latitude, 'lng': point.longitude})
          .toList(),
      'status': status,
      'eta': eta,
      'distance': distance,
      'driver_name': driverName,
      'encrypted_data': encryptedData,
      'last_updated': lastUpdated.toIso8601String(),
    };
  }
}

class RideRequest {
  final LocationData pickup;
  final LocationData destination;
  final String vehicleType;
  final String serviceLevel;
  final String paymentMethod;
  final bool isScheduled;
  final DateTime? scheduledTime;
  final int passengerCount;
  final int luggageCount;
  final String? specialRequests;
  final bool encryptedTracking;
  final Map<String, dynamic>? vipFeatures;
  final double? estimatedFare;

  const RideRequest({
    required this.pickup,
    required this.destination,
    required this.vehicleType,
    required this.serviceLevel,
    required this.paymentMethod,
    this.isScheduled = false,
    this.scheduledTime,
    this.passengerCount = 1,
    this.luggageCount = 0,
    this.specialRequests,
    this.encryptedTracking = false,
    this.vipFeatures,
    this.estimatedFare,
  });

  factory RideRequest.fromJson(Map<String, dynamic> json) {
    return RideRequest(
      pickup: LocationData.fromJson(json['pickup_location']),
      destination: LocationData.fromJson(json['destination_location']),
      vehicleType: json['vehicle_type'] ?? 'standard',
      serviceLevel: json['service_level'] ?? 'regular',
      paymentMethod: json['payment_method'] ?? 'card',
      isScheduled: json['is_scheduled'] ?? false,
      scheduledTime: json['scheduled_time'] != null
          ? DateTime.parse(json['scheduled_time'])
          : null,
      passengerCount: json['passenger_count'] ?? 1,
      luggageCount: json['luggage_count'] ?? 0,
      specialRequests: json['special_requests'],
      encryptedTracking: json['encrypted_tracking'] ?? false,
      vipFeatures: json['vip_features'],
      estimatedFare: json['estimated_fare']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'pickup_location': pickup.toJson(),
      'destination_location': destination.toJson(),
      'vehicle_type': vehicleType,
      'service_level': serviceLevel,
      'payment_method': paymentMethod,
      'is_scheduled': isScheduled,
      'scheduled_time': scheduledTime?.toIso8601String(),
      'passenger_count': passengerCount,
      'luggage_count': luggageCount,
      'special_requests': specialRequests,
      'encrypted_tracking': encryptedTracking,
      'vip_features': vipFeatures,
      'estimated_fare': estimatedFare,
    };
  }
}

class Ride {
  final String id;
  final String userId;
  final String? driverId;
  final LocationData pickup;
  final LocationData destination;
  final String status;
  final String vehicleType;
  final String serviceLevel;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final double? fare;
  final double? estimatedFare;
  final String? driverName;
  final String? driverPhone;
  final double? driverRating;
  final String? vehicleModel;
  final String? vehiclePlate;
  final String? vehicleColor;
  final String paymentMethod;
  final String? paymentStatus;
  final double? rating;
  final String? feedback;
  final bool encryptedTracking;
  final Map<String, dynamic>? vipFeatures;
  final String? cancellationReason;
  final double? distance;
  final int? duration;
  final int? estimatedArrival; // ETA in minutes

  const Ride({
    required this.id,
    required this.userId,
    this.driverId,
    required this.pickup,
    required this.destination,
    required this.status,
    required this.vehicleType,
    required this.serviceLevel,
    required this.createdAt,
    this.updatedAt,
    this.startedAt,
    this.completedAt,
    this.fare,
    this.estimatedFare,
    this.driverName,
    this.driverPhone,
    this.driverRating,
    this.vehicleModel,
    this.vehiclePlate,
    this.vehicleColor,
    required this.paymentMethod,
    this.paymentStatus,
    this.rating,
    this.feedback,
    this.encryptedTracking = false,
    this.vipFeatures,
    this.cancellationReason,
    this.distance,
    this.duration,
    this.estimatedArrival,
  });

  factory Ride.fromJson(Map<String, dynamic> json) {
    return Ride(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? json['user'] ?? '',
      driverId: json['driver_id'] ?? json['driver'],
      pickup: LocationData.fromJson(json['pickup_location'] ?? {}),
      destination: LocationData.fromJson(json['destination_location'] ?? {}),
      status: json['status'] ?? 'pending',
      vehicleType: json['vehicle_type'] ?? 'standard',
      serviceLevel: json['service_level'] ?? 'regular',
      createdAt: DateTime.parse(
        json['created_at'] ?? DateTime.now().toIso8601String(),
      ),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : null,
      startedAt: json['started_at'] != null
          ? DateTime.parse(json['started_at'])
          : null,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'])
          : null,
      fare: json['fare']?.toDouble(),
      estimatedFare: json['estimated_fare']?.toDouble(),
      driverName: json['driver_name'],
      driverPhone: json['driver_phone'],
      driverRating: json['driver_rating']?.toDouble(),
      vehicleModel: json['vehicle_model'],
      vehiclePlate: json['vehicle_plate'],
      vehicleColor: json['vehicle_color'],
      paymentMethod: json['payment_method'] ?? 'card',
      paymentStatus: json['payment_status'],
      rating: json['rating']?.toDouble(),
      feedback: json['feedback'],
      encryptedTracking: json['encrypted_tracking'] ?? false,
      vipFeatures: json['vip_features'],
      cancellationReason: json['cancellation_reason'],
      distance: json['distance']?.toDouble(),
      duration: json['duration']?.toInt(),
      estimatedArrival: json['estimated_arrival']?.toInt(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'driver_id': driverId,
      'pickup_location': pickup.toJson(),
      'destination_location': destination.toJson(),
      'status': status,
      'vehicle_type': vehicleType,
      'service_level': serviceLevel,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'started_at': startedAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'fare': fare,
      'estimated_fare': estimatedFare,
      'driver_name': driverName,
      'driver_phone': driverPhone,
      'driver_rating': driverRating,
      'vehicle_model': vehicleModel,
      'vehicle_plate': vehiclePlate,
      'vehicle_color': vehicleColor,
      'payment_method': paymentMethod,
      'payment_status': paymentStatus,
      'rating': rating,
      'feedback': feedback,
      'encrypted_tracking': encryptedTracking,
      'vip_features': vipFeatures,
      'cancellation_reason': cancellationReason,
      'distance': distance,
      'duration': duration,
      'estimated_arrival': estimatedArrival,
    };
  }

  Ride copyWith({
    String? id,
    String? userId,
    String? driverId,
    LocationData? pickup,
    LocationData? destination,
    String? status,
    String? vehicleType,
    String? serviceLevel,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? startedAt,
    DateTime? completedAt,
    double? fare,
    double? estimatedFare,
    String? driverName,
    String? driverPhone,
    double? driverRating,
    String? vehicleModel,
    String? vehiclePlate,
    String? vehicleColor,
    String? paymentMethod,
    String? paymentStatus,
    double? rating,
    String? feedback,
    bool? encryptedTracking,
    Map<String, dynamic>? vipFeatures,
    String? cancellationReason,
    double? distance,
    int? duration,
    int? estimatedArrival,
  }) {
    return Ride(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      driverId: driverId ?? this.driverId,
      pickup: pickup ?? this.pickup,
      destination: destination ?? this.destination,
      status: status ?? this.status,
      vehicleType: vehicleType ?? this.vehicleType,
      serviceLevel: serviceLevel ?? this.serviceLevel,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      startedAt: startedAt ?? this.startedAt,
      completedAt: completedAt ?? this.completedAt,
      fare: fare ?? this.fare,
      estimatedFare: estimatedFare ?? this.estimatedFare,
      driverName: driverName ?? this.driverName,
      driverPhone: driverPhone ?? this.driverPhone,
      driverRating: driverRating ?? this.driverRating,
      vehicleModel: vehicleModel ?? this.vehicleModel,
      vehiclePlate: vehiclePlate ?? this.vehiclePlate,
      vehicleColor: vehicleColor ?? this.vehicleColor,
      paymentMethod: paymentMethod ?? this.paymentMethod,
      paymentStatus: paymentStatus ?? this.paymentStatus,
      rating: rating ?? this.rating,
      feedback: feedback ?? this.feedback,
      encryptedTracking: encryptedTracking ?? this.encryptedTracking,
      vipFeatures: vipFeatures ?? this.vipFeatures,
      cancellationReason: cancellationReason ?? this.cancellationReason,
      distance: distance ?? this.distance,
      duration: duration ?? this.duration,
      estimatedArrival: estimatedArrival ?? this.estimatedArrival,
    );
  }

  bool get isActive => [
    'pending',
    'accepted',
    'driver_assigned',
    'driver_arriving',
    'in_progress',
  ].contains(status);
  bool get isCompleted => status == 'completed';
  bool get isCancelled => status == 'cancelled';
  bool get hasDriver => driverId != null && driverId!.isNotEmpty;
}

class RideResponse {
  final bool success;
  final String? rideId;
  final String message;
  final Map<String, dynamic>? data;
  final Ride? ride;

  const RideResponse({
    required this.success,
    this.rideId,
    required this.message,
    this.data,
    this.ride,
  });

  factory RideResponse.fromJson(Map<String, dynamic> json) {
    return RideResponse(
      success: json['success'] ?? false,
      rideId: json['ride_id'],
      message: json['message'] ?? '',
      data: json['data'],
      ride: json['ride'] != null ? Ride.fromJson(json['ride']) : null,
    );
  }
}

class Driver {
  final String id;
  final String name;
  final String phone;
  final double rating;
  final String? profileImage;
  final String vehicleModel;
  final String vehiclePlate;
  final String vehicleColor;
  final String vehicleType;
  final double latitude;
  final double longitude;
  final double distance;
  final int eta;
  final bool isOnline;

  const Driver({
    required this.id,
    required this.name,
    required this.phone,
    required this.rating,
    this.profileImage,
    required this.vehicleModel,
    required this.vehiclePlate,
    required this.vehicleColor,
    required this.vehicleType,
    required this.latitude,
    required this.longitude,
    required this.distance,
    required this.eta,
    this.isOnline = true,
  });

  factory Driver.fromJson(Map<String, dynamic> json) {
    return Driver(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      phone: json['phone'] ?? '',
      rating: json['rating']?.toDouble() ?? 0.0,
      profileImage: json['profile_image'],
      vehicleModel: json['vehicle_model'] ?? '',
      vehiclePlate: json['vehicle_plate'] ?? '',
      vehicleColor: json['vehicle_color'] ?? '',
      vehicleType: json['vehicle_type'] ?? '',
      latitude: json['latitude']?.toDouble() ?? 0.0,
      longitude: json['longitude']?.toDouble() ?? 0.0,
      distance: json['distance']?.toDouble() ?? 0.0,
      eta: json['eta']?.toInt() ?? 0,
      isOnline: json['is_online'] ?? true,
    );
  }
}

class FareEstimate {
  final double baseFare;
  final double distanceFare;
  final double timeFare;
  final double surgeMultiplier;
  final double totalFare;
  final String currency;
  final Map<String, double>? breakdown;

  const FareEstimate({
    required this.baseFare,
    required this.distanceFare,
    required this.timeFare,
    required this.surgeMultiplier,
    required this.totalFare,
    required this.currency,
    this.breakdown,
  });

  factory FareEstimate.fromJson(Map<String, dynamic> json) {
    return FareEstimate(
      baseFare: json['base_fare']?.toDouble() ?? 0.0,
      distanceFare: json['distance_fare']?.toDouble() ?? 0.0,
      timeFare: json['time_fare']?.toDouble() ?? 0.0,
      surgeMultiplier: json['surge_multiplier']?.toDouble() ?? 1.0,
      totalFare: json['total_fare']?.toDouble() ?? 0.0,
      currency: json['currency'] ?? 'NGN',
      breakdown: json['breakdown']?.cast<String, double>(),
    );
  }
}

class LocationPoint {
  final double latitude;
  final double longitude;
  final DateTime timestamp;
  final double? speed;
  final double? heading;

  const LocationPoint({
    required this.latitude,
    required this.longitude,
    required this.timestamp,
    this.speed,
    this.heading,
  });

  factory LocationPoint.fromJson(Map<String, dynamic> json) {
    return LocationPoint(
      latitude: json['latitude']?.toDouble() ?? 0.0,
      longitude: json['longitude']?.toDouble() ?? 0.0,
      timestamp: DateTime.parse(json['timestamp']),
      speed: json['speed']?.toDouble(),
      heading: json['heading']?.toDouble(),
    );
  }

  geo.LatLng get latLng => geo.LatLng(latitude, longitude);
}

class PlaceSearchResult {
  final String placeId;
  final String name;
  final String address;
  final double latitude;
  final double longitude;
  final String? type;

  const PlaceSearchResult({
    required this.placeId,
    required this.name,
    required this.address,
    required this.latitude,
    required this.longitude,
    this.type,
  });

  factory PlaceSearchResult.fromJson(Map<String, dynamic> json) {
    return PlaceSearchResult(
      placeId: json['place_id'] ?? '',
      name: json['name'] ?? '',
      address: json['address'] ?? '',
      latitude: json['latitude']?.toDouble() ?? 0.0,
      longitude: json['longitude']?.toDouble() ?? 0.0,
      type: json['type'],
    );
  }

  LocationData get locationData => LocationData(
    latitude: latitude,
    longitude: longitude,
    address: address,
    placeId: placeId,
  );
}

class VehicleType {
  final String id;
  final String name;
  final String description;
  final String iconName;
  final double basePrice;
  final List<String> features;
  final bool isVipOnly;
  final bool isArmoredVehicle;

  const VehicleType({
    required this.id,
    required this.name,
    required this.description,
    required this.iconName,
    required this.basePrice,
    required this.features,
    this.isVipOnly = false,
    this.isArmoredVehicle = false,
  });

  factory VehicleType.fromJson(Map<String, dynamic> json) {
    return VehicleType(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      iconName: json['icon_name'],
      basePrice: json['base_price']?.toDouble() ?? 0.0,
      features: List<String>.from(json['features'] ?? []),
      isVipOnly: json['is_vip_only'] ?? false,
      isArmoredVehicle: json['is_armored_vehicle'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'icon_name': iconName,
      'base_price': basePrice,
      'features': features,
      'is_vip_only': isVipOnly,
      'is_armored_vehicle': isArmoredVehicle,
    };
  }
}
