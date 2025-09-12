class Ride {
  final String id;
  final String riderId;
  final String? driverId;
  final String status;
  final String rideType;
  final String riderTier;
  final Location pickupLocation;
  final Location destinationLocation;
  final double? distance;
  final double? duration;
  final RidePricing? pricing;
  final String? vehicleType;
  final Vehicle? vehicle;
  final Driver? driver;
  final DateTime createdAt;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final DateTime? cancelledAt;
  final Map<String, dynamic>? metadata;

  Ride({
    required this.id,
    required this.riderId,
    this.driverId,
    required this.status,
    required this.rideType,
    required this.riderTier,
    required this.pickupLocation,
    required this.destinationLocation,
    this.distance,
    this.duration,
    this.pricing,
    this.vehicleType,
    this.vehicle,
    this.driver,
    required this.createdAt,
    this.startedAt,
    this.completedAt,
    this.cancelledAt,
    this.metadata,
  });

  factory Ride.fromJson(Map<String, dynamic> json) {
    return Ride(
      id: json['id'].toString(),
      riderId: json['rider_id'].toString(),
      driverId: json['driver_id']?.toString(),
      status: json['status'],
      rideType: json['ride_type'] ?? 'normal',
      riderTier: json['rider_tier'] ?? 'NORMAL',
      pickupLocation: Location.fromJson(json['pickup_location'] ?? {}),
      destinationLocation: Location.fromJson(
        json['destination_location'] ?? {},
      ),
      distance: json['distance']?.toDouble(),
      duration: json['duration']?.toDouble(),
      pricing: json['pricing'] != null
          ? RidePricing.fromJson(json['pricing'])
          : null,
      vehicleType: json['vehicle_type'],
      vehicle: json['vehicle'] != null
          ? Vehicle.fromJson(json['vehicle'])
          : null,
      driver: json['driver'] != null ? Driver.fromJson(json['driver']) : null,
      createdAt: DateTime.parse(json['created_at']),
      startedAt: json['started_at'] != null
          ? DateTime.parse(json['started_at'])
          : null,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'])
          : null,
      cancelledAt: json['cancelled_at'] != null
          ? DateTime.parse(json['cancelled_at'])
          : null,
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'rider_id': riderId,
      'driver_id': driverId,
      'status': status,
      'ride_type': rideType,
      'rider_tier': riderTier,
      'pickup_location': pickupLocation.toJson(),
      'destination_location': destinationLocation.toJson(),
      'distance': distance,
      'duration': duration,
      'pricing': pricing?.toJson(),
      'vehicle_type': vehicleType,
      'vehicle': vehicle?.toJson(),
      'driver': driver?.toJson(),
      'created_at': createdAt.toIso8601String(),
      'started_at': startedAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'cancelled_at': cancelledAt?.toIso8601String(),
      'metadata': metadata,
    };
  }

  bool get isCompleted => status == 'completed';
  bool get isCancelled => status.contains('cancelled');
  bool get isInProgress => status == 'in_progress';
  bool get isWaitingForDriver =>
      status == 'driver_search' || status == 'requested';
}

class Location {
  final double latitude;
  final double longitude;
  final String address;
  final String? name;
  final String? placeId;

  Location({
    required this.latitude,
    required this.longitude,
    required this.address,
    this.name,
    this.placeId,
  });

  factory Location.fromJson(Map<String, dynamic> json) {
    return Location(
      latitude: (json['latitude'] ?? json['lat'] ?? 0.0).toDouble(),
      longitude: (json['longitude'] ?? json['lng'] ?? 0.0).toDouble(),
      address: json['address'] ?? '',
      name: json['name'],
      placeId: json['place_id'] ?? json['placeId'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'latitude': latitude,
      'longitude': longitude,
      'address': address,
      'name': name,
      'place_id': placeId,
    };
  }
}

class RidePricing {
  final double basePrice;
  final double distancePrice;
  final double timePrice;
  final double surgeFee;
  final double platformFee;
  final double totalPrice;
  final String currency;

