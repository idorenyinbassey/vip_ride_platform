import 'package:flutter/material.dart';
import '../../../services/auth_service.dart';
import '../../../models/user_models.dart';
import '../../shared/premium_card_purchase_screen.dart';
import '../../shared/card_activation_screen.dart';

class RegularProfileScreen extends StatefulWidget {
  const RegularProfileScreen({super.key});

  @override
  State<RegularProfileScreen> createState() => _RegularProfileScreenState();
}

class _RegularProfileScreenState extends State<RegularProfileScreen>
    with TickerProviderStateMixin {
  final AuthService _authService = AuthService();

  late AnimationController _upgradeController;

  User? _user;
  bool _isLoading = true;

  final Map<String, dynamic> _userStats = {
    'totalRides': 12,
    'totalSpent': 840.0,
    'memberSince': 'Mar 2024',
    'averageRating': 4.5,
  };

  @override
  void initState() {
    super.initState();
    _upgradeController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    )..repeat();
    _loadUserProfile();
  }

  Future<void> _loadUserProfile() async {
    try {
      final user = _authService.getCurrentUser();
      setState(() {
        _user = user;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Colors.white,
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      backgroundColor: Colors.grey[100],
      body: CustomScrollView(
        slivers: [
          _buildProfileAppBar(),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _buildUpgradeCard(),
                  const SizedBox(height: 20),
                  _buildUserStats(),
                  const SizedBox(height: 20),
                  _buildProfileSections(),
                  const SizedBox(height: 20),
                  _buildVipPremiumCard(),
                  const SizedBox(height: 100),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileAppBar() {
    return SliverAppBar(
      expandedHeight: 120,
      pinned: true,
      backgroundColor: Colors.white,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.blue.withOpacity(0.1), Colors.white],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
          child: SafeArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Row(
                  children: [
                    const SizedBox(width: 20),
                    Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        color: Colors.blue.withOpacity(0.1),
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.blue.withOpacity(0.3)),
                      ),
                      child: const Icon(
                        Icons.person,
                        color: Colors.blue,
                        size: 30,
                      ),
                    ),
                    const SizedBox(width: 15),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _user?.fullName ?? 'Regular User',
                            style: const TextStyle(
                              color: Colors.black87,
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              const Icon(
                                Icons.person,
                                color: Colors.blue,
                                size: 16,
                              ),
                              const SizedBox(width: 4),
                              const Text(
                                'Regular Member',
                                style: TextStyle(
                                  color: Colors.blue,
                                  fontSize: 14,
                                ),
                              ),
                              const SizedBox(width: 10),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.green.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: const Text(
                                  'FREE',
                                  style: TextStyle(
                                    color: Colors.green,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 20),
                  ],
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.edit, color: Colors.blue),
          onPressed: _editProfile,
        ),
      ],
    );
  }

  Widget _buildUpgradeCard() {
    return AnimatedBuilder(
      animation: _upgradeController,
      builder: (context, child) {
        return Container(
          width: double.infinity,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Colors.amber.withOpacity(
                  0.8 + (_upgradeController.value * 0.2),
                ),
                Colors.orange.withOpacity(
                  0.8 + (_upgradeController.value * 0.2),
                ),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.amber.withOpacity(0.3),
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.star, color: Colors.white, size: 24),
                  const SizedBox(width: 10),
                  const Text(
                    'UPGRADE TO VIP',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: const Text(
                      '50% OFF',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 15),
              const Text(
                'Unlock priority booking, luxury vehicles, and VIP support',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '₦49.99/month',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'First month only',
                          style: TextStyle(color: Colors.white70, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  ElevatedButton(
                    onPressed: _upgradeToVip,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.amber,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(25),
                      ),
                    ),
                    child: const Text(
                      'Upgrade Now',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildUserStats() {
    final stats = [
      {
        'title': 'Total Rides',
        'value': '${_userStats['totalRides']}',
        'icon': Icons.directions_car,
        'color': Colors.blue,
      },
      {
        'title': 'Total Spent',
        'value': '₦${_userStats['totalSpent'].toStringAsFixed(0)}',
        'icon': Icons.account_balance_wallet,
        'color': Colors.green,
      },
      {
        'title': 'Member Since',
        'value': _userStats['memberSince'],
        'icon': Icons.calendar_today,
        'color': Colors.purple,
      },
      {
        'title': 'Rating',
        'value': '⭐ ${_userStats['averageRating']}',
        'icon': Icons.star,
        'color': Colors.amber,
      },
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Your Statistics',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
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
            childAspectRatio: 1.3,
          ),
          itemCount: stats.length,
          itemBuilder: (context, index) {
            final stat = stats[index];
            return Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    stat['icon'] as IconData,
                    color: stat['color'] as Color,
                    size: 24,
                  ),
                  const Spacer(),
                  Text(
                    stat['value'] as String,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    stat['title'] as String,
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildProfileSections() {
    final sections = [
      {
        'title': 'Account',
        'items': [
          {
            'icon': Icons.person_outline,
            'title': 'Personal Information',
            'action': _editPersonalInfo,
          },
          {
            'icon': Icons.security,
            'title': 'Security Settings',
            'action': _managePrivacy,
          },
          {
            'icon': Icons.notifications_outlined,
            'title': 'Notifications',
            'action': _manageNotifications,
          },
          {
            'icon': Icons.payment,
            'title': 'Payment Methods',
            'action': _managePayments,
          },
        ],
      },
      {
        'title': 'Ride Preferences',
        'items': [
          {
            'icon': Icons.location_on,
            'title': 'Saved Addresses',
            'action': _manageSavedAddresses,
          },
          {
            'icon': Icons.schedule,
            'title': 'Ride History',
            'action': _viewRideHistory,
          },
          {
            'icon': Icons.favorite,
            'title': 'Favorite Drivers',
            'action': _manageFavorites,
          },
        ],
      },
      {
        'title': 'Support & Legal',
        'items': [
          {
            'icon': Icons.help_outline,
            'title': 'Help Center',
            'action': _contactSupport,
          },
          {
            'icon': Icons.description,
            'title': 'Terms of Service',
            'action': _viewTerms,
          },
          {
            'icon': Icons.privacy_tip,
            'title': 'Privacy Policy',
            'action': _viewPrivacyPolicy,
          },
          {'icon': Icons.info_outline, 'title': 'About', 'action': _viewAbout},
        ],
      },
    ];

    return Column(
      children: sections.map((section) {
        return Container(
          margin: const EdgeInsets.only(bottom: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
                child: Text(
                  section['title'] as String,
                  style: const TextStyle(
                    color: Colors.blue,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: Column(
                  children: (section['items'] as List).asMap().entries.map((
                    entry,
                  ) {
                    final index = entry.key;
                    final item = entry.value;
                    final isLast =
                        index == (section['items'] as List).length - 1;

                    return Column(
                      children: [
                        ListTile(
                          leading: Icon(
                            item['icon'] as IconData,
                            color: Colors.blue,
                            size: 24,
                          ),
                          title: Text(
                            item['title'] as String,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w500,
                              color: Colors.black87,
                            ),
                          ),
                          trailing: const Icon(
                            Icons.arrow_forward_ios,
                            color: Colors.grey,
                            size: 16,
                          ),
                          onTap: item['action'] as VoidCallback,
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 4,
                          ),
                        ),
                        if (!isLast)
                          Divider(
                            color: Colors.grey[200],
                            height: 1,
                            indent: 60,
                            endIndent: 20,
                          ),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildVipPremiumCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Colors.purple, Colors.deepPurple],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.purple.withOpacity(0.3),
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
              Icon(Icons.diamond, color: Colors.white, size: 24),
              SizedBox(width: 12),
              Text(
                'VIP Premium Available',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),
          const Text(
            'Ultimate luxury with hotel partnerships, encrypted tracking, armored vehicles, and exclusive concierge services.',
            style: TextStyle(color: Colors.white70, fontSize: 14, height: 1.4),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '₦149.99/month',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'For the ultimate experience',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
              ElevatedButton(
                onPressed: _learnMoreVipPremium,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.purple,
                ),
                child: const Text('Learn More'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // Action methods
  void _editProfile() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Profile editing coming soon!')),
    );
  }

  void _upgradeToVip() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          title: const Row(
            children: [
              Icon(Icons.diamond, color: Colors.amber),
              SizedBox(width: 10),
              Text('Upgrade to VIP', style: TextStyle(color: Colors.white)),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Choose your upgrade method:',
                style: TextStyle(color: Colors.white, fontSize: 16),
              ),
              const SizedBox(height: 20),

              // Digital Card Option
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Colors.amber, Colors.orange],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.credit_card, color: Colors.white),
                        SizedBox(width: 8),
                        Text(
                          'VIP Digital Card',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Have a VIP card? Enter your serial number and activation code',
                      style: TextStyle(color: Colors.white, fontSize: 14),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 12),

              // Subscription Option
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[800],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey[600]!),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.payment, color: Colors.blue),
                        SizedBox(width: 8),
                        Text(
                          'Monthly Subscription',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Subscribe monthly for ₦49.99/month (50% off first month)',
                      style: TextStyle(color: Colors.grey, fontSize: 14),
                    ),
                  ],
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const CardActivationScreen(),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.amber,
                foregroundColor: Colors.black,
              ),
              child: const Text('Use VIP Card'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const PremiumCardPurchaseScreen(),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
              child: const Text('Subscribe'),
            ),
          ],
        );
      },
    );
  }

  void _editPersonalInfo() {
    Navigator.pushNamed(context, '/edit_personal_info');
  }

  void _managePrivacy() {
    Navigator.pushNamed(context, '/privacy_settings');
  }

  void _manageNotifications() {
    Navigator.pushNamed(context, '/notification_settings');
  }

  void _managePayments() {
    Navigator.pushNamed(context, '/payment_methods');
  }

  void _manageSavedAddresses() {
    Navigator.pushNamed(context, '/saved_addresses');
  }

  void _viewRideHistory() {
    Navigator.pushNamed(context, '/ride_history');
  }

  void _manageFavorites() {
    Navigator.pushNamed(context, '/favorite_drivers');
  }

  void _contactSupport() {
    Navigator.pushNamed(context, '/support');
  }

  void _viewTerms() {
    Navigator.pushNamed(context, '/terms');
  }

  void _viewPrivacyPolicy() {
    Navigator.pushNamed(context, '/privacy_policy');
  }

  void _viewAbout() {
    Navigator.pushNamed(context, '/about');
  }

  void _learnMoreVipPremium() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.diamond, color: Colors.purple),
            SizedBox(width: 10),
            Text('VIP Premium'),
          ],
        ),
        content: const Text(
          'VIP Premium offers the ultimate luxury experience with hotel partnerships, encrypted tracking, armored vehicles, and 24/7 concierge service.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Later'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pushNamed(context, '/premium_upgrade');
            },
            child: const Text('Learn More'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _upgradeController.dispose();
    super.dispose();
  }
}
