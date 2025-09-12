import 'package:flutter/material.dart';
import 'premium_card_payment_screen.dart';
import 'premium_card_activation_screen.dart';

class PremiumUpgradeScreen extends StatefulWidget {
  const PremiumUpgradeScreen({super.key});

  @override
  State<PremiumUpgradeScreen> createState() => _PremiumUpgradeScreenState();
}

class _PremiumUpgradeScreenState extends State<PremiumUpgradeScreen> {
  int _selectedTierIndex = 0;
  final PageController _pageController = PageController();

  final List<Map<String, dynamic>> _tiers = [
    {
      'name': 'NORMAL',
      'price': 'Free',
      'color': Colors.grey,
      'features': [
        'Standard ride booking',
        'Basic driver ratings',
        'Standard customer support',
        'Basic payment options',
        'Regular wait times',
      ],
      'limitations': [
        'No priority booking',
        'Limited vehicle options',
        'No hotel partnerships',
        'Standard commission rates',
      ],
    },
    {
      'name': 'VIP',
      'price': '\$99.99/year',
      'originalPrice': '\$119.99',
      'color': Colors.purple,
      'features': [
        'Luxury vehicle access',
        'Priority booking',
        'Hotel partnerships',
        'Premium support',
        'Exclusive discounts',
        'Fast-track service',
        'Premium driver selection',
        'Flexible cancellation',
      ],
      'savings': 'Save 15% on all rides',
    },
    {
      'name': 'VIP PREMIUM',
      'price': '\$149.99/18 months',
      'originalPrice': '\$199.99',
      'color': Colors.amber,
      'features': [
        'Everything in VIP +',
        'Encrypted GPS tracking',
        'SOS emergency button',
        'Trusted driver network',
        '24/7 concierge service',
        'Airport meet & greet',
        'Custom ride preferences',
        'Multi-destination trips',
      ],
      'savings': 'Save 25% on all rides',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Upgrade Your Experience',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
      body: Column(
        children: [
          // Header
          _buildHeader(),

          // Tier Cards
          Expanded(flex: 3, child: _buildTierCards()),

          // Selected Tier Details
          Expanded(flex: 2, child: _buildTierDetails()),

          // Action Buttons
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          const Icon(Icons.diamond, size: 60, color: Colors.amber),
          const SizedBox(height: 15),
          const Text(
            'Choose Your Tier',
            style: TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Unlock premium features and exclusive benefits',
            style: TextStyle(color: Colors.grey[400], fontSize: 16),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildTierCards() {
    return PageView.builder(
      controller: _pageController,
      onPageChanged: (index) {
        setState(() {
          _selectedTierIndex = index;
        });
      },
      itemCount: _tiers.length,
      itemBuilder: (context, index) {
        final tier = _tiers[index];
        final isSelected = index == _selectedTierIndex;

        return AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          margin: EdgeInsets.symmetric(
            horizontal: 20,
            vertical: isSelected ? 10 : 30,
          ),
          child: _buildTierCard(tier, isSelected),
        );
      },
    );
  }

  Widget _buildTierCard(Map<String, dynamic> tier, bool isSelected) {
    final color = tier['color'] as Color;

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: isSelected
              ? [color.withOpacity(0.8), color.withOpacity(1.0)]
              : [Colors.grey[800]!, Colors.grey[850]!],
        ),
        borderRadius: BorderRadius.circular(25),
        boxShadow: isSelected
            ? [
                BoxShadow(
                  color: color.withOpacity(0.3),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ]
            : [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(25),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Tier Badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              decoration: BoxDecoration(
                color: isSelected
                    ? Colors.white.withOpacity(0.2)
                    : Colors.grey[700],
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                tier['name'],
                style: TextStyle(
                  color: isSelected ? Colors.white : Colors.grey[400],
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Icon
            Icon(
              tier['name'] == 'VIP'
                  ? Icons.diamond
                  : tier['name'] == 'PREMIUM'
                  ? Icons.star
                  : Icons.person,
              size: 50,
              color: isSelected ? Colors.white : Colors.grey[500],
            ),

            const SizedBox(height: 20),

            // Price
            if (tier['originalPrice'] != null) ...[
              Text(
                tier['originalPrice'],
                style: TextStyle(
                  color: isSelected ? Colors.white60 : Colors.grey[500],
                  fontSize: 16,
                  decoration: TextDecoration.lineThrough,
                ),
              ),
              const SizedBox(height: 5),
            ],
            Text(
              tier['price'],
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.grey[300],
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),

            if (tier['savings'] != null) ...[
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  tier['savings'],
                  style: const TextStyle(
                    color: Colors.green,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],

            if (isSelected) ...[
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Text(
                  'RECOMMENDED',
                  style: TextStyle(
                    color: color.withOpacity(0.8),
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTierDetails() {
    final tier = _tiers[_selectedTierIndex];
    final features = tier['features'] as List<String>;

    return Container(
      margin: const EdgeInsets.all(20),
      padding: const EdgeInsets.all(25),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.check_circle, color: tier['color'], size: 24),
              const SizedBox(width: 10),
              Text(
                '${tier['name']} Features',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),

          const SizedBox(height: 15),

          Expanded(
            child: ListView.builder(
              itemCount: features.length,
              itemBuilder: (context, index) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Row(
                    children: [
                      Container(
                        width: 6,
                        height: 6,
                        decoration: BoxDecoration(
                          color: tier['color'],
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          features[index],
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 14,
                            height: 1.3,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    final tier = _tiers[_selectedTierIndex];
    final isNormalTier = tier['name'] == 'NORMAL';

    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // Page indicators
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(_tiers.length, (index) {
              return Container(
                margin: const EdgeInsets.symmetric(horizontal: 4),
                width: index == _selectedTierIndex ? 20 : 8,
                height: 8,
                decoration: BoxDecoration(
                  color: index == _selectedTierIndex
                      ? _tiers[index]['color']
                      : Colors.grey[600],
                  borderRadius: BorderRadius.circular(4),
                ),
              );
            }),
          ),

          const SizedBox(height: 20),

          if (!isNormalTier) ...[
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: () {
                  final tierName = tier['name'].toString().toLowerCase();
                  // Convert tier name to proper format and amount
                  final cardType = tierName == 'vip premium'
                      ? 'vip_premium'
                      : 'vip';
                  final amount = cardType == 'vip_premium' ? 149.99 : 99.99;

                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => PremiumCardPaymentScreen(
                        cardType: cardType,
                        amount: amount,
                      ),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: (tier['color'] as Color).withOpacity(0.8),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                  elevation: 5,
                ),
                child: Text(
                  'Upgrade to ${tier['name']}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),

            const SizedBox(height: 12),

            TextButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const PremiumCardActivationScreen(),
                  ),
                );
              },
              child: const Text(
                'Already have a verification code?',
                style: TextStyle(color: Colors.blue, fontSize: 14),
              ),
            ),
          ] else ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.grey[800],
                borderRadius: BorderRadius.circular(15),
                border: Border.all(color: Colors.grey[700]!),
              ),
              child: const Column(
                children: [
                  Icon(Icons.info_outline, color: Colors.blue, size: 30),
                  SizedBox(height: 10),
                  Text(
                    'You\'re currently on the Normal tier',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 5),
                  Text(
                    'Swipe to explore premium options',
                    style: TextStyle(color: Colors.grey, fontSize: 14),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
