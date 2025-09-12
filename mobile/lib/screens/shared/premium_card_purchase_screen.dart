import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/premium_card_models.dart';
import '../../services/premium_card_service.dart';
import '../../services/auth_provider.dart';
import '../../widgets/custom_button.dart';
import 'premium_card_activation_screen.dart';
import 'login_screen.dart';

class PremiumCardPurchaseScreen extends StatefulWidget {
  const PremiumCardPurchaseScreen({super.key});

  @override
  State<PremiumCardPurchaseScreen> createState() =>
      _PremiumCardPurchaseScreenState();
}

class _PremiumCardPurchaseScreenState extends State<PremiumCardPurchaseScreen> {
  final PremiumCardService _premiumCardService = PremiumCardService();

  String _selectedTier = 'vip';
  String _selectedPaymentMethod = 'stripe';
  bool _isLoading = false;
  PremiumDigitalCard? _purchasedCard;

  final Map<String, Map<String, dynamic>> _tierInfo = {
    'vip': {
      'title': 'VIP',
      'price': 99.99,
      'validity': 12,
      'features': [
        'Luxury vehicle access',
        'Priority ride matching',
        'Concierge services',
        'Hotel partnerships',
        'Enhanced customer support',
        'MFA security required',
      ],
      'color': Colors.blue,
    },
    'vip_premium': {
      'title': 'VIP Premium',
      'price': 149.99,
      'validity': 18,
      'features': [
        'All VIP features',
        'Encrypted GPS tracking',
        'SOS emergency protocols',
        'Trusted driver verification',
        'Discreet booking mode',
        'Control Center monitoring',
        'Biometric MFA support',
      ],
      'color': Colors.purple,
    },
  };

