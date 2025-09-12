import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../services/api_service.dart';

class LeasedDriverHomeScreen extends StatefulWidget {
  const LeasedDriverHomeScreen({super.key});

  @override
  State<LeasedDriverHomeScreen> createState() => _LeasedDriverHomeScreenState();
}

class _LeasedDriverHomeScreenState extends State<LeasedDriverHomeScreen> {
  final ApiService _apiService = ApiService();

  bool _isOnline = false;
  bool _isLoading = false;

  // Driver information
  Map<String, dynamic> _driverInfo = {};
  Map<String, dynamic> _leaseInfo = {};
  Map<String, dynamic> _vehicleInfo = {};
  Map<String, dynamic> _todayStats = {};

  @override
  void initState() {
    super.initState();
    _loadHomeData();
  }

  Future<void> _loadHomeData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _driverInfo = {
          'name': 'Michael Johnson',
          'rating': 4.7,
          'total_rides': 156,
          'status': 'active',
        };

        _leaseInfo = {
          'lessor_name': 'Elite Vehicle Leasing',
          'lessor_contact': '+234 803 555 7777',
          'daily_fee': 15000.0,
          'revenue_split': 70.0, // Driver gets 70%
          'lease_start': '2024-01-15',
          'lease_end': '2024-07-15',
          'days_remaining': 45,
          'payment_status': 'current',
          'payment_due_date': '2024-03-15',
        };

        _vehicleInfo = {
          'plate_number': 'GHI-789-XY',
          'make': 'Honda',
          'model': 'Accord',
          'year': 2022,
          'color': 'Black',
          'fuel_level': 75,
          'last_maintenance': '2024-01-20',
          'insurance_status': 'active',
        };