  RidePricing({
    required this.basePrice,
    required this.distancePrice,
    required this.timePrice,
    required this.surgeFee,
    required this.platformFee,
    required this.totalPrice,
    this.currency = 'NGN',
  });

  factory RidePricing.fromJson(Map<String, dynamic> json) {
    return RidePricing(
      basePrice: (json['base_price'] ?? 0.0).toDouble(),
      distancePrice: (json['distance_price'] ?? 0.0).toDouble(),
      timePrice: (json['time_price'] ?? 0.0).toDouble(),
      surgeFee: (json['surge_fee'] ?? 0.0).toDouble(),
      platformFee: (json['platform_fee'] ?? 0.0).toDouble(),
      totalPrice: (json['total_price'] ?? json['total'] ?? 0.0).toDouble(),
      currency: json['currency'] ?? 'NGN',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'base_price': basePrice,
      'distance_price': distancePrice,
      'time_price': timePrice,
      'surge_fee': surgeFee,
      'platform_fee': platformFee,
      'total_price': totalPrice,
      'currency': currency,
    };
  }
}

class Vehicle {
  final String id;
  final String make;
  final String model;
  final int year;
  final String color;
  final String plateNumber;
  final String vehicleType;
  final String category;
  final bool isActive;

  Vehicle({
    required this.id,
    required this.make,
    required this.model,
    required this.year,
    required this.color,
    required this.plateNumber,
    required this.vehicleType,
    required this.category,
    this.isActive = true,
  });

  factory Vehicle.fromJson(Map<String, dynamic> json) {
    return Vehicle(
      id: json['id'].toString(),
      make: json['make'] ?? '',
      model: json['model'] ?? '',
      year: json['year'] ?? 0,
      color: json['color'] ?? '',
      plateNumber: json['plate_number'] ?? json['license_plate'] ?? '',
      vehicleType: json['vehicle_type'] ?? '',
      category: json['category'] ?? '',
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'make': make,
      'model': model,
      'year': year,
      'color': color,
      'plate_number': plateNumber,
      'vehicle_type': vehicleType,
      'category': category,
      'is_active': isActive,
    };
  }

  String get displayName => '$make $model ($year)';
}

class Driver {
  final String id;
  final String firstName;
  final String lastName;
  final String? phoneNumber;
  final String? profilePicture;
  final double rating;
  final int totalRides;
  final String status;
  final Location? currentLocation;
  final String driverType;

  Driver({
    required this.id,
    required this.firstName,
    required this.lastName,
    this.phoneNumber,
    this.profilePicture,
    this.rating = 0.0,
    this.totalRides = 0,
    this.status = 'offline',
    this.currentLocation,
    this.driverType = 'independent_driver',
  });

  factory Driver.fromJson(Map<String, dynamic> json) {
    return Driver(
      id: json['id'].toString(),
      firstName: json['first_name'] ?? json['firstName'] ?? '',
      lastName: json['last_name'] ?? json['lastName'] ?? '',
      phoneNumber: json['phone_number'] ?? json['phoneNumber'],
      profilePicture: json['profile_picture'] ?? json['profilePicture'],
      rating: (json['rating'] ?? 0.0).toDouble(),
      totalRides: json['total_rides'] ?? json['totalRides'] ?? 0,
      status: json['status'] ?? 'offline',
      currentLocation: json['current_location'] != null
          ? Location.fromJson(json['current_location'])
          : null,
      driverType:
          json['driver_type'] ?? json['driverType'] ?? 'independent_driver',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'first_name': firstName,
      'last_name': lastName,
      'phone_number': phoneNumber,
      'profile_picture': profilePicture,
      'rating': rating,
      'total_rides': totalRides,
      'status': status,
      'current_location': currentLocation?.toJson(),
      'driver_type': driverType,
    };
  }

  String get fullName => '$firstName $lastName';
  bool get isOnline => status == 'online';
  bool get isAvailable => status == 'available';
}
