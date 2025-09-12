import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../services/api_service.dart';
import '../../../widgets/map/live_map_widget.dart';

class VipClientHomeScreen extends StatefulWidget {
  const VipClientHomeScreen({super.key});

  @override
  State<VipClientHomeScreen> createState() => _VipClientHomeScreenState();
}

class _VipClientHomeScreenState extends State<VipClientHomeScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  bool _discreteMode = false;

  // User and VIP data
  Map<String, dynamic> _userInfo = {};
  Map<String, dynamic> _vipStatus = {};
  List<Map<String, dynamic>> _recentRides = [];
  List<Map<String, dynamic>> _preferredDrivers = [];
  Map<String, dynamic> _conciergeInfo = {};

  @override
  void initState() {
    super.initState();
    _loadHomeData();
  }

  Future<void> _loadHomeData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real VIP data from API
      await Future.delayed(const Duration(seconds: 1));

      setState(() {
        _userInfo = {
          'name': 'Dr. Sarah Williams',
          'tier': 'VIP',
          'member_since': '2023-05-15',
          'profile_image': null,
          'phone': '+234 803 999 8888',
          'email': 'sarah.williams@email.com',
        };

        _vipStatus = {
          'priority_level': 'Platinum',
          'rides_this_month': 24,
          'loyalty_points': 1250,
          'next_tier_points': 750, // Points needed for next tier
          'concierge_available': true,
          'priority_matching': true,
          'discrete_booking': true,
          'premium_vehicles_only': true,
        };

        _recentRides = [
          {
            'id': 'vip_001',
            'date': '2024-03-10',
            'pickup': 'Lagos Island Executive Office',
            'dropoff': 'Eko Hotel & Suites',
            'driver_name': 'James O.',
            'driver_rating': 4.9,
            'vehicle': '2023 Mercedes E-Class',
            'fare': 8500.0,
            'status': 'completed',
            'discrete': true,
          },
          {
            'id': 'vip_002',
            'date': '2024-03-09',
            'pickup': 'Ikoyi Residence',
            'dropoff': 'Murtala Mohammed Airport',
            'driver_name': 'David A.',
            'driver_rating': 4.8,
            'vehicle': '2022 BMW 5 Series',
            'fare': 12000.0,
            'status': 'completed',
            'discrete': false,
          },
        ];

        _preferredDrivers = [
          {
            'id': 'driver_001',
            'name': 'James Okafor',
            'rating': 4.9,
            'rides_completed': 45,
            'vehicle': '2023 Mercedes E-Class',
            'specialties': ['Airport transfers', 'Business meetings'],
            'available': true,
            'last_ride': '2024-03-10',
          },
          {
            'id': 'driver_002',
            'name': 'David Adebayo',
            'rating': 4.8,
            'rides_completed': 32,
            'vehicle': '2022 BMW 5 Series',
            'specialties': ['Evening events', 'Hotel pickups'],
            'available': false,
            'last_ride': '2024-03-09',
          },
        ];

        _conciergeInfo = {
          'available': true,
          'agent_name': 'Michael Thompson',
          'response_time': '< 2 minutes',
          'services': [
            'Ride planning',
            'Event coordination',
            'Emergency assistance',
          ],
          'contact_methods': ['Chat', 'Phone', 'WhatsApp'],
        };
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading VIP data: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.amber[600]!, Colors.amber[800]!],
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.star, color: Colors.white, size: 16),
                  const SizedBox(width: 4),
                  Text(
                    'VIP',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Text(
              'Welcome, ${_userInfo['name']?.split(' ')[0] ?? 'VIP'}',
              style: const TextStyle(fontSize: 16),
            ),
          ],
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          // Discrete mode toggle
          IconButton(
            icon: Icon(
              _discreteMode ? Icons.visibility_off : Icons.visibility,
              color: _discreteMode ? Colors.amber[600] : Colors.grey[600],
            ),
            onPressed: _toggleDiscreteMode,
            tooltip: 'Discrete Mode',
          ),
          // SOS button
          IconButton(
            icon: Icon(Icons.emergency, color: Colors.red[600]),
            onPressed: _triggerVipSos,
            tooltip: 'VIP Emergency',
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
                    // VIP Status Card
                    _buildVipStatusCard(),

                    const SizedBox(height: 20),

                    // Quick Actions
                    _buildQuickActionsGrid(),

                    const SizedBox(height: 20),

                    // Live Map
                    _buildLiveMapCard(),

                    const SizedBox(height: 20),

                    // Concierge Service
                    _buildConciergeCard(),

                    const SizedBox(height: 20),

                    // Preferred Drivers
                    _buildPreferredDriversCard(),

                    const SizedBox(height: 20),

                    // Recent VIP Rides
                    _buildRecentRidesCard(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildVipStatusCard() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.amber[400]!,
              Colors.amber[700]!,
              Colors.orange[800]!,
            ],
          ),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(Icons.diamond, color: Colors.white, size: 24),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${_vipStatus['priority_level']} VIP',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Member since ${_userInfo['member_since']}',
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                if (_discreteMode)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.visibility_off,
                          color: Colors.white,
                          size: 12,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'DISCRETE',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),

            const SizedBox(height: 20),

            // VIP Stats
            Row(
              children: [
                Expanded(
                  child: _buildVipStat(
                    'Rides This Month',
                    '${_vipStatus['rides_this_month']}',
                    Icons.drive_eta,
                  ),
                ),
                Expanded(
                  child: _buildVipStat(
                    'Loyalty Points',
                    '${_vipStatus['loyalty_points']}',
                    Icons.stars,
                  ),
                ),
                Expanded(
                  child: _buildVipStat(
                    'Priority Level',
                    '${_vipStatus['priority_level']}',
                    Icons.trending_up,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Loyalty progress
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Next Tier Progress',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                    Text(
                      '${_vipStatus['next_tier_points']} points to go',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                LinearProgressIndicator(
                  value:
                      _vipStatus['loyalty_points'] /
                      (_vipStatus['loyalty_points'] +
                          _vipStatus['next_tier_points']),
                  backgroundColor: Colors.white.withOpacity(0.3),
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionsGrid() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'VIP Services',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.grey[800],
          ),
        ),
        const SizedBox(height: 12),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.2,
          children: [
            _buildQuickActionCard(
              'Priority Booking',
              'Instant premium rides',
              Icons.flash_on,
              Colors.blue[600]!,
              _priorityBooking,
            ),
            _buildQuickActionCard(
              'Preferred Driver',
              'Book your favorite driver',
              Icons.person_pin,
              Colors.green[600]!,
              _bookPreferredDriver,
            ),
            _buildQuickActionCard(
              'Airport VIP',
              'Premium airport service',
              Icons.flight,
              Colors.purple[600]!,
              _airportVipService,
            ),
            _buildQuickActionCard(
              'Concierge Chat',
              'Personal assistance',
              Icons.support_agent,
              Colors.orange[600]!,
              _openConciergeChat,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildLiveMapCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(Icons.map, color: Colors.blue[600]),
                const SizedBox(width: 8),
                Text(
                  'Live Map & Nearby VIP Drivers',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
              ],
            ),
          ),
          Container(
            height: 200,
            margin: const EdgeInsets.only(left: 16, right: 16, bottom: 16),
            decoration: BoxDecoration(borderRadius: BorderRadius.circular(12)),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: const LiveMapWidget(
                showNearbyDrivers: true,
                currentLocation: LatLng(6.5244, 3.3792), // Lagos
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConciergeCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.orange[100],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(Icons.support_agent, color: Colors.orange[600]),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Personal Concierge',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[800],
                        ),
                      ),
                      Text(
                        _conciergeInfo['available']
                            ? 'Available 24/7 • ${_conciergeInfo['response_time']} response'
                            : 'Currently unavailable',
                        style: TextStyle(
                          fontSize: 12,
                          color: _conciergeInfo['available']
                              ? Colors.green[600]
                              : Colors.red[600],
                        ),
                      ),
                    ],
                  ),
                ),
                if (_conciergeInfo['available'])
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: Colors.green[500],
                      shape: BoxShape.circle,
                    ),
                  ),
              ],
            ),

            const SizedBox(height: 16),

            Text(
              'Agent: ${_conciergeInfo['agent_name']}',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Colors.grey[700],
              ),
            ),

            const SizedBox(height: 8),

            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: (_conciergeInfo['services'] as List<String>).map((
                service,
              ) {
                return Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.orange[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.orange[200]!),
                  ),
                  child: Text(
                    service,
                    style: TextStyle(fontSize: 10, color: Colors.orange[600]),
                  ),
                );
              }).toList(),
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _openConciergeChat,
                    icon: const Icon(Icons.chat, size: 16),
                    label: const Text('Chat'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange[600],
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 8),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _callConcierge,
                    icon: const Icon(Icons.phone, size: 16),
                    label: const Text('Call'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.orange[600],
                      side: BorderSide(color: Colors.orange[300]!),
                      padding: const EdgeInsets.symmetric(vertical: 8),
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

  Widget _buildPreferredDriversCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.person_pin, color: Colors.green[600]),
                const SizedBox(width: 8),
                Text(
                  'Preferred Drivers',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: _viewAllDrivers,
                  child: const Text('View All'),
                ),
              ],
            ),

            const SizedBox(height: 16),

            ..._preferredDrivers.take(2).map((driver) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildDriverCard(driver),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentRidesCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.history, color: Colors.purple[600]),
                const SizedBox(width: 8),
                Text(
                  'Recent VIP Rides',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: _viewRideHistory,
                  child: const Text('View All'),
                ),
              ],
            ),

            const SizedBox(height: 16),

            ..._recentRides.take(2).map((ride) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildRideCard(ride),
              );
            }),
          ],
        ),
      ),
    );
  }

  // Helper widgets
  Widget _buildVipStat(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(color: Colors.white70, fontSize: 10),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildQuickActionCard(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDriverCard(Map<String, dynamic> driver) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 20,
            backgroundColor: Colors.green[100],
            child: Text(
              driver['name'][0],
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.green[600],
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
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${driver['rating']}⭐ • ${driver['rides_completed']} rides',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                Text(
                  driver['vehicle'],
                  style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                ),
              ],
            ),
          ),
          Column(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: driver['available']
                      ? Colors.green[100]
                      : Colors.red[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  driver['available'] ? 'Available' : 'Busy',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: driver['available']
                        ? Colors.green[600]
                        : Colors.red[600],
                  ),
                ),
              ),
              const SizedBox(height: 4),
              if (driver['available'])
                InkWell(
                  onTap: () => _bookDriver(driver),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.blue[100],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      'Book',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue[600],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRideCard(Map<String, dynamic> ride) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      ride['pickup'],
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    Row(
                      children: [
                        Icon(
                          Icons.arrow_downward,
                          size: 10,
                          color: Colors.grey[600],
                        ),
                        const SizedBox(width: 4),
                        Expanded(
                          child: Text(
                            ride['dropoff'],
                            style: TextStyle(
                              fontSize: 10,
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
                    '₦${ride['fare'].toStringAsFixed(0)}',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.green[600],
                    ),
                  ),
                  if (ride['discrete'])
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 4,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.amber[100],
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        'DISCRETE',
                        style: TextStyle(
                          fontSize: 8,
                          fontWeight: FontWeight.bold,
                          color: Colors.amber[600],
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Text(
                '${ride['driver_name']} • ${ride['vehicle']}',
                style: TextStyle(fontSize: 10, color: Colors.grey[600]),
              ),
              const Spacer(),
              Text(
                ride['date'],
                style: TextStyle(fontSize: 10, color: Colors.grey[600]),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // Event handlers
  void _toggleDiscreteMode() {
    setState(() {
      _discreteMode = !_discreteMode;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _discreteMode
              ? 'Discrete mode enabled - Your identity will be masked'
              : 'Discrete mode disabled',
        ),
        backgroundColor: _discreteMode ? Colors.amber[600] : Colors.grey[600],
      ),
    );
  }

  void _triggerVipSos() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.emergency, color: Colors.red[600]),
            const SizedBox(width: 8),
            const Text('VIP Emergency Alert'),
          ],
        ),
        content: const Text(
          'This will immediately alert VIP support team and emergency services. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(
                    'VIP emergency alert sent - Support team notified',
                  ),
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

  void _priorityBooking() {
    // TODO: Navigate to priority booking screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Opening priority booking...')),
    );
  }

  void _bookPreferredDriver() {
    // TODO: Navigate to preferred driver selection
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Select preferred driver...')));
  }

  void _airportVipService() {
    // TODO: Navigate to airport VIP service
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Airport VIP service coming soon')),
    );
  }

  void _openConciergeChat() {
    // TODO: Open concierge chat
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Opening concierge chat...')));
  }

  void _callConcierge() {
    // TODO: Call concierge
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('Calling concierge...')));
  }

  void _viewAllDrivers() {
    // TODO: Navigate to all preferred drivers
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('View all drivers feature coming soon')),
    );
  }

  void _viewRideHistory() {
    // TODO: Navigate to ride history
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('View ride history feature coming soon')),
    );
  }

  void _bookDriver(Map<String, dynamic> driver) {
    // TODO: Book specific driver
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('Booking ${driver['name']}...')));
  }
}
