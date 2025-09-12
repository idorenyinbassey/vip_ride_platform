import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_provider.dart';
import '../models/premium_card_models.dart';
import '../services/premium_card_service.dart';
import '../screens/shared/premium_card_payment_screen.dart';
import '../screens/shared/premium_card_management_screen.dart';
import '../screens/shared/premium_card_activation_screen.dart';

class PremiumStatusWidget extends StatefulWidget {
  const PremiumStatusWidget({super.key});

  @override
  State<PremiumStatusWidget> createState() => _PremiumStatusWidgetState();
}

class _PremiumStatusWidgetState extends State<PremiumStatusWidget> {
  final PremiumCardService _premiumCardService = PremiumCardService();
  PremiumDigitalCard? _activeCard;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUserPremiumStatus();
  }

  Future<void> _loadUserPremiumStatus() async {
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
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Container(
        height: 120,
        margin: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[850],
          borderRadius: BorderRadius.circular(15),
        ),
        child: const Center(child: CircularProgressIndicator()),
      );
    }

    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        if (user == null) return const SizedBox();

        return Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: _activeCard != null
                ? LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: _activeCard!.tier == 'vip'
                        ? [
                            Colors.amber[700]!.withOpacity(0.8),
                            Colors.amber[900]!.withOpacity(0.8),
                          ]
                        : [
                            Colors.purple[700]!.withOpacity(0.8),
                            Colors.purple[900]!.withOpacity(0.8),
                          ],
                  )
                : LinearGradient(
                    colors: [Colors.grey[800]!, Colors.grey[850]!],
                  ),
            borderRadius: BorderRadius.circular(15),
            boxShadow: [
              BoxShadow(
                color: _activeCard != null
                    ? (_activeCard!.tier == 'vip'
                              ? Colors.amber
                              : Colors.purple)
                          .withOpacity(0.2)
                    : Colors.grey.withOpacity(0.1),
                blurRadius: 10,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: _activeCard != null
              ? _buildPremiumStatus()
              : _buildNormalStatus(),
        );
      },
    );
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

  Widget _buildPremiumStatus() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    _isVipPremium(_activeCard!.tier)
                        ? Icons.diamond
                        : (_isVip(_activeCard!.tier)
                              ? Icons.star
                              : Icons.card_giftcard),
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${_getTierDisplayName(_activeCard!.tier)} MEMBER',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1,
                      ),
                    ),
                    Text(
                      'Black-Tier Access',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: _activeCard!.isActive ? Colors.green : Colors.orange,
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

        const SizedBox(height: 15),

        // Benefits Preview
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildBenefitChip(
                _isVipPremium(_activeCard!.tier)
                    ? 'Encrypted GPS'
                    : 'Priority Booking',
                Icons.security,
              ),
              _buildBenefitChip('Hotel Partners', Icons.hotel),
              _buildBenefitChip('24/7 Support', Icons.support_agent),
            ],
          ),
        ),

        const SizedBox(height: 15),

        // Action Buttons
        Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const PremiumCardManagementScreen(),
                    ),
                  );
                },
                icon: const Icon(Icons.credit_card, size: 18),
                label: const Text('Manage Card'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: _activeCard!.tier == 'vip'
                      ? Colors.amber[800]
                      : Colors.purple[800],
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 10),
            Container(
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(10),
              ),
              child: IconButton(
                onPressed: () => _showCardDetails(),
                icon: const Icon(Icons.info_outline, color: Colors.white),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildNormalStatus() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey[700],
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.person, color: Colors.white, size: 24),
            ),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'NORMAL MEMBER',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
                Text(
                  'Standard Access',
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ],
        ),

        const SizedBox(height: 15),

        Container(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            color: Colors.blue[900]!.withOpacity(0.3),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: Colors.blue[700]!.withOpacity(0.5)),
          ),
          child: Column(
            children: [
              const Row(
                children: [
                  Icon(Icons.star, color: Colors.yellow, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Unlock Premium Benefits',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                'Get access to luxury vehicles, hotel partnerships, priority booking, and more with a Premium Digital Card.',
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) =>
                                const PremiumCardPaymentScreen(
                                  cardType: 'vip_premium',
                                  amount: 149.99,
                                ),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.purple[700],
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      child: const Text(
                        'Upgrade Now',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) =>
                              const PremiumCardActivationScreen(),
                        ),
                      );
                    },
                    child: const Text(
                      'Have a code?',
                      style: TextStyle(color: Colors.blue),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildBenefitChip(String text, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(right: 10),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: Colors.white, size: 14),
          const SizedBox(width: 6),
          Text(
            text,
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

  void _showCardDetails() {
    if (_activeCard == null) return;

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.grey[900],
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _activeCard!.tier == 'vip' ? Icons.diamond : Icons.star,
                  color: _activeCard!.tier == 'vip'
                      ? Colors.amber
                      : Colors.purple,
                  size: 30,
                ),
                const SizedBox(width: 12),
                Text(
                  '${_activeCard!.tier.toUpperCase()} Card Details',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            _buildDetailRow('Card Number', _activeCard!.maskedCardNumber),
            _buildDetailRow(
              'Status',
              _activeCard!.isActive ? 'Active' : 'Pending Activation',
            ),
            if (_activeCard!.expiresAt != null)
              _buildDetailRow(
                'Expires',
                '${_activeCard!.expiresAt!.day}/${_activeCard!.expiresAt!.month}/${_activeCard!.expiresAt!.year}',
              ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const PremiumCardManagementScreen(),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: _activeCard!.tier == 'vip'
                      ? Colors.amber[700]
                      : Colors.purple[700],
                  padding: const EdgeInsets.symmetric(vertical: 15),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                child: const Text(
                  'Manage Card',
                  style: TextStyle(
                    color: Colors.white,
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

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
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
}
