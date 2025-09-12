import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../models/ride_models.dart';

class LiveMapWidget extends StatelessWidget {
  final LatLng? currentLocation;
  final LatLng? pickupLocation;
  final LatLng? destinationLocation;
  final List<Driver> nearbyDrivers;
  final bool showNearbyDrivers;
  final bool showTraffic;
  final double zoom;
  final Function(LatLng)? onLocationTap;

  const LiveMapWidget({
    super.key,
    this.currentLocation,
    this.pickupLocation,
    this.destinationLocation,
    this.nearbyDrivers = const [],
    this.showNearbyDrivers = true,
    this.showTraffic = false,
    this.zoom = 15.0,
    this.onLocationTap,
  });

  @override
  Widget build(BuildContext context) {
    return FlutterMap(
      options: MapOptions(
        initialCenter:
            currentLocation ??
            pickupLocation ??
            const LatLng(6.4581, 3.3947), // Lagos default
        initialZoom: zoom,
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.all,
        ),
        onTap: onLocationTap != null
            ? (_, latLng) => onLocationTap!(latLng)
            : null,
      ),
      children: [
        // Tile layer
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.vipride.app',
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
    if (showNearbyDrivers) {
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
    }

    return markers;
  }
}
