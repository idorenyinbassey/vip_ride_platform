import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../models/ride_models.dart';

class LiveMapWidget extends StatelessWidget {
  final MapController controller;
  final LatLng? currentLocation;
  final LatLng? pickupLocation;
  final LatLng? destinationLocation;
  final List<Driver> nearbyDrivers;
  final Ride? activeRide;
  final bool isLoading;

  const LiveMapWidget({
    super.key,
    required this.controller,
    this.currentLocation,
    this.pickupLocation,
    this.destinationLocation,
    this.nearbyDrivers = const [],
    this.activeRide,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Container(
        color: Colors.grey[200],
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Loading map...'),
            ],
          ),
        ),
      );
    }

    return FlutterMap(
      mapController: controller,
      options: MapOptions(
        center:
            currentLocation ?? const LatLng(6.5244, 3.3792), // Lagos default
        zoom: 16.0,
        minZoom: 10.0,
        maxZoom: 20.0,
        interactiveFlags: InteractiveFlag.all,
      ),
      children: [
        // Map tiles
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.vipride.app',
          maxZoom: 20,
        ),

        // Markers
        MarkerLayer(markers: _buildMarkers()),

        // Route polyline (if we have pickup and destination)
        if (pickupLocation != null && destinationLocation != null)
          PolylineLayer(
            polylines: [
              Polyline(
                points: [pickupLocation!, destinationLocation!],
                strokeWidth: 4.0,
                color: Colors.blue.withOpacity(0.7),
                isDotted: true,
              ),
            ],
          ),
      ],
    );
  }

  List<Marker> _buildMarkers() {
    final markers = <Marker>[];

    // Current location marker
    if (currentLocation != null) {
      markers.add(
        Marker(
          point: currentLocation!,
          child: Container(
            decoration: BoxDecoration(
              color: Colors.blue,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 3),
              boxShadow: const [
                BoxShadow(
                  color: Colors.black26,
                  blurRadius: 4,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: const Icon(Icons.my_location, color: Colors.white, size: 16),
          ),
          width: 32,
          height: 32,
        ),
      );
    }

    // Pickup location marker
    if (pickupLocation != null) {
      markers.add(
        Marker(
          point: pickupLocation!,
          child: Container(
            decoration: BoxDecoration(
              color: Colors.green,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
              boxShadow: const [
                BoxShadow(
                  color: Colors.black26,
                  blurRadius: 4,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: const Icon(Icons.location_on, color: Colors.white, size: 20),
          ),
          width: 36,
          height: 36,
        ),
      );
    }

    // Destination location marker
    if (destinationLocation != null) {
      markers.add(
        Marker(
          point: destinationLocation!,
          child: Container(
            decoration: BoxDecoration(
              color: Colors.red,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
              boxShadow: const [
                BoxShadow(
                  color: Colors.black26,
                  blurRadius: 4,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: const Icon(Icons.flag, color: Colors.white, size: 20),
          ),
          width: 36,
          height: 36,
        ),
      );
    }

    // Nearby drivers markers
    for (final driver in nearbyDrivers) {
      markers.add(
        Marker(
          point: LatLng(driver.latitude, driver.longitude),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.8),
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
            ),
            child: const Icon(
              Icons.directions_car,
              color: Colors.white,
              size: 16,
            ),
          ),
          width: 30,
          height: 30,
        ),
      );
    }

    return markers;
  }

  IconData _getVehicleIcon(String vehicleType) {
    switch (vehicleType.toLowerCase()) {
      case 'economy':
        return Icons.directions_car;
      case 'standard':
        return Icons.local_taxi;
      case 'premium':
        return Icons.car_rental;
      case 'suv':
        return Icons.airport_shuttle;
      default:
        return Icons.directions_car;
    }
  }

  void _showDriverInfo(BuildContext context, Driver driver) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Handle bar
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),

            // Driver info
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: Colors.blue[100],
                  child: Text(
                    driver.name.substring(0, 1).toUpperCase(),
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue[700],
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        driver.name,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Row(
                        children: [
                          Icon(Icons.star, size: 16, color: Colors.amber[600]),
                          const SizedBox(width: 4),
                          Text(
                            driver.rating.toStringAsFixed(1),
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                      Text(
                        '${driver.vehicleModel} • ${driver.vehiclePlate}',
                        style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Distance and ETA
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildInfoCard(
                  icon: Icons.location_on,
                  title: 'Distance',
                  value: '${driver.distance.toStringAsFixed(1)} km',
                ),
                _buildInfoCard(
                  icon: Icons.access_time,
                  title: 'ETA',
                  value: '${driver.eta} min',
                ),
                _buildInfoCard(
                  icon: Icons.directions_car,
                  title: 'Vehicle',
                  value: driver.vehicleType.toUpperCase(),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard({
    required IconData icon,
    required String title,
    required String value,
  }) {
    return Column(
      children: [
        Icon(icon, size: 24, color: Colors.grey[600]),
        const SizedBox(height: 4),
        Text(title, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }
}
