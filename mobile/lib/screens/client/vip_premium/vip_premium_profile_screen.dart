import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../services/auth_provider.dart';

class VipPremiumProfileScreen extends StatefulWidget {
  const VipPremiumProfileScreen({super.key});

  @override
  State<VipPremiumProfileScreen> createState() =>
      _VipPremiumProfileScreenState();
}

class _VipPremiumProfileScreenState extends State<VipPremiumProfileScreen>
    with TickerProviderStateMixin {
  late AnimationController _goldController;
  late AnimationController _cardController;

  bool _discreetModeEnabled = true;
  bool _encryptedTrackingEnabled = true;
  bool _emergencyContactsEnabled = true;
  bool _conciergeNotificationsEnabled = true;
  bool _hotelPartnershipEnabled = true;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      body: CustomScrollView(
        slivers: [
          _buildVipPremiumAppBar(),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildMembershipCard(),
                  const SizedBox(height: 20),
                  _buildQuickActions(),
                  const SizedBox(height: 20),
                  _buildVipPremiumFeatures(),
                  const SizedBox(height: 20),
                  _buildSecuritySettings(),
                  const SizedBox(height: 20),
                  _buildMembershipDetails(),
                  const SizedBox(height: 20),
                  _buildConciergeContact(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVipPremiumAppBar() {
    return SliverAppBar(
      expandedHeight: 200,
      floating: false,
      pinned: true,
      backgroundColor: Colors.black,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.amber, Colors.orange, Colors.deepOrange],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 60),
              AnimatedBuilder(
                animation: _goldController,
                builder: (context, child) {
                  return Transform.scale(
                    scale: 1.0 + (0.1 * (0.5 + 0.5 * _goldController.value)),
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.white.withOpacity(0.3),
                            blurRadius: 20,
                            spreadRadius: 5,
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.diamond,
                        color: Colors.white,
                        size: 40,
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 15),
              Consumer<AuthProvider>(
                builder: (context, authProvider, child) {
                  return Column(
                    children: [
                      Text(
                        authProvider.user?.name ?? 'VIP Premium Member',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 5),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Text(
                          'VIP PREMIUM MEMBER',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.2,
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),
            ],
          ),
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.settings, color: Colors.white),
          onPressed: _openSettings,
        ),
      ],
    );
  }

  Widget _buildMembershipCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF2C2C2C), Color(0xFF1A1A1A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.amber, width: 2),
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
          Row(
            children: [
              const Icon(Icons.diamond, color: Colors.amber, size: 24),
              const SizedBox(width: 10),
              const Text(
                'VIP Premium Card',
                style: TextStyle(
                  color: Colors.amber,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  'ACTIVE',
                  style: TextStyle(
                    color: Colors.green,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Consumer<AuthProvider>(
            builder: (context, authProvider, child) {
              return Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Member Since',
                          style: TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                        Text(
                          authProvider.user?.memberSince ?? 'Jan 2024',
                          style: const TextStyle(
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
                        const Text(
                          'Tier Level',
                          style: TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                        Text(
                          authProvider.user?.tierLevel ?? 'Premium',
                          style: const TextStyle(
                            color: Colors.amber,
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
                        const Text(
                          'Next Renewal',
                          style: TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                        Text(
                          authProvider.user?.renewalDate ?? 'Jul 2025',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              );
            },
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
        'subtitle': 'Premium vehicles',
        'color': Colors.amber,
        'action': () => _navigateToBooking(),
      },
      {
        'icon': Icons.hotel,
        'title': 'Hotel Partners',
        'subtitle': 'Exclusive access',
        'color': Colors.blue,
        'action': () => _navigateToHotels(),
      },
      {
        'icon': Icons.support_agent,
        'title': 'Concierge',
        'subtitle': '24/7 assistance',
        'color': Colors.green,
        'action': () => _navigateToConcierge(),
      },
      {
        'icon': Icons.security,
        'title': 'Security',
        'subtitle': 'Encrypted tracking',
        'color': Colors.red,
        'action': () => _navigateToSecurity(),
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

  Widget _buildVipPremiumFeatures() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'VIP Premium Features',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 15),
          _buildFeatureToggle(
            'Discreet Mode',
            'Minimal client details shared with drivers',
            Icons.visibility_off,
            _discreetModeEnabled,
            (value) => setState(() => _discreetModeEnabled = value),
          ),
          _buildFeatureToggle(
            'Encrypted Tracking',
            'AES-256-GCM GPS encryption for safety',
            Icons.lock,
            _encryptedTrackingEnabled,
            (value) => setState(() => _encryptedTrackingEnabled = value),
          ),
          _buildFeatureToggle(
            'Emergency Contacts',
            'Automatic SOS notifications',
            Icons.emergency,
            _emergencyContactsEnabled,
            (value) => setState(() => _emergencyContactsEnabled = value),
          ),
          _buildFeatureToggle(
            'Concierge Notifications',
            'Priority support messages',
            Icons.notifications,
            _conciergeNotificationsEnabled,
            (value) => setState(() => _conciergeNotificationsEnabled = value),
          ),
          _buildFeatureToggle(
            'Hotel Partnerships',
            'Exclusive hotel perks and booking',
            Icons.hotel,
            _hotelPartnershipEnabled,
            (value) => setState(() => _hotelPartnershipEnabled = value),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureToggle(
    String title,
    String subtitle,
    IconData icon,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[700],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.amber.withOpacity(0.1),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(icon, color: Colors.amber, size: 18),
          ),
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
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeThumbColor: Colors.amber,
            inactiveThumbColor: Colors.grey,
            inactiveTrackColor: Colors.grey[600],
          ),
        ],
      ),
    );
  }

  Widget _buildSecuritySettings() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.security, color: Colors.red, size: 20),
              SizedBox(width: 8),
              Text(
                'Security Settings',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),
          _buildSecurityItem(
            'Emergency Contacts',
            '3 contacts configured',
            Icons.contact_emergency,
          ),
          _buildSecurityItem(
            'Two-Factor Authentication',
            'Enabled via SMS',
            Icons.verified_user,
          ),
          _buildSecurityItem(
            'Trusted Devices',
            '2 devices registered',
            Icons.devices,
          ),
          _buildSecurityItem(
            'Location Services',
            'High accuracy enabled',
            Icons.location_on,
          ),
        ],
      ),
    );
  }

  Widget _buildSecurityItem(String title, String status, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, color: Colors.grey[400], size: 18),
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
                  status,
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          const Icon(Icons.arrow_forward_ios, color: Colors.grey, size: 14),
        ],
      ),
    );
  }

  Widget _buildMembershipDetails() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Membership Benefits',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 15),
          _BenefitItem(
            icon: Icons.priority_high,
            title: 'Priority Ride Matching',
            description: 'Faster response times with premium drivers',
          ),
          _BenefitItem(
            icon: Icons.hotel_class,
            title: 'Hotel Partnerships',
            description: 'Exclusive perks at 50+ partner hotels',
          ),
          _BenefitItem(
            icon: Icons.shield,
            title: 'Enhanced Security',
            description: 'Encrypted tracking and emergency response',
          ),
          _BenefitItem(
            icon: Icons.support_agent,
            title: '24/7 Concierge',
            description: 'Personal assistance anytime, anywhere',
          ),
        ],
      ),
    );
  }

  Widget _buildConciergeContact() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Colors.amber, Colors.orange],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const CircleAvatar(
            backgroundColor: Colors.white,
            child: Icon(Icons.support_agent, color: Colors.amber),
          ),
          const SizedBox(width: 15),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Need Assistance?',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Your personal concierge is available 24/7',
                  style: TextStyle(color: Colors.white, fontSize: 12),
                ),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: _navigateToConcierge,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: Colors.amber,
            ),
            child: const Text('Chat Now'),
          ),
        ],
      ),
    );
  }

  void _navigateToBooking() {
    Navigator.pushNamed(context, '/vip_premium_booking');
  }

  void _navigateToHotels() {
    Navigator.pushNamed(context, '/hotel_dashboard');
  }

  void _navigateToConcierge() {
    Navigator.pushNamed(context, '/concierge_chat');
  }

  void _navigateToSecurity() {
    Navigator.pushNamed(context, '/security_settings');
  }

  void _openSettings() {
    // TODO: Navigate to settings
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Settings screen coming soon!'),
        backgroundColor: Colors.amber,
      ),
    );
  }

  @override
  void dispose() {
    _goldController.dispose();
    _cardController.dispose();
    super.dispose();
  }
}

class _BenefitItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;

  const _BenefitItem({
    required this.icon,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: Colors.amber.withOpacity(0.1),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(icon, color: Colors.amber, size: 16),
          ),
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
                    fontWeight: FontWeight.w600,
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
}
