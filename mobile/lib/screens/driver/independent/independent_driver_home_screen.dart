import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart' as geo;
import '../../../services/api_service.dart';
import '../../../services/location_service.dart';
import '../../../models/ride_models.dart';
import '../../../widgets/map/live_map_widget.dart';

class IndependentDriverHomeScreen extends StatefulWidget {
  const IndependentDriverHomeScreen({super.key});

  @override
  State<IndependentDriverHomeScreen> createState() =>
      _IndependentDriverHomeScreenState();
}

class _IndependentDriverHomeScreenState
    extends State<IndependentDriverHomeScreen> {
  final ApiService _apiService = ApiService();
  final LocationService _locationService = LocationService();

  bool _isOnline = false;
  bool _isLoading = false;
  final List<Ride> _nearbyRides = [];
  geo.LatLng? _currentLocation;

  // Driver stats
  int _todayRides = 0;
  double _todayEarnings = 0.0;
  double _rating = 4.8;

  @override
  void initState() {
    super.initState();
    _initializeDriver();
  }

  Future<void> _initializeDriver() async {
    setState(() => _isLoading = true);

    try {
      // Get current location
      final position = await _locationService.getCurrentLocation();
      if (position != null) {
        setState(() {
          _currentLocation = geo.LatLng(position.latitude, position.longitude);
        });
      }

      // Load driver stats
      await _loadDriverStats();

      // Start location tracking if online
      if (_isOnline) {
        await _locationService.startLocationTracking();
      }
    } catch (e) {
      print('Error initializing driver: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _loadDriverStats() async {
    try {
      // TODO: Implement driver stats API call
      setState(() {
        _todayRides = 12;
        _todayEarnings = 15650.00;
        _rating = 4.8;
      });
    } catch (e) {
      print('Error loading driver stats: $e');
    }
  }

  Future<void> _toggleOnlineStatus() async {
    setState(() => _isLoading = true);

    try {
      if (!_isOnline) {
        // Going online
        bool locationPermission = await _locationService
            .requestLocationPermission();
        if (!locationPermission) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Location permission required to go online'),
            ),
          );
          return;
        }

        await _locationService.startLocationTracking();
        // TODO: Call API to set driver status online
        setState(() => _isOnline = true);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('You are now online and ready to receive rides'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        // Going offline
        _locationService.stopLocationTracking();
        // TODO: Call API to set driver status offline
        setState(() => _isOnline = false);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('You are now offline'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                children: [
                  // Status Header
                  _buildStatusHeader(),

                  // Online/Offline Toggle
                  _buildOnlineToggle(),

                  // Today's Stats
                  _buildTodayStats(),

                  // Map with current location
                  Expanded(child: _buildDriverMap()),

                  // Quick Actions
                  _buildQuickActions(),
                ],
              ),
      ),
    );
  }

  Widget _buildStatusHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _isOnline ? Colors.green[600] : Colors.grey[600],
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 2)),
        ],
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 25,
            backgroundColor: Colors.white,
            child: Icon(
              _isOnline ? Icons.directions_car : Icons.local_taxi,
              color: _isOnline ? Colors.green[600] : Colors.grey[600],
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _isOnline ? 'You\'re Online' : 'You\'re Offline',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  _isOnline ? 'Ready to receive rides' : 'Tap to go online',
                  style: const TextStyle(color: Colors.white70, fontSize: 14),
                ),
              ],
            ),
          ),
          Icon(
            _isOnline ? Icons.check_circle : Icons.radio_button_unchecked,
            color: Colors.white,
            size: 24,
          ),
        ],
      ),
    );
  }

  Widget _buildOnlineToggle() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: SizedBox(
        width: double.infinity,
        height: 50,
        child: ElevatedButton(
          onPressed: _isLoading ? null : _toggleOnlineStatus,
          style: ElevatedButton.styleFrom(
            backgroundColor: _isOnline ? Colors.red[600] : Colors.green[600],
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: Text(
            _isOnline ? 'Go Offline' : 'Go Online',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTodayStats() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          _buildStatCard('Rides', _todayRides.toString(), Icons.directions_car),
          const SizedBox(width: 12),
          _buildStatCard(
            'Earnings',
            '₦${_todayEarnings.toStringAsFixed(0)}',
            Icons.attach_money,
          ),
          const SizedBox(width: 12),
          _buildStatCard('Rating', _rating.toStringAsFixed(1), Icons.star),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8),
          boxShadow: const [
            BoxShadow(
              color: Colors.black12,
              blurRadius: 4,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Icon(icon, color: Colors.blue[600], size: 24),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            Text(
              title,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDriverMap() {
    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 2)),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: LiveMapWidget(
          currentLocation: _currentLocation,
          nearbyDrivers: const [], // Driver doesn't need to see other drivers
        ),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          _buildActionButton(
            'SOS',
            Icons.emergency,
            Colors.red,
            () => _triggerSOS(),
          ),
          const SizedBox(width: 12),
          _buildActionButton(
            'Support',
            Icons.support_agent,
            Colors.blue,
            () => _openSupport(),
          ),
          const SizedBox(width: 12),
          _buildActionButton(
            'Navigation',
            Icons.navigation,
            Colors.green,
            () => _openNavigation(),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: Column(
            children: [
              Icon(icon, color: color, size: 24),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _triggerSOS() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Emergency SOS'),
        content: const Text(
          'This will alert the security desk and emergency services. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Implement SOS API call
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Emergency alert sent'),
                  backgroundColor: Colors.red,
                ),
              );
            },
            child: const Text('Send SOS'),
          ),
        ],
      ),
    );
  }

  void _openSupport() {
    // TODO: Implement support screen navigation
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Support feature coming soon')),
    );
  }

  void _openNavigation() {
    // TODO: Implement navigation to active ride destination
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('No active ride to navigate to')),
    );
  }

  @override
  void dispose() {
    _locationService.stopLocationTracking();
    super.dispose();
  }
}
