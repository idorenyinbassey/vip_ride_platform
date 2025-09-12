import 'package:flutter/material.dart';
import '../../../services/api_service.dart';
import '../../../models/ride_models.dart';

class FleetOwnerDashboardScreen extends StatefulWidget {
  const FleetOwnerDashboardScreen({super.key});

  @override
  State<FleetOwnerDashboardScreen> createState() =>
      _FleetOwnerDashboardScreenState();
}

class _FleetOwnerDashboardScreenState extends State<FleetOwnerDashboardScreen> {
  final ApiService _apiService = ApiService();

  // Fleet statistics
  int _totalVehicles = 0;
  int _activeDrivers = 0;
  int _onlineVehicles = 0;
  double _todayEarnings = 0.0;
  double _monthlyEarnings = 0.0;

  // Recent activity
  List<Map<String, dynamic>> _recentActivity = [];

  // Top performers
  List<Map<String, dynamic>> _topDrivers = [];
  List<Map<String, dynamic>> _topVehicles = [];

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real fleet data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _totalVehicles = 25;
        _activeDrivers = 18;
        _onlineVehicles = 12;
        _todayEarnings = 245650.0;
        _monthlyEarnings = 5892400.0;

        _recentActivity = [
          {
            'type': 'ride_completed',
            'driver': 'James Okafor',
            'vehicle': 'ABC-123-XY',
            'amount': 3200,
            'time': '2 mins ago',
          },
          {
            'type': 'driver_online',
            'driver': 'Sarah Ahmed',
            'vehicle': 'DEF-456-ZW',
            'time': '5 mins ago',
          },
          {
            'type': 'maintenance_due',
            'vehicle': 'GHI-789-UV',
            'message': 'Service due in 3 days',
            'time': '1 hour ago',
          },
        ];

        _topDrivers = [
          {
            'name': 'James Okafor',
            'earnings': 28500,
            'rides': 45,
            'rating': 4.9,
          },
          {
            'name': 'Sarah Ahmed',
            'earnings': 26200,
            'rides': 42,
            'rating': 4.8,
          },
          {'name': 'Peter Eze', 'earnings': 24800, 'rides': 38, 'rating': 4.7},
        ];

        _topVehicles = [
          {
            'plate': 'ABC-123-XY',
            'model': '2020 Honda Accord',
            'earnings': 35000,
            'trips': 65,
          },
          {
            'plate': 'DEF-456-ZW',
            'model': '2021 Toyota Camry',
            'earnings': 32500,
            'trips': 58,
          },
          {
            'plate': 'GHI-789-UV',
            'model': '2019 Hyundai Elantra',
            'earnings': 28900,
            'trips': 52,
          },
        ];
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading dashboard: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Fleet Dashboard'),
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
              onRefresh: _loadDashboardData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Welcome header
                    _buildWelcomeHeader(),

                    const SizedBox(height: 24),

                    // Fleet statistics
                    _buildFleetStats(),

                    const SizedBox(height: 24),

                    // Earnings overview
                    _buildEarningsOverview(),

                    const SizedBox(height: 24),

                    // Recent activity
                    _buildRecentActivity(),

                    const SizedBox(height: 24),