        _todayStats = {
          'rides_completed': 8,
          'gross_earnings': 25000.0,
          'driver_share': 17500.0, // 70% of gross
          'daily_fee_paid': 15000.0,
          'net_earnings': 2500.0, // driver_share - daily_fee
          'hours_online': 6.5,
          'avg_rating': 4.8,
        };
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading data: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('Leased Driver Dashboard'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            icon: Icon(
              _isOnline ? Icons.location_on : Icons.location_off,
              color: _isOnline ? Colors.green : Colors.grey,
            ),
            onPressed: _toggleOnlineStatus,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadHomeData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Online status toggle
                    _buildOnlineStatusCard(),

                    const SizedBox(height: 16),

                    // Lease information
                    _buildLeaseInfoCard(),

                    const SizedBox(height: 16),

                    // Today's earnings summary
                    _buildEarningsSummaryCard(),

                    const SizedBox(height: 16),

                    // Vehicle information
                    _buildVehicleInfoCard(),

                    const SizedBox(height: 16),

                    // Performance metrics
                    _buildPerformanceCard(),

                    const SizedBox(height: 16),

                    // Map view
                    _buildMapCard(),

                    const SizedBox(height: 16),

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
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: _isOnline
                ? [Colors.green[400]!, Colors.green[600]!]
                : [Colors.grey[400]!, Colors.grey[600]!],
          ),
        ),
        padding: const EdgeInsets.all(24),
        child: Row(
          children: [
            Icon(
              _isOnline
                  ? Icons.radio_button_checked
                  : Icons.radio_button_unchecked,
              color: Colors.white,
              size: 32,
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
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    _isOnline
                        ? 'Ready to receive ride requests'
                        : 'Tap to start receiving requests',
                    style: const TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                ],
              ),
            ),
            Switch(
              value: _isOnline,
              onChanged: (value) => _toggleOnlineStatus(),
              activeThumbColor: Colors.white,
              activeTrackColor: Colors.green[300],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLeaseInfoCard() {
    final daysRemaining = _leaseInfo['days_remaining'] ?? 0;
    final isNearExpiry = daysRemaining <= 30;

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
                Icon(Icons.assignment, color: Colors.purple[600]),
                const SizedBox(width: 8),
                const Text(
                  'Lease Agreement',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: _leaseInfo['payment_status'] == 'current'
                        ? Colors.green[100]
                        : Colors.red[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _leaseInfo['payment_status']?.toString().toUpperCase() ??
                        'UNKNOWN',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: _leaseInfo['payment_status'] == 'current'
                          ? Colors.green[600]
                          : Colors.red[600],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Lessor info
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.purple[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _leaseInfo['lessor_name'] ?? 'Unknown Lessor',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _leaseInfo['lessor_contact'] ?? 'No contact',
                    style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Lease terms
            Row(
              children: [
                Expanded(
                  child: _buildLeaseMetric(
                    'Daily Fee',
                    '₦${(_leaseInfo['daily_fee'] ?? 0).toStringAsFixed(0)}',
                    Icons.money,
                    Colors.orange,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildLeaseMetric(
                    'Revenue Split',
                    '${_leaseInfo['revenue_split'] ?? 0}%',
                    Icons.pie_chart,
                    Colors.blue,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Lease expiry warning
            if (isNearExpiry)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange[300]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.warning, color: Colors.orange[600], size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Lease expires in $daysRemaining days. Contact lessor to renew.',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.orange[600],
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildEarningsSummaryCard() {
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
                Icon(Icons.account_balance_wallet, color: Colors.green[600]),
                const SizedBox(width: 8),
                const Text(
                  'Today\'s Earnings',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Net earnings highlight
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.monetization_on,
                    color: Colors.green[600],
                    size: 32,
                  ),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '₦${(_todayStats['net_earnings'] ?? 0).toStringAsFixed(0)}',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.green[600],
                        ),
                      ),
                      Text(
                        'Net Earnings (After Daily Fee)',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.green[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Earnings breakdown
            Row(
              children: [
                Expanded(
                  child: _buildEarningsMetric(
                    'Gross Earnings',
                    '₦${(_todayStats['gross_earnings'] ?? 0).toStringAsFixed(0)}',
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildEarningsMetric(
                    'Your Share (${_leaseInfo['revenue_split']}%)',
                    '₦${(_todayStats['driver_share'] ?? 0).toStringAsFixed(0)}',
                    Colors.purple,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _buildEarningsMetric(
                    'Daily Fee',
                    '-₦${(_todayStats['daily_fee_paid'] ?? 0).toStringAsFixed(0)}',
                    Colors.orange,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildEarningsMetric(
                    'Rides Completed',
                    '${_todayStats['rides_completed'] ?? 0}',
                    Colors.indigo,
                  ),
                ),
              ],
            ),
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
                  'Leased Vehicle',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Vehicle header
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.directions_car,
                    size: 40,
                    color: Colors.orange[600],
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _vehicleInfo['plate_number'] ?? 'N/A',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          '${_vehicleInfo['year']} ${_vehicleInfo['make']} ${_vehicleInfo['model']}',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Fuel level indicator
                  Column(
                    children: [
                      Icon(Icons.local_gas_station, color: Colors.orange[600]),
                      Text(
                        '${_vehicleInfo['fuel_level'] ?? 0}%',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceCard() {
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
                Icon(Icons.trending_up, color: Colors.blue[600]),
                const SizedBox(width: 8),
                const Text(
                  'Performance Today',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: _buildPerformanceMetric(
                    'Hours Online',
                    '${_todayStats['hours_online'] ?? 0}h',
                    Icons.access_time,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildPerformanceMetric(
                    'Avg Rating',
                    '${_todayStats['avg_rating'] ?? 0.0}⭐',
                    Icons.star,
                    Colors.amber,
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
      child: Container(
        height: 200,
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(12)),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: FlutterMap(
            options: MapOptions(
              initialCenter: LatLng(6.5244, 3.3792), // Lagos coordinates
              initialZoom: 12.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.example.app',
              ),
              MarkerLayer(
                markers: [
                  Marker(
                    point: LatLng(6.5244, 3.3792),
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.blue[600],
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 3),
                      ),
                      child: const Icon(
                        Icons.person_pin_circle,
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
                  child: _buildQuickActionButton(
                    'Contact Lessor',
                    Icons.phone,
                    Colors.blue,
                    _contactLessor,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildQuickActionButton(
                    'View Lease Terms',
                    Icons.description,
                    Colors.purple,
                    _viewLeaseTerms,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _buildQuickActionButton(
                    'Report Issue',
                    Icons.report_problem,
                    Colors.orange,
                    _reportIssue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildQuickActionButton(
                    'Emergency SOS',
                    Icons.emergency,
                    Colors.red,
                    _triggerEmergency,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLeaseMetric(
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
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(fontSize: 10, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildEarningsMetric(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(label, style: TextStyle(fontSize: 10, color: Colors.grey[600])),
        ],
      ),
    );
  }

  Widget _buildPerformanceMetric(
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
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                Text(
                  label,
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionButton(
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

  void _toggleOnlineStatus() {
    setState(() {
      _isOnline = !_isOnline;
    });

    // TODO: Update online status via API
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(_isOnline ? 'You are now online' : 'You are now offline'),
        backgroundColor: _isOnline ? Colors.green : Colors.grey,
      ),
    );
  }

  void _contactLessor() {
    // TODO: Contact lessor functionality
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Contacting lessor...')));
  }

  void _viewLeaseTerms() {
    // TODO: Navigate to lease terms screen
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Viewing lease terms...')));
  }

  void _reportIssue() {
    // TODO: Report issue functionality
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Report issue feature coming soon')),
    );
  }

  void _triggerEmergency() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Emergency Alert'),
        content: const Text(
          'This will send an emergency alert to your lessor and emergency services. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // TODO: Trigger emergency alert
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
}
