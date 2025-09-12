import 'package:flutter/material.dart';
import '../../../services/api_service.dart';
import '../../../services/ride_service.dart';
import '../../../services/driver_service.dart';
import '../../../models/ride_models.dart';

class FleetDriverRidesScreen extends StatefulWidget {
  const FleetDriverRidesScreen({super.key});

  @override
  State<FleetDriverRidesScreen> createState() => _FleetDriverRidesScreenState();
}

class _FleetDriverRidesScreenState extends State<FleetDriverRidesScreen>
    with SingleTickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  final RideService _rideService = RideService();
  final DriverService _driverService = DriverService();

  late TabController _tabController;

  List<Ride> _availableRides = [];
  Ride? _activeRide;
  List<Ride> _rideHistory = [];

  bool _isLoading = false;

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
      // Load real rides data from backend APIs
      final availableRidesFuture = _rideService.getNearbyDrivers(
        0,
        0,
        'all',
      ); // Get available rides for drivers
      final activeRidesFuture = _rideService.getActiveRides();
      final historyFuture = _rideService.getRideHistory();

      final results = await Future.wait([
        _getAvailableRides(),
        activeRidesFuture,
        historyFuture,
      ]);

      setState(() {
        _availableRides = results[0];
        final activeRides = results[1];
        _activeRide = activeRides.isNotEmpty ? activeRides.first : null;
        _rideHistory = results[2];
        _isLoading = false;
      });
    } catch (e) {
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

  Future<List<Ride>> _getAvailableRides() async {
    try {
      final response = await _apiService.get(
        '/api/v1/rides/matching/matching/active_offers/',
      );

      if (response.statusCode == 200) {
        final List<dynamic> ridesData = response.data['results'] ?? [];
        return ridesData.map((data) => Ride.fromJson(data)).toList();
      }
    } catch (e) {
      print('Failed to get available rides: $e');
    }
    return [];
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
          labelColor: Colors.orange[600],
          unselectedLabelColor: Colors.grey,
          indicatorColor: Colors.orange[600],
          tabs: const [
            Tab(text: 'Available'),
            Tab(text: 'Active'),
            Tab(text: 'History'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildAvailableRides(),
                _buildActiveRide(),
                _buildRideHistory(),
              ],
            ),
    );
  }

  Widget _buildAvailableRides() {
    return RefreshIndicator(
      onRefresh: _loadRidesData,
      child: _availableRides.isEmpty
          ? _buildEmptyState(
              'No available rides',
              'New ride requests will appear here',
              Icons.local_taxi_outlined,
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _availableRides.length,
              itemBuilder: (context, index) {
                return _buildAvailableRideCard(_availableRides[index]);
              },
            ),
    );
  }

  Widget _buildActiveRide() {
    return RefreshIndicator(
      onRefresh: _loadRidesData,
      child: _activeRide == null
          ? _buildEmptyState(
              'No active ride',
              'Accept a ride request to start earning',
              Icons.radio_button_unchecked,
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: _buildActiveRideCard(_activeRide!),
            ),
    );
  }

  Widget _buildRideHistory() {
    return RefreshIndicator(
      onRefresh: _loadRidesData,
      child: _rideHistory.isEmpty
          ? _buildEmptyState(
              'No ride history',
              'Completed rides will appear here',
              Icons.history,
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _rideHistory.length,
              itemBuilder: (context, index) {
                return _buildHistoryRideCard(_rideHistory[index]);
              },
            ),
    );
  }

  Widget _buildEmptyState(String title, String subtitle, IconData icon) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            title,
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
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
    );
  }

  Widget _buildAvailableRideCard(Ride ride) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with tier and fare
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildTierChip(ride.serviceLevel),
                Text(
                  '₦${ride.estimatedFare?.toStringAsFixed(0) ?? ride.fare?.toStringAsFixed(0) ?? "0"}',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Route information
            Column(
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.radio_button_checked,
                      color: Colors.green[600],
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        ride.pickup.address,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                Container(
                  margin: const EdgeInsets.only(left: 8),
                  child: Column(
                    children: List.generate(
                      3,
                      (index) => Container(
                        margin: const EdgeInsets.symmetric(vertical: 1),
                        width: 2,
                        height: 4,
                        decoration: BoxDecoration(
                          color: Colors.grey[400],
                          borderRadius: BorderRadius.circular(1),
                        ),
                      ),
                    ),
                  ),
                ),
                Row(
                  children: [
                    Icon(Icons.location_on, color: Colors.red[600], size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        ride.destination.address,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Trip details
            Row(
              children: [
                Expanded(
                  child: _buildDetailItem(
                    Icons.straighten,
                    '${ride.distance?.toStringAsFixed(1) ?? "0"} km',
                  ),
                ),
                Expanded(
                  child: _buildDetailItem(
                    Icons.access_time,
                    '${ride.duration ?? ride.estimatedArrival ?? 0} min',
                  ),
                ),
                Expanded(
                  child: _buildDetailItem(
                    Icons.star,
                    ride.driverRating?.toStringAsFixed(1) ?? "N/A",
                  ),
                ),
              ],
            ),

            // Special requests
            if (ride.vipFeatures != null && ride.vipFeatures!.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue[200]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info, size: 16, color: Colors.blue[600]),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        ride.vipFeatures!.entries
                            .map((e) => '${e.key}: ${e.value}')
                            .join(', '),
                        style: TextStyle(fontSize: 12, color: Colors.blue[600]),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 16),

            // Action buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _declineRide(ride),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.grey[600],
                      side: BorderSide(color: Colors.grey[300]!),
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
                      backgroundColor: Colors.orange[600],
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Accept'),
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
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Active Ride',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                _buildStatusChip(ride.status),
              ],
            ),

            const SizedBox(height: 16),

            // Client information
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 24,
                    backgroundColor: Colors.blue[100],
                    child: Text(
                      'C', // Client initial placeholder
                      style: TextStyle(
                        color: Colors.blue[600],
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Client', // Client name placeholder
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Row(
                          children: [
                            Icon(
                              Icons.star,
                              size: 14,
                              color: Colors.amber[600],
                            ),
                            const SizedBox(width: 4),
                            Text(
                              ride.rating?.toStringAsFixed(1) ?? "N/A",
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () => _callClient('N/A'), // Phone placeholder
                    icon: const Icon(Icons.phone),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.green[100],
                      foregroundColor: Colors.green[600],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Route
            Column(
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.radio_button_checked,
                      color: Colors.green[600],
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        ride.pickup.address,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                Container(
                  margin: const EdgeInsets.only(left: 10),
                  child: Column(
                    children: List.generate(
                      4,
                      (index) => Container(
                        margin: const EdgeInsets.symmetric(vertical: 2),
                        width: 2,
                        height: 6,
                        decoration: BoxDecoration(
                          color: Colors.grey[400],
                          borderRadius: BorderRadius.circular(1),
                        ),
                      ),
                    ),
                  ),
                ),
                Row(
                  children: [
                    Icon(Icons.location_on, color: Colors.red[600], size: 20),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        ride.destination.address,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 20),

            // Trip info
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      Text(
                        '₦${ride.fare?.toStringAsFixed(0) ?? ride.estimatedFare?.toStringAsFixed(0) ?? "0"}',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange[600],
                        ),
                      ),
                      Text(
                        'Fare',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                  Column(
                    children: [
                      Text(
                        '${ride.distance?.toStringAsFixed(1) ?? "0"} km',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Distance',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                  Column(
                    children: [
                      Text(
                        '${ride.duration ?? ride.estimatedArrival ?? 0} min',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Duration',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Action buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _openNavigation,
                    icon: const Icon(Icons.navigation),
                    label: const Text('Navigate'),
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
                    onPressed: () => _completeRide(ride),
                    icon: const Icon(Icons.check_circle),
                    label: const Text('Complete'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green[600],
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
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
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with earnings and time
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '₦${ride.fare?.toStringAsFixed(0) ?? "0"}',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                    // Tips not available in current Ride model, skip for now
                  ],
                ),
                Text(
                  _formatTime(
                    ride.completedAt ?? ride.updatedAt ?? ride.createdAt,
                  ),
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Route
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ride.pickup.address,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(
                            Icons.arrow_downward,
                            size: 12,
                            color: Colors.grey[500],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '${ride.distance?.toStringAsFixed(1) ?? "0"} km • ${ride.duration ?? 0} min',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        ride.destination.address,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Column(
                  children: [
                    Row(
                      children: [
                        Icon(Icons.star, size: 14, color: Colors.amber[600]),
                        const SizedBox(width: 2),
                        Text(
                          ride.rating?.toStringAsFixed(1) ?? "N/A",
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                    Text(
                      'Client',
                      style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTierChip(String tier) {
    Color color;
    String label;

    switch (tier) {
      case 'vip':
        color = Colors.purple;
        label = 'VIP';
        break;
      case 'premium':
        color = Colors.orange;
        label = 'Premium';
        break;
      default:
        color = Colors.blue;
        label = 'Regular';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.green.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green.withOpacity(0.3)),
      ),
      child: Text(
        'In Progress',
        style: TextStyle(
          fontSize: 12,
          color: Colors.green[600],
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildDetailItem(IconData icon, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: Colors.grey[600]),
        const SizedBox(width: 4),
        Text(text, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  String _formatTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inMinutes}m ago';
    }
  }

  void _acceptRide(Ride ride) async {
    try {
      final success = await _driverService.acceptRide(ride.id);
      if (success) {
        setState(() {
          _activeRide = ride;
          _availableRides.remove(ride);
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Ride accepted successfully')),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to accept ride'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error accepting ride: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _declineRide(Ride ride) async {
    try {
      final success = await _driverService.declineRide(
        ride.id,
        'Driver declined',
      );
      if (success) {
        setState(() {
          _availableRides.remove(ride);
        });
        if (mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('Ride declined')));
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error declining ride: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _callClient(String phone) {
    // TODO: Make phone call
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('Calling $phone...')));
  }

  void _openNavigation() {
    // TODO: Open navigation
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Opening navigation...')));
  }

  void _completeRide(Ride ride) {
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
              // TODO: Complete ride via API
              setState(() {
                _activeRide = null;
                // Create completed ride copy
                final completedRide = ride.copyWith(
                  status: 'completed',
                  completedAt: DateTime.now(),
                  rating: 4.8,
                );
                _rideHistory.insert(0, completedRide);
              });
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Ride completed successfully')),
              );
            },
            child: const Text('Complete'),
          ),
        ],
      ),
    );
  }
}
