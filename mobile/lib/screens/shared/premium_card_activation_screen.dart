import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:pin_code_fields/pin_code_fields.dart';
import '../../services/premium_card_service.dart';
import '../../models/premium_card_models.dart';
import '../../widgets/custom_button.dart';
import '../../services/auth_provider.dart';

class PremiumCardActivationScreen extends StatefulWidget {
  final String? verificationCode; // Pre-filled if coming from purchase

  const PremiumCardActivationScreen({super.key, this.verificationCode});

  @override
  State<PremiumCardActivationScreen> createState() =>
      _PremiumCardActivationScreenState();
}

class _PremiumCardActivationScreenState
    extends State<PremiumCardActivationScreen> {
  final PremiumCardService _premiumCardService = PremiumCardService();
  final TextEditingController _codeController = TextEditingController();

  String _currentCode = '';
  bool _isLoading = false;
  bool _activationSuccessful = false;
  PremiumDigitalCard? _activatedCard;

  @override
  void initState() {
    super.initState();
    if (widget.verificationCode != null) {
      _currentCode = widget.verificationCode!;
      _codeController.text = widget.verificationCode!;
    }
  }

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _activateCard() async {
    if (_currentCode.length != 8 || _isLoading) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final card = await _premiumCardService.activatePremiumCard(
        verificationCode: _currentCode,
      );

      // Refresh user data to update tier
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      await authProvider.refreshUserProfile();

      setState(() {
        _activatedCard = card;
        _activationSuccessful = true;
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Premium card activated successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Activation failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );

        // Clear the entered code on error
        setState(() {
          _currentCode = '';
          _codeController.clear();
        });
      }
    }
  }

  Widget _buildSuccessView() {
    return Column(
      children: [
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: Colors.green[100],
            borderRadius: BorderRadius.circular(50),
          ),
          child: Icon(Icons.check_circle, size: 60, color: Colors.green[700]),
        ),
        const SizedBox(height: 24),
        Text(
          'Premium Activated!',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: Colors.green[700],
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Your premium tier has been activated successfully. You now have access to all premium features.',
          style: Theme.of(
            context,
          ).textTheme.bodyLarge?.copyWith(color: Colors.grey[600]),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 24),
        if (_activatedCard != null) ...[
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.green[50],
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.green[200]!),
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
                  _activatedCard!.maskedCardNumber,
                  style: const TextStyle(
                    fontSize: 18,
                    fontFamily: 'monospace',
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '${_activatedCard!.tierDisplayName} • Active',
                  style: TextStyle(
                    color: Colors.green[700],
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (_activatedCard!.expiresAt != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    'Valid until ${_activatedCard!.expiresAt!.day}/${_activatedCard!.expiresAt!.month}/${_activatedCard!.expiresAt!.year}',
                    style: TextStyle(color: Colors.grey[600], fontSize: 14),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 24),
        ],
        CustomButton(
          onPressed: () {
            // Navigate to the appropriate home screen
            Navigator.of(
              context,
            ).pushNamedAndRemoveUntil('/', (route) => false);
          },
          text: 'Continue to App',
        ),
      ],
    );
  }

  Widget _buildActivationForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        // Header
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: Theme.of(context).primaryColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(50),
          ),
          child: Icon(
            Icons.diamond,
            size: 50,
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 24),
        Text(
          'Activate Premium Card',
          style: Theme.of(
            context,
          ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Text(
          'Enter the 8-digit verification code from your Premium Digital Card to activate your premium tier.',
          style: Theme.of(
            context,
          ).textTheme.bodyLarge?.copyWith(color: Colors.grey[600]),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 32),

        // PIN Code Input
        PinCodeTextField(
          appContext: context,
          length: 8,
          controller: _codeController,
          onChanged: (value) {
            setState(() {
              _currentCode = value;
            });
          },
          onCompleted: (value) {
            _activateCard();
          },
          pinTheme: PinTheme(
            shape: PinCodeFieldShape.box,
            borderRadius: BorderRadius.circular(8),
            fieldHeight: 56,
            fieldWidth: 40,
            activeFillColor: Colors.white,
            selectedFillColor: Colors.white,
            inactiveFillColor: Colors.grey[100],
            activeColor: Theme.of(context).primaryColor,
            selectedColor: Theme.of(context).primaryColor,
            inactiveColor: Colors.grey[300],
          ),
          enableActiveFill: true,
          keyboardType: TextInputType.number,
          textStyle: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 32),

        // Activate Button
        CustomButton(
          onPressed: _currentCode.length == 8 && !_isLoading
              ? _activateCard
              : null,
          text: 'Activate Card',
          isLoading: _isLoading,
        ),
        const SizedBox(height: 24),

        // Help Section
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.blue[200]!),
          ),
          child: Column(
            children: [
              Row(
                children: [
                  Icon(Icons.help_outline, color: Colors.blue[700]),
                  const SizedBox(width: 8),
                  Text(
                    'Need Help?',
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: Colors.blue[700],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'If you don\'t have a verification code, you can purchase a Premium Digital Card from the profile section.',
                style: TextStyle(color: Colors.blue[700], fontSize: 14),
              ),
            ],
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Premium Activation'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Colors.black,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: _activationSuccessful
              ? _buildSuccessView()
              : _buildActivationForm(),
        ),
      ),
    );
  }
}
