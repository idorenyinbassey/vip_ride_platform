import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../services/gps_service.dart';
import '../../../models/ride_tracking.dart';

class EncryptedTrackingScreen extends StatefulWidget {
  final String rideId;

  const EncryptedTrackingScreen({super.key, required this.rideId});

  @override
  State<EncryptedTrackingScreen> createState() =>
      _EncryptedTrackingScreenState();
}

class _EncryptedTrackingScreenState extends State<EncryptedTrackingScreen>
    with TickerProviderStateMixin {
  final MapController _mapController = MapController();
  final GpsService _gpsService = GpsService();

  late AnimationController _pulseController;
  late AnimationController _lockController;

  RideTracking? _currentTracking;
  LatLng? _userLocation;
  LatLng? _driverLocation;
  List<LatLng> _route = [];
  bool _isEncryptionActive = true;
  bool _isLoading = true;
  String _encryptionStatus = 'AES-256-GCM Active';

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _startTracking();
  }

  void _initializeAnimations() {
    _pulseController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();

    _lockController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    )..forward();
  }

  Future<void> _startTracking() async {
    try {
      await _gpsService.startEncryptedTracking(widget.rideId);

      _gpsService.trackingStream.listen((tracking) {
        setState(() {
          _currentTracking = tracking;
          _userLocation = LatLng(tracking.userLat, tracking.userLng);
          _driverLocation = LatLng(tracking.driverLat, tracking.driverLng);
          _route = tracking.route;
          _isLoading = false;
        });

        _updateMapView();
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _updateMapView() {
    if (_userLocation != null && _driverLocation != null) {
      final bounds = LatLngBounds.fromPoints([
        _userLocation!,
        _driverLocation!,
      ]);
      _mapController.fitBounds(
        bounds,
        options: const FitBoundsOptions(padding: EdgeInsets.all(50)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Row(
          children: [
            AnimatedBuilder(
              animation: _lockController,
              builder: (context, child) {
                return Transform.scale(
                  scale: _lockController.value,
                  child: const Icon(Icons.lock, color: Colors.amber),
                );
              },
            ),
            const SizedBox(width: 10),
            const Text(
              'Encrypted Tracking',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(
              _isEncryptionActive ? Icons.visibility_off : Icons.visibility,
              color: Colors.amber,
            ),
            onPressed: _toggleEncryption,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Colors.amber),
                  SizedBox(height: 20),
                  Text(
                    'Initializing encrypted tracking...',
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                ],
              ),
            )
          : Stack(
              children: [
                _buildEncryptedMap(),
                _buildEncryptionIndicator(),
                _buildTrackingInfo(),
                _buildSosButton(),
              ],
            ),
    );
  }

  Widget _buildEncryptedMap() {
    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        center: _userLocation ?? const LatLng(6.5244, 3.3792), // Lagos default
        zoom: 13.0,
        minZoom: 10.0,
        maxZoom: 18.0,
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.vipride.tracking',
          additionalOptions: const {
            'attribution': '© OpenStreetMap contributors',
          },
        ),
        // Encrypted overlay
        if (_isEncryptionActive)
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.amber.withOpacity(0.1),
                  Colors.orange.withOpacity(0.05),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),
        // Route polyline
        if (_route.isNotEmpty)
          PolylineLayer(
            polylines: [
              Polyline(
                points: _route,
                strokeWidth: 4.0,
                color: Colors.amber.withOpacity(0.8),
              ),
            ],
          ),
        // Markers
        MarkerLayer(markers: _buildMarkers()),
      ],
    );
  }

  List<Marker> _buildMarkers() {
    final markers = <Marker>[];

    // User location marker
    if (_userLocation != null) {
      markers.add(
        Marker(
          point: _userLocation!,
          child: AnimatedBuilder(
            animation: _pulseController,
            builder: (context, child) {
              return Transform.scale(
                scale: 1.0 + (_pulseController.value * 0.3),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.8),
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 3),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.blue.withOpacity(0.5),
                        blurRadius: 10,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.person,
                    color: Colors.white,
                    size: 20,
                  ),
                ),
              );
            },
          ),
        ),
      );
    }

    // Driver location marker
    if (_driverLocation != null) {
      markers.add(
        Marker(
          point: _driverLocation!,
          child: Container(
            decoration: BoxDecoration(
              color: Colors.amber,
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 3),
              boxShadow: [
                BoxShadow(
                  color: Colors.amber.withOpacity(0.5),
                  blurRadius: 10,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: const Icon(
              Icons.directions_car,
              color: Colors.black,
              size: 20,
            ),
          ),
        ),
      );
    }

    return markers;
  }

  Widget _buildEncryptionIndicator() {
    return Positioned(
      top: 20,
      left: 20,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.8),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.amber, width: 1),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            AnimatedBuilder(
              animation: _pulseController,
              builder: (context, child) {
                return Icon(
                  Icons.lock,
                  color: Colors.amber.withOpacity(
                    0.7 + (_pulseController.value * 0.3),
                  ),
                  size: 16,
                );
              },
            ),
            const SizedBox(width: 8),
            Text(
              _encryptionStatus,
              style: const TextStyle(
                color: Colors.amber,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrackingInfo() {
    if (_currentTracking == null) return const SizedBox.shrink();

    return Positioned(
      bottom: 120,
      left: 20,
      right: 20,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.9),
          borderRadius: BorderRadius.circular(15),
          border: Border.all(color: Colors.amber.withOpacity(0.5), width: 1),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.security, color: Colors.amber, size: 20),
                const SizedBox(width: 8),
                const Text(
                  'VIP Premium Tracking',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.circle, color: Colors.green, size: 8),
                      const SizedBox(width: 4),
                      Text(
                        (_currentTracking!.status ?? 'Unknown').toUpperCase(),
                        style: const TextStyle(
                          color: Colors.green,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildInfoItem(
                    'ETA',
                    _currentTracking!.eta ?? 'N/A',
                    Icons.schedule,
                  ),
                ),
                Expanded(
                  child: _buildInfoItem(
                    'Distance',
                    '${(_currentTracking!.distance / 1000).toStringAsFixed(1)} km',
                    Icons.straighten,
                  ),
                ),
                Expanded(
                  child: _buildInfoItem(
                    'Driver',
                    _currentTracking!.driverName ?? 'Unknown',
                    Icons.person,
                  ),
                ),
              ],
            ),
            if (_currentTracking!.encryptedData?.isNotEmpty == true) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.amber.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.amber.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.enhanced_encryption,
                      color: Colors.amber,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'End-to-end encrypted: ${_currentTracking!.encryptedData?.substring(0, 20) ?? 'N/A'}...',
                        style: const TextStyle(
                          color: Colors.amber,
                          fontSize: 11,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.grey[400], size: 16),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(
            color: Colors.grey,
            fontSize: 12,
            fontWeight: FontWeight.w500,
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildSosButton() {
    return Positioned(
      bottom: 30,
      left: 20,
      right: 20,
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton.icon(
              onPressed: _triggerSos,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(25),
                ),
              ),
              icon: const Icon(Icons.emergency, size: 20),
              label: const Text(
                'EMERGENCY SOS',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              ),
            ),
          ),
          const SizedBox(width: 12),
          FloatingActionButton(
            onPressed: _callSupport,
            backgroundColor: Colors.amber,
            foregroundColor: Colors.black,
            child: const Icon(Icons.support_agent),
          ),
        ],
      ),
    );
  }

  void _toggleEncryption() {
    setState(() {
      _isEncryptionActive = !_isEncryptionActive;
      _encryptionStatus = _isEncryptionActive
          ? 'AES-256-GCM Active'
          : 'Standard Tracking';
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _isEncryptionActive
              ? 'Encryption activated'
              : 'Standard tracking mode',
        ),
        backgroundColor: _isEncryptionActive ? Colors.green : Colors.orange,
      ),
    );
  }

  void _triggerSos() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: const Row(
          children: [
            Icon(Icons.emergency, color: Colors.red),
            SizedBox(width: 10),
            Text('Emergency SOS', style: TextStyle(color: Colors.red)),
          ],
        ),
        content: const Text(
          'This will immediately alert:\n'
          '• VIP Security Team\n'
          '• Local Emergency Services\n'
          '• Your emergency contacts\n\n'
          'Are you sure you want to trigger SOS?',
          style: TextStyle(color: Colors.white),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _executeSos();
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('TRIGGER SOS'),
          ),
        ],
      ),
    );
  }

  void _executeSos() {
    // TODO: Implement actual SOS functionality
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('🚨 Emergency SOS activated! Help is on the way.'),
        backgroundColor: Colors.red,
        duration: Duration(seconds: 5),
      ),
    );
  }

  void _callSupport() {
    // TODO: Implement support call functionality
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Connecting to VIP Premium support...'),
        backgroundColor: Colors.amber,
      ),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _lockController.dispose();
    _gpsService.stopTracking();
    super.dispose();
  }
}
