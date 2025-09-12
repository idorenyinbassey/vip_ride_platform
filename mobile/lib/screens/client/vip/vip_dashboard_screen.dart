import 'package:flutter/material.dart';
import '../../../services/ride_service.dart';
import '../../../models/ride_models.dart';

class VipDashboardScreen extends StatefulWidget {
  const VipDashboardScreen({super.key});

  @override
  State<VipDashboardScreen> createState() => _VipDashboardScreenState();
}

class _VipDashboardScreenState extends State<VipDashboardScreen>
    with TickerProviderStateMixin {
  final RideService _rideService = RideService();
  late AnimationController _goldController;
  late AnimationController _cardController;

  List<Ride> _recentRides = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _loadDashboardData();
  }

  void _initializeAnimations() {
    _goldController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    )..repeat();

    _cardController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
  }

  Future<void> _loadDashboardData() async {
    setState(() => _isLoading = true);
    try {
      final rides = await _rideService.getUserRides();
      setState(() {
        _recentRides = rides.take(3).toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadDashboardData,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildVipHeader(),
                const SizedBox(height: 20),
                _buildVipMembershipCard(),
                const SizedBox(height: 20),
                _buildQuickActions(),
                const SizedBox(height: 20),
                _buildVipFeatures(),
                const SizedBox(height: 20),
                _buildRecentRides(),
                const SizedBox(height: 20),
                _buildUpgradePrompt(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildVipHeader() {
    return Row(
      children: [
        AnimatedBuilder(
          animation: _goldController,
          builder: (context, child) {
            return Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.amber.withOpacity(
                  0.1 + (_goldController.value * 0.1),
                ),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.amber.withOpacity(0.5)),
              ),
              child: const Icon(Icons.star, color: Colors.amber, size: 24),
            );
          },
        ),
        const SizedBox(width: 15),
        const Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Welcome back, VIP!',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'Priority service at your fingertips',
                style: TextStyle(color: Colors.grey, fontSize: 14),
              ),
            ],
          ),
        ),
        IconButton(
          icon: const Icon(Icons.notifications, color: Colors.amber),
          onPressed: () => _showNotifications(),
        ),
      ],
    );
  }

  Widget _buildVipMembershipCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Colors.amber, Colors.orange],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.amber.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.star, color: Colors.white, size: 24),
              SizedBox(width: 10),
              Text(
                'VIP Membership',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Spacer(),
              Text(
                'ACTIVE',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          const Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Member Since',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                    Text(
                      'Jan 2024',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
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
                      'Next Billing',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                    Text(
                      'Oct 2025',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    final actions = [
      {
        'icon': Icons.directions_car,
        'title': 'Book VIP Ride',
        'subtitle': 'Luxury vehicles',
        'color': Colors.amber,
        'action': () => _navigateToBooking(),
      },
      {
        'icon': Icons.schedule,
        'title': 'Schedule Ride',
        'subtitle': 'Plan ahead',
        'color': Colors.blue,
        'action': () => _scheduleRide(),
      },
      {
        'icon': Icons.support_agent,
        'title': 'VIP Support',
        'subtitle': 'Priority help',
        'color': Colors.green,
        'action': () => _contactSupport(),
      },
      {
        'icon': Icons.local_offer,
        'title': 'Offers',
        'subtitle': 'VIP deals',
        'color': Colors.purple,
        'action': () => _viewOffers(),
      },
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Quick Actions',
          style: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 15),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 15,
            mainAxisSpacing: 15,
            childAspectRatio: 1.2,
          ),
          itemCount: actions.length,
          itemBuilder: (context, index) {
            final action = actions[index];
            return GestureDetector(
              onTapDown: (_) => _cardController.forward(),
              onTapUp: (_) => _cardController.reverse(),
              onTapCancel: () => _cardController.reverse(),
              onTap: action['action'] as VoidCallback,
              child: AnimatedBuilder(
                animation: _cardController,
                builder: (context, child) {
                  return Transform.scale(
                    scale: 1.0 - (_cardController.value * 0.05),
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.grey[800],
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: (action['color'] as Color).withOpacity(0.3),
                        ),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            action['icon'] as IconData,
                            color: action['color'] as Color,
                            size: 32,
                          ),
                          const SizedBox(height: 10),
                          Text(
                            action['title'] as String,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            action['subtitle'] as String,
                            style: const TextStyle(
                              color: Colors.grey,
                              fontSize: 12,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildVipFeatures() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.amber.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.star, color: Colors.amber, size: 20),
              SizedBox(width: 8),
              Text(
                'Your VIP Benefits',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),
          _buildBenefitItem(
            'Priority ride matching',
            'Faster response times',
            Icons.flash_on,
          ),
          _buildBenefitItem(
            'Luxury vehicles',
            'BMW, Mercedes, Audi access',
            Icons.directions_car_filled,
          ),
          _buildBenefitItem(
            'VIP support',
            'Dedicated support team',
            Icons.headset_mic,
          ),
          _buildBenefitItem(
            '10% discount',
            'On all rides this month',
            Icons.discount,
          ),
        ],
      ),
    );
  }

  Widget _buildBenefitItem(String title, String description, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, color: Colors.amber, size: 18),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  description,
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentRides() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Text(
              'Recent Rides',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            Spacer(),
            Text(
              'View All',
              style: TextStyle(color: Colors.amber, fontSize: 14),
            ),
          ],
        ),
        const SizedBox(height: 15),
        if (_isLoading)
          const Center(child: CircularProgressIndicator(color: Colors.amber))
        else if (_recentRides.isEmpty)
          _buildEmptyRides()
        else
          ..._recentRides.map((ride) => _buildRideCard(ride)),
      ],
    );
  }

  Widget _buildEmptyRides() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(30),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Column(
        children: [
          Icon(Icons.directions_car, color: Colors.grey, size: 48),
          SizedBox(height: 15),
          Text(
            'No rides yet',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w500,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Book your first VIP ride to get started',
            style: TextStyle(color: Colors.grey, fontSize: 14),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildRideCard(Ride ride) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.amber.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.directions_car,
              color: Colors.amber,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${ride.pickup} → ${ride.destination}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  'Completed • ${ride.createdAt.day}/${ride.createdAt.month}',
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          if (ride.fare != null)
            Text(
              '₦${ride.fare!.toStringAsFixed(0)}',
              style: const TextStyle(
                color: Colors.amber,
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildUpgradePrompt() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Colors.purple, Colors.deepPurple],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const Icon(Icons.diamond, color: Colors.white, size: 24),
          const SizedBox(width: 12),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Upgrade to VIP Premium',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Get hotel partnerships, encrypted tracking & more',
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: _upgradeToVipPremium,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: Colors.purple,
            ),
            child: const Text('Upgrade'),
          ),
        ],
      ),
    );
  }

  // Navigation methods
  void _navigateToBooking() {
    Navigator.pushNamed(context, '/vip_booking');
  }

  void _scheduleRide() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Schedule ride feature coming soon!'),
        backgroundColor: Colors.amber,
      ),
    );
  }

  void _contactSupport() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Connecting to VIP support...'),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _viewOffers() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('VIP offers and deals coming soon!'),
        backgroundColor: Colors.purple,
      ),
    );
  }

  void _showNotifications() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[800],
        title: const Text(
          'VIP Notifications',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          'No new notifications',
          style: TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK', style: TextStyle(color: Colors.amber)),
          ),
        ],
      ),
    );
  }

  void _upgradeToVipPremium() {
    Navigator.pushNamed(context, '/premium_upgrade');
  }

  @override
  void dispose() {
    _goldController.dispose();
    _cardController.dispose();
    super.dispose();
  }
}
