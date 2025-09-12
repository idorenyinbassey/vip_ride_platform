import 'package:flutter/material.dart';
import '../../../services/api_service.dart';
import '../../../services/ride_service.dart';
import '../../../models/ride_models.dart';

class IndependentDriverRidesScreen extends StatefulWidget {
  const IndependentDriverRidesScreen({super.key});

  @override
  State<IndependentDriverRidesScreen> createState() =>
      _IndependentDriverRidesScreenState();
}

class _IndependentDriverRidesScreenState
    extends State<IndependentDriverRidesScreen>
    with TickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  final RideService _rideService = RideService();
  late TabController _tabController;

  List<Ride> _availableRides = [];
  List<Ride> _acceptedRides = [];
  List<Ride> _completedRides = [];
  Ride? _activeRide;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadRides();
  }

  Future<void> _loadRides() async {
    setState(() => _isLoading = true);

    try {
      // Load available rides for drivers (pending rides in the area)
      final availableRides = await _rideService.getActiveRides();

      // Load ride history for this driver
      final rideHistory = await _rideService.getRideHistory();

      setState(() {
        _availableRides = availableRides
            .where(
              (ride) =>
                  ride.status == 'pending' || ride.status == 'driver_requested',
            )
            .toList();

        _completedRides = rideHistory
            .where((ride) => ride.status == 'completed')
            .toList();

        _acceptedRides = availableRides
            .where(
              (ride) =>
                  ride.status == 'accepted' ||
                  ride.status == 'driver_en_route' ||
                  ride.status == 'driver_arrived' ||
                  ride.status == 'in_progress',
            )
            .toList();
      });
    } catch (e) {
      debugPrint('❌ Failed to load rides: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error loading rides: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _acceptRide(Ride ride) async {
    try {
      // Call API to accept ride - will need driver accept endpoint
      final response = await _apiService.post(
        '/api/v1/rides/workflow/${ride.id}/accept/',
        data: {'driver_id': 'current_driver_id'}, // Will get from auth context
      );

      if (response.statusCode == 200) {
        await _loadRides(); // Reload to get updated ride status

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Ride accepted! Navigate to pickup location.'),
            backgroundColor: Colors.green,
          ),
        );

        // Switch to active ride tab
        _tabController.animateTo(1);
      } else {
        throw Exception('Failed to accept ride');
      }
    } catch (e) {
      debugPrint('❌ Failed to accept ride: $e');
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error accepting ride: $e')));
    }
  }

  Future<void> _declineRide(Ride ride) async {
    try {
      // Call API to decline ride
      final response = await _apiService.post(
        '/api/v1/rides/workflow/${ride.id}/decline/',
        data: {'driver_id': 'current_driver_id'}, // Will get from auth context
      );

      if (response.statusCode == 200) {
        await _loadRides(); // Reload to remove declined ride

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Ride declined'),
            backgroundColor: Colors.orange,
          ),
        );
      } else {
        throw Exception('Failed to decline ride');
      }
    } catch (e) {
      debugPrint('❌ Failed to decline ride: $e');
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error declining ride: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Driver Rides'),
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
              text: 'Available (${_availableRides.length})',
              icon: const Icon(Icons.search, size: 16),
            ),
            Tab(
              text: 'Active (${_activeRide != null ? 1 : 0})',
              icon: const Icon(Icons.directions_car, size: 16),
            ),
            Tab(
              text: 'Accepted (${_acceptedRides.length})',
              icon: const Icon(Icons.check_circle, size: 16),
            ),
            Tab(
              text: 'History (${_completedRides.length})',
              icon: const Icon(Icons.history, size: 16),
            ),
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
                _buildAcceptedRides(),
                _buildRideHistory(),
              ],
            ),
    );
  }

  Widget _buildAvailableRides() {
    if (_availableRides.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No available rides',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
            SizedBox(height: 8),
            Text(
              'Make sure you\'re online to receive ride requests',
              style: TextStyle(fontSize: 14, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadRides,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _availableRides.length,
        itemBuilder: (context, index) {
          final ride = _availableRides[index];
          return _buildAvailableRideCard(ride);
        },
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
            // Ride header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '₦${ride.fare?.toStringAsFixed(0) ?? ride.estimatedFare?.toStringAsFixed(0) ?? "0"}',
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.blue[100],
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    ride.vehicleType.toUpperCase(),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.blue[700],
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Route info
            Row(
              children: [
                Column(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: Colors.green,
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ),
                    Container(width: 2, height: 30, color: Colors.grey[300]),
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: Colors.red,
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ),
                  ],
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ride.pickup.address,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        ride.destination.address,
                        style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Trip details
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildTripDetail(
                  Icons.straighten,
                  '${ride.distance?.toStringAsFixed(1) ?? "0"} km',
                  'Distance',
                ),
                _buildTripDetail(
                  Icons.access_time,
                  '${ride.duration ?? 0} min',
                  'Duration',
                ),
                _buildTripDetail(
                  Icons.schedule,
                  '${DateTime.now().difference(ride.createdAt).inMinutes}m ago',
                  'Requested',
                ),
              ],
            ),

            const SizedBox(height: 20),

            // Action buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _declineRide(ride),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red,
                      side: const BorderSide(color: Colors.red),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text('Decline'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => _acceptRide(ride),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
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

  Widget _buildTripDetail(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, size: 20, color: Colors.grey[600]),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildActiveRide() {
    if (_activeRide == null) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.directions_car_outlined, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No active ride',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
            SizedBox(height: 8),
            Text(
              'Accept a ride to start driving',
              style: TextStyle(fontSize: 14, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Active ride card
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text(
                    'Active Ride - ₦${_activeRide!.fare?.toStringAsFixed(0) ?? _activeRide!.estimatedFare?.toStringAsFixed(0) ?? "0"}',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 20),
                  // Route display
                  // TODO: Add full active ride management UI
                  const Text('Active ride management UI will be here'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAcceptedRides() {
    if (_acceptedRides.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle_outline, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No accepted rides',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _acceptedRides.length,
      itemBuilder: (context, index) {
        final ride = _acceptedRides[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          child: ListTile(
            title: Text(
              '₦${ride.fare?.toStringAsFixed(0) ?? ride.estimatedFare?.toStringAsFixed(0) ?? "0"}',
            ),
            subtitle: Text(
              '${ride.pickup.address} → ${ride.destination.address}',
            ),
            trailing: const Icon(Icons.check_circle, color: Colors.green),
          ),
        );
      },
    );
  }

  Widget _buildRideHistory() {
    if (_completedRides.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No completed rides',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _completedRides.length,
      itemBuilder: (context, index) {
        final ride = _completedRides[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          child: ListTile(
            title: Text(
              '₦${ride.fare?.toStringAsFixed(0) ?? ride.estimatedFare?.toStringAsFixed(0) ?? "0"}',
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('${ride.pickup.address} → ${ride.destination.address}'),
                Text(
                  'Completed: ${ride.completedAt?.toString().split('.')[0]}',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
            trailing: const Icon(Icons.check_circle, color: Colors.green),
            isThreeLine: true,
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
}
