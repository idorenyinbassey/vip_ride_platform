import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart' as latlong;
import '../../../services/api_service.dart';
import '../../../services/location_service.dart';
import '../../../widgets/map/live_map_widget.dart';

class FleetDriverHomeScreen extends StatefulWidget {
  const FleetDriverHomeScreen({super.key});

  @override
  State<FleetDriverHomeScreen> createState() => _FleetDriverHomeScreenState();
}

class _FleetDriverHomeScreenState extends State<FleetDriverHomeScreen> {
  final ApiService _apiService = ApiService();
  final LocationService _locationService = LocationService();

  bool _isOnline = false;
  bool _isLoading = false;

  // Driver stats
  double _todayEarnings = 0.0;
  int _todayRides = 0;
  int _acceptanceRate = 0;
  double _currentRating = 0.0;

  // Fleet info
  Map<String, dynamic>? _fleetInfo;
  Map<String, dynamic>? _assignedVehicle;

  // Current location
  double? _currentLat;
  double? _currentLng;

  @override
  void initState() {
    super.initState();
    _loadDriverData();
    _loadFleetInfo();
  }

  Future<void> _loadDriverData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real driver data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _todayEarnings = 12800.0;
        _todayRides = 6;
        _acceptanceRate = 92;
        _currentRating = 4.8;
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading driver data: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _loadFleetInfo() async {
    try {
      // TODO: Load real fleet info from API
      await Future.delayed(const Duration(milliseconds: 500));

      setState(() {
        _fleetInfo = {
          'name': 'Lagos Premier Fleet',
          'manager': 'John Doe',
          'contact': '+234 803 456 7890',
          'total_vehicles': 25,
          'active_drivers': 18,
        };

        _assignedVehicle = {
          'plate_number': 'DEF-456-ZW',
          'make': 'Toyota',
          'model': 'Camry',
          'year': 2021,
          'color': 'Silver',
          'fuel_level': 75,
          'last_maintenance': '2024-02-01',
          'next_maintenance_due': '2024-05-01',
        };
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading fleet info: $e')));
    }
  }

  Future<void> _toggleOnlineStatus() async {
    if (!_isOnline) {
      // Going online - start location tracking
      final hasPermission = await _locationService.requestLocationPermission();
      if (!hasPermission) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Location permission required to go online'),
          ),
        );
        return;
      }

      final position = await _locationService.getCurrentLocation();
      if (position != null) {
        setState(() {
          _currentLat = position.latitude;
          _currentLng = position.longitude;
        });
      }
    }

    setState(() => _isOnline = !_isOnline);

