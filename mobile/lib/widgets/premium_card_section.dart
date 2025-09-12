import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/premium_card_models.dart';
import '../../services/premium_card_service.dart';
import '../../services/auth_provider.dart';
import '../screens/shared/premium_card_purchase_screen.dart';
import '../screens/shared/premium_card_activation_screen.dart';

class PremiumCardSection extends StatefulWidget {
  const PremiumCardSection({super.key});

  @override
  State<PremiumCardSection> createState() => _PremiumCardSectionState();
}

class _PremiumCardSectionState extends State<PremiumCardSection> {
  final PremiumCardService _premiumCardService = PremiumCardService();
  List<PremiumDigitalCard> _cards = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadPremiumCards();
  }

  Future<void> _loadPremiumCards() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final cards = await _premiumCardService.getPremiumCards();
      setState(() {
        _cards = cards;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _refreshCards() async {
    await _loadPremiumCards();
  }

  void _navigateToPurchase() {
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => const PremiumCardPurchaseScreen(),
          ),
        )
        .then((_) {
          // Refresh cards when returning from purchase
          _refreshCards();
        });
  }

  void _navigateToActivation() {
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => const PremiumCardActivationScreen(),
          ),
        )
        .then((_) {
          // Refresh cards and user profile when returning from activation
          _refreshCards();
          Provider.of<AuthProvider>(
            context,
            listen: false,
          ).refreshUserProfile();
        });
  }

  Widget _buildCardItem(PremiumDigitalCard card) {
    final isActive = card.isActive;
    final isExpired = card.isExpired;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: isActive && !isExpired
            ? LinearGradient(
                colors: card.tier == 'premium'
                    ? [Colors.blue[700]!, Colors.blue[900]!]
                    : [Colors.purple[700]!, Colors.purple[900]!],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              )
            : LinearGradient(
                colors: [Colors.grey[400]!, Colors.grey[600]!],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Premium Digital Card',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                card.tierDisplayName.toUpperCase(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            card.maskedCardNumber,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontFamily: 'monospace',
              letterSpacing: 3,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Verification Code',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    card.verificationCode ?? 'Hidden',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontFamily: 'monospace',
                      letterSpacing: 2,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    'Status',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: _getStatusColor(card),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      _getStatusText(card),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          if (card.expiresAt != null && !isExpired) ...[
            const SizedBox(height: 12),
            Text(
              'Valid until ${card.expiresAt!.day}/${card.expiresAt!.month}/${card.expiresAt!.year}',
              style: TextStyle(
                color: Colors.white.withOpacity(0.8),
                fontSize: 12,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getStatusColor(PremiumDigitalCard card) {
    if (card.isExpired) return Colors.red[600]!;
    if (card.isActive) return Colors.green[600]!;
    return Colors.orange[600]!;
  }

  String _getStatusText(PremiumDigitalCard card) {
    if (card.isExpired) return 'EXPIRED';
    if (card.isActive) return 'ACTIVE';
    return 'PENDING';
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        children: [
          Icon(Icons.diamond_outlined, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'No Premium Cards',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Purchase a Premium Digital Card to unlock exclusive features and elevated service.',
            style: TextStyle(fontSize: 14, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: ElevatedButton(
                  onPressed: _navigateToPurchase,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Theme.of(context).primaryColor,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text(
                    'Purchase Card',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
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

  Widget _buildActionButtons() {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton.icon(
            onPressed: _navigateToActivation,
            icon: const Icon(Icons.verified_user),
            label: const Text('Activate Card'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _navigateToPurchase,
            icon: const Icon(Icons.add),
            label: const Text('Buy New'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).primaryColor,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Premium Digital Cards',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            IconButton(
              onPressed: _refreshCards,
              icon: const Icon(Icons.refresh),
            ),
          ],
        ),
        const SizedBox(height: 16),

        if (_isLoading)
          const Center(
            child: Padding(
              padding: EdgeInsets.all(32.0),
              child: CircularProgressIndicator(),
            ),
          )
        else if (_error != null)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.red[50],
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.red[200]!),
            ),
            child: Column(
              children: [
                Text(
                  'Error loading cards: $_error',
                  style: TextStyle(color: Colors.red[700]),
                ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: _refreshCards,
                  child: const Text('Retry'),
                ),
              ],
            ),
          )
        else if (_cards.isEmpty)
          _buildEmptyState()
        else ...[
          ...(_cards.map((card) => _buildCardItem(card)).toList()),
          const SizedBox(height: 16),
          _buildActionButtons(),
        ],
      ],
    );
  }
}
