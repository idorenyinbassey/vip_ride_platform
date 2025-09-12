import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/premium_card_service.dart';
import '../../models/premium_card_models.dart';
import 'premium_card_payment_screen.dart';

class PremiumCardManagementScreen extends StatefulWidget {
  const PremiumCardManagementScreen({super.key});

  @override
  State<PremiumCardManagementScreen> createState() =>
      _PremiumCardManagementScreenState();
}

class _PremiumCardManagementScreenState
    extends State<PremiumCardManagementScreen> {
  final PremiumCardService _premiumCardService = PremiumCardService();

  PremiumDigitalCard? _activeCard;
  bool _isLoading = true;
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    _loadActiveCard();
  }

  Future<void> _loadActiveCard() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final card = await _premiumCardService.getActiveCard();
      setState(() {
        _activeCard = card;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      // Handle error - no active card or network error
    }
  }

  Future<void> _refreshCard() async {
    setState(() {
      _isRefreshing = true;
    });
    await _loadActiveCard();
    setState(() {
      _isRefreshing = false;
    });
  }

  String _getTierDisplayName(String tier) {
    switch (tier.toLowerCase()) {
      case 'vip':
        return 'VIP';
      case 'vip_premium':
        return 'VIP PREMIUM';
      default:
        return tier.toUpperCase();
    }
  }

  bool _isVipPremium(String tier) {
    return tier.toLowerCase() == 'vip_premium';
  }

  bool _isVip(String tier) {
    return tier.toLowerCase() == 'vip' || _isVipPremium(tier);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Digital Card',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: _isRefreshing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : const Icon(Icons.refresh, color: Colors.white),
            onPressed: _isRefreshing ? null : _refreshCard,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.purple),
              ),
            )
          : _activeCard != null
          ? _buildCardView()
          : _buildNoCardView(),
    );
  }

  Widget _buildCardView() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // Active Card Display
          _buildActiveCardDisplay(),

          const SizedBox(height: 30),

          // Card Stats
          _buildCardStats(),

          const SizedBox(height: 30),

          // Quick Actions
          _buildQuickActions(),

          const SizedBox(height: 30),

          // Card Features
          _buildCardFeatures(),

          const SizedBox(height: 30),

          // Card Details
          _buildCardDetails(),
        ],
      ),
    );
  }

  Widget _buildActiveCardDisplay() {
    if (_activeCard == null) return const SizedBox();

    return Container(
      width: double.infinity,
      height: 220,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: _activeCard!.tier == 'vip'
              ? [Colors.amber[700]!, Colors.amber[900]!]
              : [Colors.purple[700]!, Colors.purple[900]!],
        ),
        boxShadow: [
          BoxShadow(
            color:
                (_isVipPremium(_activeCard!.tier)
                        ? Colors.amber
                        : Colors.purple)
                    .withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Stack(
        children: [
          // Card Pattern
          Positioned(
            right: -50,
            top: -50,
            child: Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white.withOpacity(0.1),
              ),
            ),
          ),

          Padding(
            padding: const EdgeInsets.all(25),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${_activeCard!.tier.toUpperCase()} CARD',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.5,
                          ),
                        ),
                        const Text(
                          'BLACK TIER ACCESS',
                          style: TextStyle(
                            color: Colors.white70,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 5,
                      ),
                      decoration: BoxDecoration(
                        color: _activeCard!.isActive
                            ? Colors.green
                            : Colors.orange,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        _activeCard!.isActive ? 'ACTIVE' : 'PENDING',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),

                Text(
                  _activeCard!.cardNumber.replaceAllMapped(
                    RegExp(r'(\d{4})(?=\d)'),
                    (match) => '${match.group(1)} ',
                  ),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.w500,
                    letterSpacing: 2,
                  ),
                ),

                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'VALID UNTIL',
                          style: TextStyle(
                            color: Colors.white70,
                            fontSize: 10,
                            letterSpacing: 1,
                          ),
                        ),
                        Text(
                          _activeCard!.expiresAt != null
                              ? '${_activeCard!.expiresAt!.month.toString().padLeft(2, '0')}/${_activeCard!.expiresAt!.year.toString().substring(2)}'
                              : 'NEVER',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),

                    // VIP Ride logo/icon
                    Container(
                      width: 50,
                      height: 30,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Center(
                        child: Text(
                          'VIP',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCardStats() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            'Savings This Month',
            '\$45.67',
            Icons.savings,
            Colors.green,
          ),
        ),
        const SizedBox(width: 15),
        Expanded(
          child: _buildStatCard(
            'Rides This Month',
            '23',
            Icons.directions_car,
            Colors.blue,
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
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 30),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            title,
            style: TextStyle(color: Colors.grey[400], fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
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
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildActionButton(
                'Copy Card',
                Icons.copy,
                Colors.blue,
                () => _copyCardNumber(),
              ),
              _buildActionButton(
                'Share Card',
                Icons.share,
                Colors.purple,
                () => _shareCard(),
              ),
              _buildActionButton(
                'Freeze Card',
                Icons.block,
                Colors.orange,
                () => _freezeCard(),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 30),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCardFeatures() {
    final features = _isVipPremium(_activeCard!.tier)
        ? [
            'Encrypted GPS tracking',
            'SOS emergency button',
            'Luxury vehicle access',
            'Priority booking',
            'Hotel partnerships',
            '24/7 premium support',
          ]
        : [
            'Luxury vehicle access',
            'Priority booking',
            'Hotel partnerships',
            'Premium support',
            'Exclusive discounts',
            'Fast-track service',
          ];

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Your Benefits',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 20),
          ...features.map(
            (feature) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Row(
                children: [
                  Icon(
                    Icons.check_circle,
                    color: _activeCard!.tier == 'vip'
                        ? Colors.amber
                        : Colors.purple,
                    size: 20,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    feature,
                    style: const TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCardDetails() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Card Details',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 20),
          _buildDetailRow('Card Number', _activeCard!.maskedCardNumber),
          _buildDetailRow('Tier', _activeCard!.tierDisplayName),
          _buildDetailRow(
            'Status',
            _activeCard!.isActive ? 'Active' : 'Pending',
          ),
          if (_activeCard!.activatedAt != null)
            _buildDetailRow(
              'Activated',
              _formatDate(_activeCard!.activatedAt!),
            ),
          if (_activeCard!.expiresAt != null)
            _buildDetailRow('Expires', _formatDate(_activeCard!.expiresAt!)),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 15),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey[400], fontSize: 14)),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNoCardView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.credit_card_off, size: 100, color: Colors.grey[600]),
            const SizedBox(height: 30),
            const Text(
              'No Active Card',
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 15),
            Text(
              'You don\'t have an active Premium Digital Card. Purchase one to unlock Black-Tier benefits.',
              style: TextStyle(color: Colors.grey[400], fontSize: 16),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const PremiumCardPaymentScreen(
                        cardType: 'vip_premium',
                        amount: 149.99,
                      ),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purple[700],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
                child: const Text(
                  'Purchase Premium Card',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _copyCardNumber() {
    if (_activeCard != null) {
      Clipboard.setData(ClipboardData(text: _activeCard!.cardNumber));
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Card number copied to clipboard'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  void _shareCard() {
    // Implement share functionality
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Share functionality coming soon')),
    );
  }

  void _freezeCard() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[850],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
        title: const Text('Freeze Card', style: TextStyle(color: Colors.white)),
        content: const Text(
          'Are you sure you want to freeze this card? You can unfreeze it anytime from settings.',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // Implement freeze functionality
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Card frozen successfully'),
                  backgroundColor: Colors.orange,
                ),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
            child: const Text('Freeze Card'),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}
