import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart' as geo;

class LiveMapWidget extends StatelessWidget {
  final geo.LatLng? currentLocation;
  final geo.LatLng? pickupLocation;
  final geo.LatLng? destinationLocation;
  final List<geo.LatLng>? route;
  final MapController? mapController;
  final Function(geo.LatLng)? onTap;

  const LiveMapWidget({
    super.key,
    this.currentLocation,
    this.pickupLocation,
    this.destinationLocation,
    this.route,
    this.mapController,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return FlutterMap(
      mapController: mapController,
      options: MapOptions(
        initialCenter: currentLocation ?? const geo.LatLng(6.5244, 3.3792),
        initialZoom: 13.0,
        onTap: onTap != null ? (_, point) => onTap!(point) : null,
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.example.vip_ride_app',
        ),
        if (route != null && route!.isNotEmpty)
          PolylineLayer(
            polylines: [
              Polyline(points: route!, strokeWidth: 4.0, color: Colors.blue),
            ],
          ),
        MarkerLayer(
          markers: [
            if (currentLocation != null)
              Marker(
                point: currentLocation!,
                child: const Icon(
                  Icons.my_location,
                  color: Colors.blue,
                  size: 30,
                ),
              ),
            if (pickupLocation != null)
              Marker(
                point: pickupLocation!,
                child: const Icon(
                  Icons.location_on,
                  color: Colors.green,
                  size: 30,
                ),
              ),
            if (destinationLocation != null)
              Marker(
                point: destinationLocation!,
                child: const Icon(Icons.flag, color: Colors.red, size: 30),
              ),
          ],
        ),
      ],
    );
  }
}