    // TODO: Update online status via API
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(_isOnline ? 'You are now online' : 'You are now offline'),
        backgroundColor: _isOnline ? Colors.green : Colors.grey,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Fleet Driver'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: _showNotifications,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: () async {
                await _loadDriverData();
                await _loadFleetInfo();
              },
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Online status toggle
                    _buildOnlineStatusCard(),

                    const SizedBox(height: 24),

                    // Fleet information
                    if (_fleetInfo != null) _buildFleetInfoCard(),

                    const SizedBox(height: 24),

                    // Vehicle information
                    if (_assignedVehicle != null) _buildVehicleInfoCard(),

                    const SizedBox(height: 24),

                    // Today's stats
                    _buildTodayStatsCard(),

                    const SizedBox(height: 24),

                    // Map (if online)
                    if (_isOnline && _currentLat != null && _currentLng != null)
                      _buildMapCard(),

                    const SizedBox(height: 24),

                    // Quick actions
                    _buildQuickActionsCard(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildOnlineStatusCard() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: _isOnline
                ? [Colors.green[400]!, Colors.green[600]!]
                : [Colors.grey[400]!, Colors.grey[600]!],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _isOnline ? 'You\'re Online' : 'You\'re Offline',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _isOnline
                        ? 'Ready to accept ride requests'
                        : 'Tap to go online and start earning',
                    style: const TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                ],
              ),
            ),
            Switch(
              value: _isOnline,
              onChanged: (value) => _toggleOnlineStatus(),
              activeColor: Colors.white,
              activeTrackColor: Colors.green[300],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFleetInfoCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.business, color: Colors.blue[600]),
                const SizedBox(width: 8),
                const Text(
                  'Fleet Information',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildInfoRow('Fleet Name', _fleetInfo!['name']),
            const SizedBox(height: 8),
            _buildInfoRow('Manager', _fleetInfo!['manager']),
            const SizedBox(height: 8),
            _buildInfoRow('Contact', _fleetInfo!['contact']),
            const SizedBox(height: 8),
            _buildInfoRow('Total Vehicles', '${_fleetInfo!['total_vehicles']}'),
            const SizedBox(height: 8),
            _buildInfoRow('Active Drivers', '${_fleetInfo!['active_drivers']}'),
          ],
        ),
      ),
    );
  }

  Widget _buildVehicleInfoCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.directions_car, color: Colors.orange[600]),
                const SizedBox(width: 8),
                const Text(
                  'Assigned Vehicle',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _assignedVehicle!['plate_number'],
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${_assignedVehicle!['year']} ${_assignedVehicle!['make']} ${_assignedVehicle!['model']}',
                        style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.green[100],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${_assignedVehicle!['fuel_level']}% Fuel',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.green[600],
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildVehicleMetric(
                    'Color',
                    _assignedVehicle!['color'],
                  ),
                ),
                Expanded(
                  child: _buildVehicleMetric(
                    'Last Service',
                    _assignedVehicle!['last_maintenance'],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTodayStatsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Today\'s Performance',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Earnings',
                    '₦${_todayEarnings.toStringAsFixed(0)}',
                    Icons.monetization_on,
                    Colors.green,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Rides',
                    '$_todayRides',
                    Icons.local_taxi,
                    Colors.blue,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Rating',
                    '${_currentRating.toStringAsFixed(1)}',
                    Icons.star,
                    Colors.amber,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Acceptance',
                    '$_acceptanceRate%',
                    Icons.check_circle,
                    Colors.orange,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMapCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: SizedBox(
          height: 300,
          child: LiveMapWidget(
            currentLocation: latlong.LatLng(_currentLat!, _currentLng!),
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Quick Actions',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildActionButton(
                    'Contact Fleet',
                    Icons.phone,
                    Colors.blue,
                    _contactFleet,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildActionButton(
                    'Emergency',
                    Icons.emergency,
                    Colors.red,
                    _triggerSOS,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildActionButton(
                    'Report Issue',
                    Icons.report_problem,
                    Colors.orange,
                    _reportIssue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildActionButton(
                    'Navigation',
                    Icons.navigation,
                    Colors.green,
                    _openNavigation,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(fontSize: 14, color: Colors.grey[600])),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }

  Widget _buildVehicleMetric(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }

  Widget _buildStatItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
        ],
      ),
    );
  }

  Widget _buildActionButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onPressed,
  ) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      child: Column(
        children: [
          Icon(icon, size: 20),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  void _showNotifications() {
    // TODO: Show notifications
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Notifications feature coming soon')),
    );
  }

  void _contactFleet() {
    // TODO: Contact fleet manager
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Contacting fleet manager...')),
    );
  }

  void _triggerSOS() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Emergency SOS'),
        content: const Text(
          'This will alert fleet management and emergency services. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Trigger SOS alert
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Emergency alert sent'),
                  backgroundColor: Colors.red,
                ),
              );
            },
            child: const Text(
              'Send Alert',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

  void _reportIssue() {
    // TODO: Open issue reporting
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Issue reporting feature coming soon')),
    );
  }

  void _openNavigation() {
    // TODO: Open navigation app
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Opening navigation...')));
  }
}
