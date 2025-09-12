import 'package:flutter/material.dart';
import '../../../services/api_service.dart';

class VipProfileScreen extends StatefulWidget {
  const VipProfileScreen({super.key});

  @override
  State<VipProfileScreen> createState() => _VipProfileScreenState();
}

class _VipProfileScreenState extends State<VipProfileScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;

  // User profile data
  final Map<String, dynamic> _userProfile = {
    'id': 'vip_user_001',
    'full_name': 'Dr. Sarah Williams',
    'email': 'sarah.williams@email.com',
    'phone': '+234 803 999 8888',
    'avatar': null,
    'member_since': '2023-05-15',
    'tier': 'VIP',
    'tier_level': 'Platinum',
    'verification_status': 'verified',
  };

  // VIP stats
  final Map<String, dynamic> _vipStats = {
    'total_rides': 127,
    'total_spent': 2845000.0,
    'average_rating': 4.9,
    'cancellation_rate': 1.8,
    'discrete_rides_count': 89,
    'concierge_requests': 45,
    'priority_bookings': 118,
  };

  // Loyalty info
  final Map<String, dynamic> _loyaltyInfo = {
    'current_points': 18750,
    'lifetime_points': 25450,
    'tier_points': 18750,
    'points_to_next_tier': 6250,
    'next_tier': 'Diamond',
    'tier_benefits': [
      'Priority driver matching',
      'Discrete booking mode',
      '24/7 concierge service',
      'Complimentary upgrades',
      'Airport VIP lounge access',
      'Exclusive driver pool',
    ],
  };

  // Preferred drivers
  final List<Map<String, dynamic>> _preferredDrivers = [
    {
      'id': 'vip_driver_001',
      'name': 'James Okafor',
      'rating': 4.9,
      'rides_together': 23,
      'vehicle_type': 'Executive Sedan',
      'vehicle_model': '2023 Mercedes E-Class',
      'available': true,
    },
    {
      'id': 'vip_driver_002',
      'name': 'David Adebayo',
      'rating': 4.8,
      'rides_together': 18,
      'vehicle_type': 'Luxury SUV',
      'vehicle_model': '2022 BMW X5',
      'available': false,
    },
    {
      'id': 'vip_driver_003',
      'name': 'Samuel Adeola',
      'rating': 4.9,
      'rides_together': 15,
      'vehicle_type': 'Premium Van',
      'vehicle_model': 'Mercedes V-Class',
      'available': true,
    },
  ];

  @override
  void initState() {
    super.initState();
    _loadProfileData();
  }

  Future<void> _loadProfileData() async {
    setState(() => _isLoading = true);

    try {
      // TODO: Load real profile data from API
      await Future.delayed(const Duration(seconds: 1));
      // Data is already set above for demo purposes
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error loading profile: $e')));
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
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.diamond, color: Colors.white, size: 14),
                  const SizedBox(width: 4),
                  Text(
                    _userProfile['tier_level'] ?? 'VIP',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            const Text('VIP Profile'),
          ],
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            icon: Icon(Icons.edit, color: Colors.grey[600]),
            onPressed: _editProfile,
          ),
          IconButton(
            icon: Icon(Icons.settings, color: Colors.grey[600]),
            onPressed: _openSettings,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadProfileData,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Profile header
                    _buildProfileHeader(),

                    const SizedBox(height: 20),

                    // VIP tier & loyalty
                    _buildVipTierCard(),

                    const SizedBox(height: 20),

                    // VIP statistics
                    _buildVipStatsCard(),

                    const SizedBox(height: 20),

                    // Preferred drivers
                    _buildPreferredDriversCard(),

                    const SizedBox(height: 20),

                    // VIP benefits
                    _buildVipBenefitsCard(),

                    const SizedBox(height: 20),

                    // Account management
                    _buildAccountManagementCard(),

                    const SizedBox(height: 20),

                    // Support & help
                    _buildSupportCard(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildProfileHeader() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            // Avatar
            Stack(
              children: [
                CircleAvatar(
                  radius: 40,
                  backgroundColor: Colors.amber[100],
                  child: _userProfile['avatar'] != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(40),
                          child: Image.network(
                            _userProfile['avatar'],
                            width: 80,
                            height: 80,
                            fit: BoxFit.cover,
                          ),
                        )
                      : Text(
                          _userProfile['full_name']?[0] ?? 'V',
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: Colors.amber[600],
                          ),
                        ),
                ),
                if (_userProfile['verification_status'] == 'verified')
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: Colors.green[600],
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                      ),
                      child: const Icon(
                        Icons.verified,
                        color: Colors.white,
                        size: 16,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(width: 16),

            // User info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _userProfile['full_name'] ?? 'VIP User',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Colors.amber[600]!, Colors.amber[800]!],
                          ),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          '${_userProfile['tier']} ${_userProfile['tier_level']}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      if (_userProfile['verification_status'] == 'verified')
                        Row(
                          children: [
                            Icon(
                              Icons.verified,
                              size: 14,
                              color: Colors.green[600],
                            ),
                            const SizedBox(width: 2),
                            Text(
                              'Verified',
                              style: TextStyle(
                                fontSize: 10,
                                color: Colors.green[600],
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _userProfile['email'] ?? '',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  Text(
                    _userProfile['phone'] ?? '',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Member since ${_formatDate(_userProfile['member_since'])}',
                    style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVipTierCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [Colors.amber[600]!, Colors.amber[800]!],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.diamond, color: Colors.white, size: 24),
                  const SizedBox(width: 8),
                  Text(
                    '${_userProfile['tier_level']} Status',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Loyalty points
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Loyalty Points',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          '${_loyaltyInfo['current_points']}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 8),

                    // Progress to next tier
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${_loyaltyInfo['points_to_next_tier']} points to ${_loyaltyInfo['next_tier']}',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.9),
                            fontSize: 10,
                          ),
                        ),
                        const SizedBox(height: 4),
                        LinearProgressIndicator(
                          value:
                              _loyaltyInfo['tier_points'] /
                              (_loyaltyInfo['tier_points'] +
                                  _loyaltyInfo['points_to_next_tier']),
                          backgroundColor: Colors.white.withOpacity(0.3),
                          valueColor: const AlwaysStoppedAnimation<Color>(
                            Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 12),

              // Quick stats
              Row(
                children: [
                  _buildQuickStat('Total Rides', '${_vipStats['total_rides']}'),
                  _buildQuickStat(
                    'Avg Rating',
                    '${_vipStats['average_rating']}⭐',
                  ),
                  _buildQuickStat(
                    'Total Spent',
                    '₦${(_vipStats['total_spent'] / 1000).toStringAsFixed(0)}K',
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildVipStatsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'VIP Statistics',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),

            const SizedBox(height: 16),

            // Stats grid
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              childAspectRatio: 2.5,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              children: [
                _buildStatCard(
                  'Discrete Rides',
                  '${_vipStats['discrete_rides_count']}',
                  Icons.visibility_off,
                  Colors.purple[600]!,
                ),
                _buildStatCard(
                  'Priority Bookings',
                  '${_vipStats['priority_bookings']}',
                  Icons.flash_on,
                  Colors.amber[600]!,
                ),
                _buildStatCard(
                  'Concierge Requests',
                  '${_vipStats['concierge_requests']}',
                  Icons.support_agent,
                  Colors.blue[600]!,
                ),
                _buildStatCard(
                  'Cancellation Rate',
                  '${_vipStats['cancellation_rate']}%',
                  Icons.cancel,
                  _vipStats['cancellation_rate'] < 5
                      ? Colors.green[600]!
                      : Colors.red[600]!,
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
                  'Preferred Drivers (${_preferredDrivers.length})',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: _managePreferredDrivers,
                  child: const Text('Manage'),
                ),
              ],
            ),

            const SizedBox(height: 16),

            ..._preferredDrivers.take(3).map((driver) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildPreferredDriverItem(driver),
              );
            }),

            if (_preferredDrivers.length > 3)
              Center(
                child: TextButton(
                  onPressed: _viewAllPreferredDrivers,
                  child: Text('View All ${_preferredDrivers.length} Drivers'),
                ),
              ),

            if (_preferredDrivers.isEmpty)
              Center(
                child: Column(
                  children: [
                    Icon(Icons.person_add, size: 48, color: Colors.grey[400]),
                    const SizedBox(height: 8),
                    Text(
                      'No preferred drivers yet',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                    TextButton(
                      onPressed: _addPreferredDriver,
                      child: const Text('Add Preferred Driver'),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildVipBenefitsCard() {
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
                Icon(Icons.star, color: Colors.amber[600]),
                const SizedBox(width: 8),
                Text(
                  'VIP Benefits',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            ..._loyaltyInfo['tier_benefits'].map<Widget>((benefit) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Icon(
                      Icons.check_circle,
                      size: 16,
                      color: Colors.green[600],
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        benefit,
                        style: const TextStyle(fontSize: 14),
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildAccountManagementCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Account Management',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),

            const SizedBox(height: 16),

            _buildManagementOption(
              'Payment Methods',
              'Manage cards and payment options',
              Icons.payment,
              () => _openPaymentMethods(),
            ),
            _buildManagementOption(
              'Emergency Contacts',
              'Update emergency contact information',
              Icons.emergency,
              () => _manageEmergencyContacts(),
            ),
            _buildManagementOption(
              'VIP Preferences',
              'Configure VIP settings and preferences',
              Icons.tune,
              () => _openVipPreferences(),
            ),
            _buildManagementOption(
              'Privacy & Security',
              'Manage privacy and security settings',
              Icons.security,
              () => _openPrivacySettings(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSupportCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Support & Help',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),

            const SizedBox(height: 16),

            _buildSupportOption(
              'VIP Concierge',
              '24/7 personal assistance',
              Icons.support_agent,
              Colors.blue[600]!,
              () => _contactConcierge(),
            ),
            _buildSupportOption(
              'Help Center',
              'FAQs and guides',
              Icons.help_center,
              Colors.green[600]!,
              () => _openHelpCenter(),
            ),
            _buildSupportOption(
              'Contact Support',
              'Get help from our team',
              Icons.support_agent,
              Colors.orange[600]!,
              () => _contactSupport(),
            ),
          ],
        ),
      ),
    );
  }

  // Helper widgets
  Widget _buildQuickStat(String label, String value) {
    return Expanded(
      child: Column(
        children: [
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
            style: TextStyle(
              color: Colors.white.withOpacity(0.9),
              fontSize: 10,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
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
                  title,
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPreferredDriverItem(Map<String, dynamic> driver) {
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
            backgroundColor: Colors.grey[300],
            child: Text(
              driver['name'][0],
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
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
                  '${driver['rating']}⭐ • ${driver['rides_together']} rides together',
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
                Text(
                  driver['vehicle_model'],
                  style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                ),
              ],
            ),
          ),
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: driver['available'] ? Colors.green[600] : Colors.grey[400],
              shape: BoxShape.circle,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildManagementOption(
    String title,
    String subtitle,
    IconData icon,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          children: [
            Icon(icon, color: Colors.grey[600], size: 20),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            Icon(Icons.chevron_right, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  Widget _buildSupportOption(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            Icon(Icons.chevron_right, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  // Helper methods
  String _formatDate(String? dateString) {
    if (dateString == null) return '';
    try {
      final date = DateTime.parse(dateString);
      return '${_getMonthName(date.month)} ${date.year}';
    } catch (e) {
      return dateString;
    }
  }

  String _getMonthName(int month) {
    const months = [
      '',
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    return months[month];
  }

  // Event handlers
  void _editProfile() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('Edit Profile')),
          body: const Center(child: Text('Edit Profile Screen - Coming Soon')),
        ),
      ),
    );
  }

  void _openSettings() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('VIP Settings')),
          body: const Center(child: Text('VIP Settings Screen - Coming Soon')),
        ),
      ),
    );
  }

  void _managePreferredDrivers() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('Preferred Drivers')),
          body: const Center(
            child: Text('Preferred Drivers Management - Coming Soon'),
          ),
        ),
      ),
    );
  }

  void _viewAllPreferredDrivers() {
    _managePreferredDrivers();
  }

  void _addPreferredDriver() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Preferred Driver'),
        content: const Text(
          'This feature will allow you to add drivers to your preferred list after completing rides with them.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _openPaymentMethods() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('Payment Methods')),
          body: const Center(
            child: Text('Payment Methods Screen - Coming Soon'),
          ),
        ),
      ),
    );
  }

  void _manageEmergencyContacts() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('Emergency Contacts')),
          body: const Center(
            child: Text('Emergency Contacts Management - Coming Soon'),
          ),
        ),
      ),
    );
  }

  void _openVipPreferences() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('VIP Preferences')),
          body: const Center(
            child: Text('VIP Preferences Screen - Coming Soon'),
          ),
        ),
      ),
    );
  }

  void _openPrivacySettings() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('Privacy & Security')),
          body: const Center(
            child: Text('Privacy & Security Settings - Coming Soon'),
          ),
        ),
      ),
    );
  }

  void _contactConcierge() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.support_agent, color: Colors.blue[600]),
            const SizedBox(width: 8),
            const Text('VIP Concierge'),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('How would you like to contact your VIP concierge?'),
            SizedBox(height: 16),
            Text(
              '• Live Chat (Available 24/7)\n• Phone Call (+234 800 VIP HELP)\n• WhatsApp Support\n• Video Call (Premium)',
              style: TextStyle(fontSize: 14),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Chat Now'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Call'),
          ),
        ],
      ),
    );
  }

  void _openHelpCenter() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('Help Center')),
          body: const Center(child: Text('Help Center - Coming Soon')),
        ),
      ),
    );
  }

  void _contactSupport() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('Contact Support')),
          body: const Center(child: Text('Contact Support - Coming Soon')),
        ),
      ),
    );
  }
}
