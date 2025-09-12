import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../services/api_service.dart';
import '../../../services/ride_service.dart';
import '../../../services/driver_service.dart';
import '../../../models/ride_models.dart';

class LeasedDriverRidesScreen extends StatefulWidget {
  const LeasedDriverRidesScreen({super.key});

  @override
  State<LeasedDriverRidesScreen> createState() =>
      _LeasedDriverRidesScreenState();
}

class _LeasedDriverRidesScreenState extends State<LeasedDriverRidesScreen>
    with TickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  final RideService _rideService = RideService();
  final DriverService _driverService = DriverService();

  late TabController _tabController;
  bool _isLoading = false;

  // Real ride data using proper models
  List<Ride> _availableRides = [];
  List<Ride> _activeRides = [];
  List<Ride> _completedRides = [];
  List<Ride> _activeRides = [];
  List<Ride> _rideHistory = [];

  // Active ride details
  Ride? _currentRide;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadRidesData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadRidesData() async {
    setState(() => _isLoading = true);

    try {
      // Load real rides data from API using DriverService
      final availableRides = await _driverService.getAvailableRides();
      final activeRides = await _driverService.getActiveRides();
      final completedRides = await _driverService.getRideHistory();

      setState(() {
        _availableRides = availableRides.cast<Ride>();
        _activeRides = activeRides.cast<Ride>();
        _completedRides = completedRides.cast<Ride>();
        _isLoading = false;
      });
    } catch (e) {
      print('Error loading rides data: $e');
      setState(() => _isLoading = false);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to load rides: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
          {
            'id': 'ride_002',
            'pickup_address': 'Lekki Phase 1, Lagos',
            'dropoff_address': 'Ajah, Lagos',
            'pickup_lat': 6.4474,
            'pickup_lng': 3.4739,
            'dropoff_lat': 6.4698,
            'dropoff_lng': 3.5650,
            'estimated_fare': 4200.0,
            'distance': '8.1 km',
            'duration': '22 mins',
            'client_rating': 4.6,
            'pickup_time': '2024-03-11 15:00',
            'ride_type': 'premium',
            'client_name': 'Sarah M.',
            'payment_method': 'wallet',
          },
        ];

        _activeRides = [
          {
            'id': 'ride_active_001',
            'pickup_address': 'Ikeja GRA, Lagos',
            'dropoff_address': 'Maryland, Lagos',
            'pickup_lat': 6.5952,
            'pickup_lng': 3.3384,
            'dropoff_lat': 6.5689,
            'dropoff_lng': 3.3736,
            'fare': 2800.0,
            'distance': '4.5 km',
            'client_name': 'Michael A.',
            'client_phone': '+234 803 123 4567',
            'client_rating': 4.9,
            'status': 'in_progress',
            'start_time': '2024-03-11 13:45',
            'payment_method': 'cash',
            'ride_type': 'standard',
          },
        ];

        _rideHistory = [
          {
            'id': 'ride_hist_001',
            'pickup_address': 'Surulere, Lagos',
            'dropoff_address': 'Yaba, Lagos',
            'fare': 2200.0,
            'driver_share': 1540.0, // 70% of fare
            'distance': '3.8 km',
            'duration': '18 mins',
            'client_name': 'David O.',
            'client_rating': 4.7,
            'ride_rating': 5.0,
            'completion_time': '2024-03-11 12:30',
            'payment_method': 'card',
            'ride_type': 'standard',
          },
          {
            'id': 'ride_hist_002',
            'pickup_address': 'Banana Island, Lagos',
            'dropoff_address': 'VI, Lagos',
            'fare': 4500.0,
            'driver_share': 3150.0, // 70% of fare
            'distance': '6.2 km',
            'duration': '25 mins',
            'client_name': 'Grace L.',
            'client_rating': 4.8,
            'ride_rating': 4.8,
            'completion_time': '2024-03-11 11:15',
            'payment_method': 'wallet',
            'ride_type': 'premium',
          },
        ];

        if (_activeRides.isNotEmpty) {
          _currentRide = _activeRides.first;
        }
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading rides: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Rides'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.blue[600],
          unselectedLabelColor: Colors.grey[600],
          indicatorColor: Colors.blue[600],
          tabs: [
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.radio_button_unchecked, size: 16),
                  const SizedBox(width: 4),
                  Text('Available (${_availableRides.length})'),
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.drive_eta, size: 16),
                  const SizedBox(width: 4),
                  Text('Active (${_activeRides.length})'),
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.history, size: 16),
                  const SizedBox(width: 4),
                  Text('History (${_rideHistory.length})'),
                ],
              ),
            ),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildAvailableRidesTab(),
                _buildActiveRidesTab(),
                _buildHistoryTab(),
              ],
            ),
    );
  }

  Widget _buildAvailableRidesTab() {
    return RefreshIndicator(
      onRefresh: _loadRidesData,
      child: _availableRides.isEmpty
          ? _buildEmptyState(
              'No available rides',
              'Pull to refresh or wait for new ride requests',
              Icons.radio_button_unchecked,
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _availableRides.length,
              itemBuilder: (context, index) {
                final ride = _availableRides[index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: _buildAvailableRideCard(ride),
                );
              },
            ),
    );
  }

  Widget _buildActiveRidesTab() {
    return RefreshIndicator(
      onRefresh: _loadRidesData,
      child: _activeRides.isEmpty
          ? _buildEmptyState(
              'No active rides',
              'Accept a ride request to start earning',
              Icons.drive_eta,
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  if (_currentRide != null) ...[
                    _buildActiveRideCard(_currentRide!),
                    const SizedBox(height: 16),
                    _buildRideMap(),
                    const SizedBox(height: 16),
                    _buildRideActions(),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildHistoryTab() {
    return RefreshIndicator(
      onRefresh: _loadRidesData,
      child: _rideHistory.isEmpty
          ? _buildEmptyState(
              'No ride history',
              'Complete rides will appear here',
              Icons.history,
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _rideHistory.length,
              itemBuilder: (context, index) {
                final ride = _rideHistory[index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: _buildHistoryRideCard(ride),
                );
              },
            ),
    );
  }

  Widget _buildAvailableRideCard(Ride ride) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Ride header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.green[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(Icons.location_on, color: Colors.green[600]),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ride['pickup_address'],
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      Row(
                        children: [
                          Icon(
                            Icons.arrow_downward,
                            size: 16,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              ride['dropoff_address'],
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                // Fare highlight
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.blue[100],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '₦${ride['estimated_fare'].toStringAsFixed(0)}',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue[600],
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Ride details
            Row(
              children: [
                Expanded(
                  child: _buildRideDetailItem(
                    Icons.straighten,
                    'Distance',
                    ride['distance'],
                  ),
                ),
                Expanded(
                  child: _buildRideDetailItem(
                    Icons.access_time,
                    'Duration',
                    ride['duration'],
                  ),
                ),
                Expanded(
                  child: _buildRideDetailItem(
                    Icons.star,
                    'Client Rating',
                    '${ride['client_rating']}⭐',
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Client info
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 16,
                    backgroundColor: Colors.blue[100],
                    child: Text(
                      ride['client_name'][0],
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.blue[600],
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          ride['client_name'],
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          '${ride['ride_type']} • ${ride['payment_method']}',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    'Pickup: ${ride['pickup_time'].split(' ')[1]}',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Action buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _declineRide(ride['id']),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red[600],
                      side: BorderSide(color: Colors.red[300]!),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Text('Decline'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: ElevatedButton(
                    onPressed: () => _acceptRide(ride),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green[600],
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    child: const Text('Accept Ride'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActiveRideCard(Ride ride) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [Colors.blue[400]!, Colors.blue[600]!],
          ),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'RIDE IN PROGRESS',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
                const Spacer(),
                Text(
                  '₦${ride['fare'].toStringAsFixed(0)}',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Trip details
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.radio_button_checked,
                        color: Colors.green[300],
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          ride['pickup_address'],
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.location_on, color: Colors.red[300], size: 16),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          ride['dropoff_address'],
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Client info
            Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: Colors.white.withOpacity(0.2),
                  child: Text(
                    ride['client_name'][0],
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ride['client_name'],
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        '${ride['client_rating']}⭐ • ${ride['payment_method']}',
                        style: TextStyle(fontSize: 12, color: Colors.white70),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: () => _callClient(ride['client_phone']),
                  icon: const Icon(Icons.phone, color: Colors.white),
                  style: IconButton.styleFrom(
                    backgroundColor: Colors.white.withOpacity(0.2),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryRideCard(Ride ride) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with earnings
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ride['pickup_address'],
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      Row(
                        children: [
                          Icon(
                            Icons.arrow_downward,
                            size: 12,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              ride['dropoff_address'],
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '₦${ride['driver_share'].toStringAsFixed(0)}',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.green[600],
                      ),
                    ),
                    Text(
                      'Your share (70%)',
                      style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                    ),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Trip stats
            Row(
              children: [
                Expanded(
                  child: _buildHistoryDetailItem(
                    Icons.straighten,
                    ride['distance'],
                  ),
                ),
                Expanded(
                  child: _buildHistoryDetailItem(
                    Icons.access_time,
                    ride['duration'],
                  ),
                ),
                Expanded(
                  child: _buildHistoryDetailItem(
                    Icons.star,
                    '${ride['ride_rating']}⭐',
                  ),
                ),
                Expanded(
                  child: _buildHistoryDetailItem(
                    Icons.payment,
                    ride['payment_method'],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Bottom info
            Row(
              children: [
                Text(
                  ride['client_name'],
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                const Spacer(),
                Text(
                  ride['completion_time'].split(' ')[0], // Date only
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                const SizedBox(width: 8),
                Text(
                  ride['completion_time'].split(' ')[1], // Time only
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRideMap() {
    if (_currentRide == null) return const SizedBox.shrink();

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        height: 250,
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(12)),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: FlutterMap(
            options: MapOptions(
              center: LatLng(
                _currentRide!['pickup_lat'],
                _currentRide!['pickup_lng'],
              ),
              zoom: 13.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.example.app',
              ),
              MarkerLayer(
                markers: [
                  // Pickup marker
                  Marker(
                    point: LatLng(
                      _currentRide!['pickup_lat'],
                      _currentRide!['pickup_lng'],
                    ),
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.green[600],
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 3),
                      ),
                      child: const Icon(
                        Icons.location_on,
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                  ),
                  // Dropoff marker
                  Marker(
                    point: LatLng(
                      _currentRide!['dropoff_lat'],
                      _currentRide!['dropoff_lng'],
                    ),
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.red[600],
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 3),
                      ),
                      child: const Icon(
                        Icons.flag,
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRideActions() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              'Ride Actions',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _openNavigation(),
                    icon: const Icon(Icons.navigation),
                    label: const Text('Navigation'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue[600],
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _callClient(_currentRide!['client_phone']),
                    icon: const Icon(Icons.phone),
                    label: const Text('Call Client'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green[600],
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _completeRide(),
                icon: const Icon(Icons.check_circle),
                label: const Text('Complete Ride'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange[600],
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),

            const SizedBox(height: 8),

            TextButton.icon(
              onPressed: () => _reportIssue(),
              icon: Icon(Icons.report_problem, color: Colors.red[600]),
              label: Text(
                'Report Issue',
                style: TextStyle(color: Colors.red[600]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRideDetailItem(IconData icon, String label, String value) {
    return Column(
      children: [
        Icon(icon, size: 16, color: Colors.grey[600]),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
          textAlign: TextAlign.center,
        ),
        Text(
          label,
          style: TextStyle(fontSize: 10, color: Colors.grey[600]),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildHistoryDetailItem(IconData icon, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: 12, color: Colors.grey[600]),
        const SizedBox(width: 4),
        Text(value, style: TextStyle(fontSize: 10, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildEmptyState(String title, String subtitle, IconData icon) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              title,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              subtitle,
              style: TextStyle(fontSize: 14, color: Colors.grey[500]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  void _acceptRide(Map<String, dynamic> ride) {
    setState(() {
      _availableRides.removeWhere((r) => r['id'] == ride['id']);
      _activeRides.add({
        ...ride,
        'status': 'accepted',
        'start_time': DateTime.now().toString(),
      });
      _currentRide = _activeRides.last;
    });

    _tabController.animateTo(1); // Switch to Active tab

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Ride accepted! Navigate to pickup location.'),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _declineRide(String rideId) {
    setState(() {
      _availableRides.removeWhere((ride) => ride['id'] == rideId);
    });

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Ride declined')));
  }

  void _openNavigation() {
    // TODO: Open navigation app
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Opening navigation...')));
  }

  void _callClient(String phoneNumber) {
    // TODO: Make phone call
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('Calling $phoneNumber...')));
  }

  void _completeRide() {
    if (_currentRide == null) return;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Complete Ride'),
        content: const Text('Mark this ride as completed?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);

              // Move ride to history
              setState(() {
                final completedRide = {
                  ..._currentRide!,
                  'completion_time': DateTime.now().toString(),
                  'driver_share': _currentRide!['fare'] * 0.7, // 70% to driver
                  'ride_rating': 4.8,
                };

                _rideHistory.insert(0, completedRide);
                _activeRides.clear();
                _currentRide = null;
              });

              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Ride completed successfully!'),
                  backgroundColor: Colors.green,
                ),
              );

              _tabController.animateTo(2); // Switch to History tab
            },
            child: const Text('Complete'),
          ),
        ],
      ),
    );
  }

  void _reportIssue() {
    // TODO: Report issue functionality
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Report issue feature coming soon')),
    );
  }
}