                    // Top performers
                    _buildTopPerformers(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildWelcomeHeader() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [Colors.orange[400]!, Colors.orange[600]!],
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
                  const Text(
                    'Good Morning!',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Fleet Owner Dashboard',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '$_onlineVehicles of $_totalVehicles vehicles online',
                    style: const TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                ],
              ),
            ),
            const Icon(Icons.local_shipping, color: Colors.white, size: 48),
          ],
        ),
      ),
    );
  }

  Widget _buildFleetStats() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Total Vehicles',
            _totalVehicles.toString(),
            Icons.directions_car,
            Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Active Drivers',
            _activeDrivers.toString(),
            Icons.people,
            Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            'Online Now',
            _onlineVehicles.toString(),
            Icons.online_prediction,
            Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              title,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEarningsOverview() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Earnings Overview',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Today',
                        style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                      ),
                      Text(
                        '₦${_todayEarnings.toStringAsFixed(0)}',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.green,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'This Month',
                        style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                      ),
                      Text(
                        '₦${_monthlyEarnings.toStringAsFixed(0)}',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _viewDetailedEarnings,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange[600],
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text('View Detailed Earnings'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivity() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Recent Activity',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                TextButton(
                  onPressed: _viewAllActivity,
                  child: const Text('View All'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _recentActivity.length,
              separatorBuilder: (context, index) => const Divider(),
              itemBuilder: (context, index) {
                final activity = _recentActivity[index];
                return _buildActivityItem(activity);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityItem(Map<String, dynamic> activity) {
    IconData icon;
    Color color;
    String title;
    String subtitle;

    switch (activity['type']) {
      case 'ride_completed':
        icon = Icons.check_circle;
        color = Colors.green;
        title = 'Ride Completed - ₦${activity['amount']}';
        subtitle = '${activity['driver']} • ${activity['vehicle']}';
        break;
      case 'driver_online':
        icon = Icons.online_prediction;
        color = Colors.blue;
        title = 'Driver Came Online';
        subtitle = '${activity['driver']} • ${activity['vehicle']}';
        break;
      case 'maintenance_due':
        icon = Icons.warning;
        color = Colors.orange;
        title = 'Maintenance Alert';
        subtitle = '${activity['vehicle']} • ${activity['message']}';
        break;
      default:
        icon = Icons.info;
        color = Colors.grey;
        title = 'Activity';
        subtitle = '';
    }

    return ListTile(
      leading: CircleAvatar(
        backgroundColor: color.withOpacity(0.1),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(
        title,
        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
      ),
      subtitle: Text(
        subtitle,
        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
      ),
      trailing: Text(
        activity['time'],
        style: TextStyle(fontSize: 12, color: Colors.grey[500]),
      ),
      contentPadding: EdgeInsets.zero,
    );
  }

  Widget _buildTopPerformers() {
    return Column(
      children: [
        // Top Drivers
        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Top Drivers This Month',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _topDrivers.length,
                  separatorBuilder: (context, index) =>
                      const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final driver = _topDrivers[index];
                    return _buildDriverRankItem(driver, index + 1);
                  },
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Top Vehicles
        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Top Vehicles This Month',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _topVehicles.length,
                  separatorBuilder: (context, index) =>
                      const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final vehicle = _topVehicles[index];
                    return _buildVehicleRankItem(vehicle, index + 1);
                  },
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDriverRankItem(Map<String, dynamic> driver, int rank) {
    return Row(
      children: [
        CircleAvatar(
          radius: 16,
          backgroundColor: _getRankColor(rank),
          child: Text(
            rank.toString(),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                driver['name'],
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Row(
                children: [
                  Icon(Icons.star, size: 14, color: Colors.amber[600]),
                  const SizedBox(width: 4),
                  Text(
                    '${driver['rating']} • ${driver['rides']} rides',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ],
          ),
        ),
        Text(
          '₦${driver['earnings']}',
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
      ],
    );
  }

  Widget _buildVehicleRankItem(Map<String, dynamic> vehicle, int rank) {
    return Row(
      children: [
        CircleAvatar(
          radius: 16,
          backgroundColor: _getRankColor(rank),
          child: Text(
            rank.toString(),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                vehicle['plate'],
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                '${vehicle['model']} • ${vehicle['trips']} trips',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ),
        Text(
          '₦${vehicle['earnings']}',
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
      ],
    );
  }

  Color _getRankColor(int rank) {
    switch (rank) {
      case 1:
        return Colors.amber[600]!;
      case 2:
        return Colors.grey[400]!;
      case 3:
        return Colors.brown[400]!;
      default:
        return Colors.blue[400]!;
    }
  }

  void _showNotifications() {
    // TODO: Show notifications screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Notifications feature coming soon')),
    );
  }

  void _viewDetailedEarnings() {
    // Navigate to earnings tab
    // TODO: This would be handled by parent widget
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Navigate to earnings screen')),
    );
  }

  void _viewAllActivity() {
    // TODO: Show all activity screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Activity history feature coming soon')),
    );
  }
}