  Future<void> _purchaseCard() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
    });

    try {
      // Generate payment tokens based on method
      String? paymentToken;
      String? paymentIntentId;

      debugPrint('🚀 Starting purchase process...');
      debugPrint('  - Tier: $_selectedTier');
      debugPrint('  - Payment Method: $_selectedPaymentMethod');

      if (_selectedPaymentMethod == 'stripe') {
        // Generate Stripe payment intent and method IDs
        paymentIntentId = 'pi_test_${DateTime.now().millisecondsSinceEpoch}';
        paymentToken = 'pm_test_${DateTime.now().millisecondsSinceEpoch}';
        debugPrint('  - Generated Stripe Payment Intent: $paymentIntentId');
        debugPrint('  - Generated Payment Method: $paymentToken');
      } else if (_selectedPaymentMethod == 'google_pay') {
        paymentToken = 'gp_token_${DateTime.now().millisecondsSinceEpoch}';
        debugPrint('  - Generated Google Pay Token: $paymentToken');
      } else if (_selectedPaymentMethod == 'paystack') {
        paymentToken = 'ps_token_${DateTime.now().millisecondsSinceEpoch}';
        debugPrint('  - Generated Paystack Token: $paymentToken');
      } else if (_selectedPaymentMethod == 'flutterwave') {
        paymentToken = 'flw_token_${DateTime.now().millisecondsSinceEpoch}';
        debugPrint('  - Generated Flutterwave Token: $paymentToken');
      }

      final card = await _premiumCardService.purchasePremiumCard(
        tier: _selectedTier,
        paymentMethod: _selectedPaymentMethod,
        paymentToken: paymentToken,
        paymentIntentId: paymentIntentId,
      );

      debugPrint('✅ Purchase successful!');
      debugPrint('  - Card: ${card.cardNumber}');
      debugPrint('  - Status: ${card.status}');

      setState(() {
        _purchasedCard = card;
        _isLoading = false;
      });

      if (mounted) {
        // Refresh user profile to get updated tier
        final authProvider = Provider.of<AuthProvider>(context, listen: false);
        try {
          await authProvider.refreshProfile();
          debugPrint('✅ User profile refreshed after purchase');
        } catch (e) {
          debugPrint('⚠️ Failed to refresh profile: $e');
        }

        // Show success dialog with next steps
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.green),
                SizedBox(width: 8),
                Text('Purchase Successful!'),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '🎉 Your ${_selectedTier.toUpperCase()} card has been purchased!',
                ),
                const SizedBox(height: 16),
                Text('Card Number: ${card.cardNumber}'),
                Text('Verification Code: ${card.verificationCode}'),
                const SizedBox(height: 16),
                const Text(
                  'Next Steps:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const Text('1. Save these details securely'),
                const Text('2. Activate your card to unlock premium features'),
                const Text('3. Enjoy your upgraded experience!'),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () async {
                  // Refresh user profile to update tier status
                  final authProvider = Provider.of<AuthProvider>(
                    context,
                    listen: false,
                  );
                  await authProvider.refreshProfile();

                  if (mounted) {
                    Navigator.of(context).pop(); // Close dialog
                    Navigator.of(context).pop(); // Return to previous screen
                    // The app will automatically navigate to BlackTierClientApp if tier was updated
                  }
                },
                child: const Text('Continue'),
              ),
              ElevatedButton(
                onPressed: () async {
                  // Refresh user profile to update tier status
                  final authProvider = Provider.of<AuthProvider>(
                    context,
                    listen: false,
                  );
                  await authProvider.refreshProfile();

                  if (mounted) {
                    Navigator.of(context).pop(); // Close dialog
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(
                        builder: (context) =>
                            const PremiumCardActivationScreen(),
                      ),
                    );
                  }
                },
                child: const Text('Activate Now'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      debugPrint('❌ Purchase failed: $e');
      setState(() {
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Purchase failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Widget _buildTierCard(String tier, Map<String, dynamic> info) {
    final bool isSelected = tier == _selectedTier;

    return Card(
      elevation: isSelected ? 8 : 2,
      color: isSelected ? info['color'].withOpacity(0.1) : null,
      child: InkWell(
        onTap: _purchasedCard == null
            ? () {
                setState(() {
                  _selectedTier = tier;
                });
              }
            : null,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.diamond, color: info['color'], size: 24),
                  const SizedBox(width: 8),
                  Text(
                    info['title'],
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isSelected ? info['color'] : null,
                    ),
                  ),
                  const Spacer(),
                  if (isSelected)
                    Icon(Icons.check_circle, color: info['color']),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                '\$${info['price']} • ${info['validity']} months',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: info['color'],
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 12),
              ...info['features']
                  .map<Widget>(
                    (feature) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        children: [
                          Icon(Icons.check, size: 16, color: info['color']),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              feature,
                              style: const TextStyle(fontSize: 14),
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                  .toList(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPaymentMethodSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Payment Method',
          style: Theme.of(
            context,
          ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        ...['stripe', 'flutterwave', 'paystack', 'google_pay'].map((method) {
          final Map<String, dynamic> methodInfo = {
            'stripe': {
              'title': 'Credit/Debit Card (Stripe)',
              'icon': Icons.credit_card,
            },
            'flutterwave': {
              'title': 'Flutterwave',
              'icon': Icons.payments_outlined,
            },
            'paystack': {
              'title': 'Paystack',
              'icon': Icons.account_balance_wallet,
            },
            'google_pay': {'title': 'Google Pay', 'icon': Icons.payment},
          }[method]!;

          return RadioListTile<String>(
            title: Row(
              children: [
                Icon(methodInfo['icon']),
                const SizedBox(width: 12),
                Text(methodInfo['title']),
              ],
            ),
            value: method,
            groupValue: _selectedPaymentMethod,
            onChanged: _purchasedCard == null
                ? (value) {
                    setState(() {
                      _selectedPaymentMethod = value!;
                    });
                  }
                : null,
          );
        }),
      ],
    );
  }

  Widget _buildPurchasedCardDisplay() {
    if (_purchasedCard == null) return const SizedBox.shrink();

    return Card(
      color: Colors.green[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Icon(Icons.check_circle, color: Colors.green[700]),
                const SizedBox(width: 8),
                Text(
                  'Card Purchased Successfully!',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.green[700],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey[300]!),
              ),
              child: Column(
                children: [
                  Text(
                    'Premium Digital Card',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _purchasedCard!.maskedCardNumber,
                    style: const TextStyle(
                      fontSize: 18,
                      fontFamily: 'monospace',
                      letterSpacing: 2,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${_purchasedCard!.tierDisplayName} • ${_purchasedCard!.statusDisplayName}',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  if (_purchasedCard!.verificationCode != null) ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.amber[50],
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: Colors.amber[300]!),
                      ),
                      child: Column(
                        children: [
                          Text(
                            'Activation Code',
                            style: TextStyle(
                              fontWeight: FontWeight.w600,
                              color: Colors.amber[700],
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _purchasedCard!.verificationCode!,
                            style: TextStyle(
                              fontSize: 20,
                              fontFamily: 'monospace',
                              fontWeight: FontWeight.bold,
                              color: Colors.amber[700],
                              letterSpacing: 2,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Use this code to activate your premium tier',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.amber[700],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: CustomButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed('/premium-activation');
                    },
                    text: 'Activate Now',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: CustomButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                    },
                    text: 'Done',
                    outlined: true,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Purchase Premium Card'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Colors.black,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Text(
                'Upgrade Your Experience',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Purchase a Premium Digital Card to unlock exclusive features and enhanced services.',
                style: Theme.of(
                  context,
                ).textTheme.bodyLarge?.copyWith(color: Colors.grey[600]),
              ),
              const SizedBox(height: 24),

              // Show purchased card if available
              _buildPurchasedCardDisplay(),

              if (_purchasedCard == null) ...[
                // Tier Selection
                Text(
                  'Choose Your Tier',
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),

                ..._tierInfo.entries.map(
                  (entry) => Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: _buildTierCard(entry.key, entry.value),
                  ),
                ),

                const SizedBox(height: 24),

                // Payment Method Selection
                _buildPaymentMethodSelector(),

                const SizedBox(height: 32),

                // Purchase Button
                Consumer<AuthProvider>(
                  builder: (context, authProvider, child) {
                    if (!authProvider.isLoggedIn) {
                      return Column(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.orange[100],
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.orange[300]!),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.info_outline,
                                  color: Colors.orange[700],
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Text(
                                    'Please login to purchase premium cards',
                                    style: TextStyle(color: Colors.orange[700]),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 16),
                          CustomButton(
                            onPressed: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(
                                  builder: (context) => const LoginScreen(),
                                ),
                              );
                            },
                            text: 'Login to Continue',
                            isLoading: false,
                          ),
                        ],
                      );
                    }

                    return CustomButton(
                      onPressed: _isLoading ? null : _purchaseCard,
                      text: _isLoading ? 'Processing...' : 'Purchase Card',
                      isLoading: _isLoading,
                    );
                  },
                ),

                const SizedBox(height: 16),

                // Terms and Conditions
                Text(
                  'By purchasing a Premium Digital Card, you agree to our Terms of Service and Privacy Policy. The card is valid for the specified duration and provides access to premium features.',
                  style: Theme.of(
                    context,
                  ).textTheme.bodySmall?.copyWith(color: Colors.grey[500]),
                  textAlign: TextAlign.center,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
