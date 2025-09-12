import 'package:flutter/material.dart';

class LeasedDriverRidesScreen extends StatefulWidget {
  const LeasedDriverRidesScreen({super.key});

  @override
  State<LeasedDriverRidesScreen> createState() =>
      _LeasedDriverRidesScreenState();
}

class _LeasedDriverRidesScreenState extends State<LeasedDriverRidesScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final bool _isLoading = false;

  // Mock data for demonstration
  final List<Map<String, dynamic>> _availableRides = [
    {
      'id': 'ride_001',
      'pickup': 'Lekki Phase 1, Lagos',
      'dropoff': 'Ajah, Lagos',
      'fare': 4200.0,
      'distance': '8.1 km',
      'duration': '22 mins',
      'client': 'Sarah M.',
      'payment': 'wallet',
      'pickupTime': '2025-09-12 15:00',
    },
    {
      'id': 'ride_002',
      'pickup': 'Ikeja GRA, Lagos',
      'dropoff': 'Maryland, Lagos',
      'fare': 3500.0,
      'distance': '5.2 km',
      'duration': '15 mins',
      'client': 'John D.',
      'payment': 'card',
      'pickupTime': '2025-09-12 16:30',
    },
  ];

  final List<Map<String, dynamic>> _activeRides = [
    {
      'id': 'ride_003',
      'pickup': 'Victoria Island, Lagos',
      'dropoff': 'Ikoyi, Lagos',
      'fare': 5000.0,
      'distance': '6.0 km',
      'duration': '18 mins',
      'client': 'Adaeze O.',
      'payment': 'cash',
      'pickupTime': '2025-09-12 17:00',
      'status': 'en_route',
    },
  ];

  final List<Map<String, dynamic>> _completedRides = [
    {
      'id': 'ride_004',
      'pickup': 'Yaba, Lagos',
      'dropoff': 'Surulere, Lagos',
      'fare': 2200.0,
      'distance': '3.8 km',
      'duration': '10 mins',
      'client': 'Chinedu K.',
      'payment': 'wallet',
      'pickupTime': '2025-09-11 14:00',
      'completedTime': '2025-09-11 14:15',
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Leased Driver Rides'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Available'),
            Tab(text: 'Active'),
            Tab(text: 'Completed'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildAvailableRides(),
          _buildActiveRides(),
          _buildCompletedRides(),
        ],
      ),
    );
  }

  Widget _buildAvailableRides() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_availableRides.isEmpty) {
      return const Center(child: Text('No available rides at the moment.'));
    }
    return ListView.builder(
      itemCount: _availableRides.length,
      itemBuilder: (context, index) {
        final ride = _availableRides[index];
        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: ListTile(
            leading: const Icon(Icons.directions_car, color: Colors.blue),
            title: Text('${ride['pickup']} → ${ride['dropoff']}'),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Client: ${ride['client']}'),
                Text('Fare: ₦${ride['fare']}'),
                Text(
                  'Distance: ${ride['distance']} | Duration: ${ride['duration']}',
                ),
                Text('Pickup: ${ride['pickupTime']}'),
                Text('Payment: ${ride['payment']}'),
              ],
            ),
            trailing: ElevatedButton(
              onPressed: () {
                // Accept ride logic here
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Accepted ride ${ride['id']}')),
                );
              },
              child: const Text('Accept'),
            ),
          ),
        );
      },
    );
  }

  Widget _buildActiveRides() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_activeRides.isEmpty) {
      return const Center(child: Text('No active rides.'));
    }
    return ListView.builder(
      itemCount: _activeRides.length,
      itemBuilder: (context, index) {
        final ride = _activeRides[index];
        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: ListTile(
            leading: const Icon(Icons.navigation, color: Colors.green),
            title: Text('${ride['pickup']} → ${ride['dropoff']}'),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Client: ${ride['client']}'),
                Text('Fare: ₦${ride['fare']}'),
                Text(
                  'Distance: ${ride['distance']} | Duration: ${ride['duration']}',
                ),
                Text('Pickup: ${ride['pickupTime']}'),
                Text('Payment: ${ride['payment']}'),
                Text('Status: ${ride['status']}'),
              ],
            ),
            trailing: ElevatedButton(
              onPressed: () {
                // Complete ride logic here
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Completed ride ${ride['id']}')),
                );
              },
              child: const Text('Complete'),
            ),
          ),
        );
      },
    );
  }

  Widget _buildCompletedRides() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_completedRides.isEmpty) {
      return const Center(child: Text('No completed rides.'));
    }
    return ListView.builder(
      itemCount: _completedRides.length,
      itemBuilder: (context, index) {
        final ride = _completedRides[index];
        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: ListTile(
            leading: const Icon(Icons.check_circle, color: Colors.grey),
            title: Text('${ride['pickup']} → ${ride['dropoff']}'),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Client: ${ride['client']}'),
                Text('Fare: ₦${ride['fare']}'),
                Text(
                  'Distance: ${ride['distance']} | Duration: ${ride['duration']}',
                ),
                Text('Pickup: ${ride['pickupTime']}'),
                Text('Completed: ${ride['completedTime']}'),
                Text('Payment: ${ride['payment']}'),
              ],
            ),
          ),
        );
      },
    );
  }
}
