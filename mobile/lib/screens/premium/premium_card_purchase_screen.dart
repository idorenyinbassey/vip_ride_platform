import 'package:flutter/material.dart';
import '../../services/premium_card_service.dart';

class PremiumCardPurchaseScreen extends StatefulWidget {
  final String tier;

  const PremiumCardPurchaseScreen({super.key, required this.tier});

  @override
  State<PremiumCardPurchaseScreen> createState() =>
      _PremiumCardPurchaseScreenState();
}

class _PremiumCardPurchaseScreenState extends State<PremiumCardPurchaseScreen> {
  final PremiumCardService _premiumCardService = PremiumCardService();
  String? _selectedPaymentMethod;
  bool _isLoading = false;
  String? _errorMessage;

  final Map<String, double> _tierPrices = {'vip': 99.99, 'vip_premium': 149.99};

  final Map<String, String> _tierDescriptions = {
    'vip': 'Luxury cars + hotel booking',
    'vip_premium': 'Encrypted GPS + SOS + trusted drivers',
  };

  final List<Map<String, dynamic>> _paymentMethods = [
    {
      'id': 'stripe',
      'name': 'Credit/Debit Card',
      'icon': Icons.credit_card,
      'description': 'Visa, MasterCard, American Express',
    },
    {
      'id': 'google_pay',
      'name': 'Google Pay',
      'icon': Icons.payments,
      'description': 'Pay with Google Pay',
    },
    {
      'id': 'paystack',
      'name': 'Paystack',
      'icon': Icons.account_balance_wallet,
      'description': 'Bank transfer, cards, and more',
    },
    {
      'id': 'flutterwave',
      'name': 'Flutterwave',
      'icon': Icons.waves,
      'description': 'Cards, bank, USSD, and more',
    },
  ];

  @override
  Widget build(BuildContext context) {
    String displayTier = widget.tier == 'vip_premium'
        ? 'VIP Premium'
        : (widget.tier == 'vip' ? 'VIP' : widget.tier.toUpperCase());
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: Text('Purchase $displayTier Card'),
        backgroundColor: widget.tier == 'vip' ? Colors.black : Colors.grey[800],
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildCardPreview(),
            const SizedBox(height: 24),
            _buildPriceSection(),
            const SizedBox(height: 24),
            _buildPaymentMethodsSection(),
            const SizedBox(height: 24),
            if (_errorMessage != null) _buildErrorMessage(),
            const SizedBox(height: 32),
            _buildPurchaseButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildCardPreview() {
    String displayTier = widget.tier == 'vip_premium'
        ? 'VIP Premium'
        : (widget.tier == 'vip' ? 'VIP' : widget.tier.toUpperCase());
    return Container(
      width: double.infinity,
      height: 200,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: widget.tier == 'vip'
              ? [Colors.black, Colors.grey[800]!]
              : [Colors.grey[700]!, Colors.grey[900]!],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'VIP RIDE',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
                Icon(
                  widget.tier == 'vip' ? Icons.diamond : Icons.star,
                  color: Colors.white,
                  size: 28,
                ),
              ],
            ),
            const Spacer(),
            Text(
              displayTier,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
              ),
            ),
            Text(
              _tierDescriptions[widget.tier] ?? '',
              style: TextStyle(
                color: Colors.white.withOpacity(0.8),
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Text(
                  '•••• •••• •••• ••••',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 16,
                    letterSpacing: 2,
                  ),
                ),
                const Spacer(),
                Text(
                  'VALID',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPriceSection() {
    final price = _tierPrices[widget.tier] ?? 0.0;
    String displayTier = widget.tier == 'vip_premium'
        ? 'VIP Premium'
        : (widget.tier == 'vip' ? 'VIP' : widget.tier.toUpperCase());
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Subscription Details',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[800],
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('$displayTier Card', style: const TextStyle(fontSize: 16)),
              Text(
                '\$${price.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            widget.tier == 'vip'
                ? 'Valid for 18 months'
                : 'Valid for 12 months',
            style: TextStyle(color: Colors.grey[600], fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildPaymentMethodsSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Payment Method',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[800],
            ),
          ),
          const SizedBox(height: 12),
          ...List.generate(_paymentMethods.length, (index) {
            final method = _paymentMethods[index];
            return _buildPaymentMethodTile(method);
          }),
        ],
      ),
    );
  }

  Widget _buildPaymentMethodTile(Map<String, dynamic> method) {
    final isSelected = _selectedPaymentMethod == method['id'];
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(method['icon'] as IconData),
        title: Text(method['name'] as String),
        subtitle: Text(method['description'] as String),
        trailing: Radio<String>(
          value: method['id'] as String,
          groupValue: _selectedPaymentMethod,
          onChanged: (value) {
            setState(() {
              _selectedPaymentMethod = value;
              _errorMessage = null;
            });
          },
        ),
        onTap: () {
          setState(() {
            _selectedPaymentMethod = method['id'] as String;
            _errorMessage = null;
          });
        },
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        tileColor: isSelected ? Colors.blue[50] : Colors.transparent,
      ),
    );
  }

  Widget _buildErrorMessage() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red[200]!),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: Colors.red[600]),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _errorMessage!,
              style: TextStyle(color: Colors.red[700]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPurchaseButton() {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: _isLoading || _selectedPaymentMethod == null
            ? null
            : _handlePurchase,
        style: ElevatedButton.styleFrom(
          backgroundColor: widget.tier == 'vip'
              ? Colors.black
              : Colors.grey[800],
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: _isLoading
            ? const SizedBox(
                height: 24,
                width: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : Text(
                'Purchase for \$${_tierPrices[widget.tier]?.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
      ),
    );
  }

  Future<void> _handlePurchase() async {
    if (_selectedPaymentMethod == null) {
      setState(() {
        _errorMessage = 'Please select a payment method';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // Use debugPrint for better Flutter web compatibility
      debugPrint('🚀 Starting purchase process...');
      debugPrint('  - Tier: ${widget.tier}');
      debugPrint('  - Payment Method: $_selectedPaymentMethod');
      debugPrint('  - Amount: \$${_tierPrices[widget.tier]}');

      // For demonstration purposes, simulate payment token/intent creation
      String? paymentToken;
      String? paymentIntentId;

      if (_selectedPaymentMethod == 'stripe') {
        // In a real app, you would create a payment intent first
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
      }

      final result = await _premiumCardService.purchasePremiumCard(
        tier: widget.tier,
        paymentMethod: _selectedPaymentMethod!,
        paymentToken: paymentToken,
        paymentIntentId: paymentIntentId,
      );

      debugPrint('✅ Purchase successful!');
      debugPrint('  - Card: ${result.cardNumber}');
      debugPrint('  - Status: ${result.status}');

      if (mounted) {
        // Show success dialog
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => AlertDialog(
            title: Row(
              children: [
                Icon(Icons.check_circle, color: Colors.green),
                const SizedBox(width: 8),
                const Text('Success!'),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Your ${widget.tier.toUpperCase()} card has been purchased successfully!',
                ),
                const SizedBox(height: 16),
                Text('Card Number: ${result.cardNumber}'),
                Text('Verification Code: ${result.verificationCode}'),
                const SizedBox(height: 16),
                Text('Please save these details for activation.'),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop(); // Close dialog
                  Navigator.of(context).pop(); // Return to previous screen
                },
                child: const Text('Continue'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      debugPrint('❌ Purchase failed: $e');
      setState(() {
        _errorMessage = e.toString().replaceFirst('Exception: ', '');
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
}
