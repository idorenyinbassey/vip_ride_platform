import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../../../services/auth_provider.dart';
import '../../../services/card_activation_service.dart';
import '../../../services/api_service.dart';
import '../../../models/card_models.dart';
import '../../../widgets/loading_overlay.dart';
import 'mfa_setup_screen.dart';

class CardActivationScreen extends StatefulWidget {
  const CardActivationScreen({super.key});

  @override
  State<CardActivationScreen> createState() => _CardActivationScreenState();
}

class _CardActivationScreenState extends State<CardActivationScreen>
    with TickerProviderStateMixin {
  final CardActivationService _cardService = CardActivationService();
  final _formKey = GlobalKey<FormState>();
  final _serialController = TextEditingController();
  final _activationController = TextEditingController();

  late AnimationController _cardController;
  late AnimationController _shimmerController;
  late Animation<double> _cardFlipAnimation;
  late Animation<double> _shimmerAnimation;

  bool _isLoading = false;
  bool _isValidating = false;
  DigitalCard? _previewCard;
  CardTier? _detectedTier;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
    _cardController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _shimmerController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();

    _cardFlipAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _cardController, curve: Curves.easeInOut),
    );

    _shimmerAnimation = Tween<double>(
      begin: -1.0,
      end: 2.0,
    ).animate(_shimmerController);
  }

  @override
  void dispose() {
    _cardController.dispose();
    _shimmerController.dispose();
    _serialController.dispose();
    _activationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900],
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text(
          'Activate VIP Card',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: LoadingOverlay(
        isLoading: _isLoading,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeaderSection(),
                const SizedBox(height: 30),
                _buildCardPreview(),
                const SizedBox(height: 30),
                _buildInputSection(),
                const SizedBox(height: 30),
                _buildBenefitsSection(),
                const SizedBox(height: 40),
                _buildActivationButton(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeaderSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
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
                blurRadius: 10,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: Row(
            children: [
              const Icon(Icons.diamond, color: Colors.white, size: 32),
              const SizedBox(width: 15),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Upgrade to VIP',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      'Enter your VIP card details to unlock premium features',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCardPreview() {
    return AnimatedBuilder(
      animation: _cardFlipAnimation,
      builder: (context, child) {
        return Transform(
          alignment: Alignment.center,
          transform: Matrix4.identity()
            ..setEntry(3, 2, 0.001)
            ..rotateY(_cardFlipAnimation.value * 0.1),
          child: Container(
            height: 200,
            width: double.infinity,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color:
                      (_detectedTier != null
                              ? CardUtils.getTierColor(_detectedTier!)
                              : Colors.grey)
                          .withOpacity(0.3),
                  blurRadius: 15,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: _previewCard != null
                ? _buildActiveCardPreview()
                : _buildEmptyCardPreview(),
          ),
        );
      },
    );
  }

  Widget _buildActiveCardPreview() {
    final card = _previewCard!;
    final primaryColor = CardUtils.getTierColor(card.tier);
    final secondaryColor = CardUtils.getTierSecondaryColor(card.tier);

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: LinearGradient(
          colors: [primaryColor, secondaryColor],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Stack(
        children: [
          // Shimmer effect
          AnimatedBuilder(
            animation: _shimmerAnimation,
            builder: (context, child) {
              return Positioned.fill(
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    gradient: LinearGradient(
                      colors: [
                        Colors.transparent,
                        Colors.white.withOpacity(0.2),
                        Colors.transparent,
                      ],
                      stops: [0.0, 0.5, 1.0],
                      begin: Alignment(_shimmerAnimation.value - 1, 0),
                      end: Alignment(_shimmerAnimation.value, 0),
                    ),
                  ),
                ),
              );
            },
          ),

          // Card content
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      card.tier.displayName,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Icon(Icons.diamond, color: Colors.white, size: 24),
                  ],
                ),

                const Spacer(),

                Text(
                  card.displaySerialNumber,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 2,
                  ),
                ),

                const SizedBox(height: 10),

                Text(
                  'Status: ${card.status.displayName}',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyCardPreview() {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        color: Colors.grey[800],
        border: Border.all(
          color: Colors.grey[600]!,
          width: 2,
          style: BorderStyle.solid,
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.credit_card, size: 48, color: Colors.grey[500]),
          const SizedBox(height: 10),
          Text(
            'Enter card details to preview',
            style: TextStyle(color: Colors.grey[400], fontSize: 16),
          ),
        ],
      ),
    );
  }

  Widget _buildInputSection() {
    return Column(
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
        const SizedBox(height: 15),

        // Serial Number Input
        TextFormField(
          controller: _serialController,
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            labelText: 'Serial Number',
            hintText: 'VIP-XXXX-XXXX-XXXX',
            labelStyle: const TextStyle(color: Colors.grey),
            hintStyle: TextStyle(color: Colors.grey[600]),
            prefixIcon: const Icon(Icons.numbers, color: Colors.amber),
            filled: true,
            fillColor: Colors.grey[800],
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Colors.amber, width: 2),
            ),
          ),
          inputFormatters: [
            FilteringTextInputFormatter.allow(RegExp(r'[A-Z0-9\-]')),
            TextInputFormatter.withFunction((oldValue, newValue) {
              String formatted = CardUtils.formatSerialNumber(
                newValue.text.toUpperCase(),
              );
              return TextEditingValue(
                text: formatted,
                selection: TextSelection.collapsed(offset: formatted.length),
              );
            }),
          ],
          onChanged: _onSerialNumberChanged,
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Please enter the serial number';
            }
            if (!CardUtils.isValidSerialNumber(value)) {
              return 'Invalid serial number format';
            }
            return null;
          },
        ),

        const SizedBox(height: 20),

        // Activation Code Input
        TextFormField(
          controller: _activationController,
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            labelText: 'Activation Code',
            hintText: 'Enter 8-12 character code',
            labelStyle: const TextStyle(color: Colors.grey),
            hintStyle: TextStyle(color: Colors.grey[600]),
            prefixIcon: const Icon(Icons.key, color: Colors.amber),
            filled: true,
            fillColor: Colors.grey[800],
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Colors.amber, width: 2),
            ),
          ),
          inputFormatters: [
            FilteringTextInputFormatter.allow(RegExp(r'[A-Z0-9]')),
            LengthLimitingTextInputFormatter(12),
            TextInputFormatter.withFunction((oldValue, newValue) {
              return TextEditingValue(
                text: newValue.text.toUpperCase(),
                selection: newValue.selection,
              );
            }),
          ],
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Please enter the activation code';
            }
            if (!CardUtils.isValidActivationCode(value)) {
              return 'Invalid activation code format';
            }
            return null;
          },
        ),

        if (_errorMessage != null) ...[
          const SizedBox(height: 15),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.red.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.red.withOpacity(0.5)),
            ),
            child: Row(
              children: [
                const Icon(Icons.error, color: Colors.red, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _errorMessage!,
                    style: const TextStyle(color: Colors.red, fontSize: 14),
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildBenefitsSection() {
    if (_detectedTier == null) return const SizedBox.shrink();

    final benefits =
        _cardService.getTierBenefits()[_detectedTier!.name.toLowerCase()] ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${_detectedTier!.displayName} Benefits',
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 15),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.grey[800],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: CardUtils.getTierColor(_detectedTier!).withOpacity(0.5),
            ),
          ),
          child: Column(
            children: benefits.map((benefit) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Icon(
                      Icons.check_circle,
                      color: CardUtils.getTierColor(_detectedTier!),
                      size: 18,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        benefit,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildActivationButton() {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: _canActivate() ? _activateCard : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: _detectedTier != null
              ? CardUtils.getTierColor(_detectedTier!)
              : Colors.grey,
          foregroundColor: Colors.black,
          elevation: 8,
          shadowColor: _detectedTier != null
              ? CardUtils.getTierColor(_detectedTier!).withOpacity(0.4)
              : Colors.transparent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        child: _isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  color: Colors.black,
                  strokeWidth: 2,
                ),
              )
            : Text(
                'Activate ${_detectedTier?.displayName ?? 'VIP'} Card',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
      ),
    );
  }

  void _onSerialNumberChanged(String value) async {
    setState(() {
      _errorMessage = null;
      _detectedTier = CardUtils.getTierFromSerialNumber(value);
    });

    if (CardUtils.isValidSerialNumber(value)) {
      setState(() {
        _isValidating = true;
      });

      try {
        final card = await _cardService.getCardDetails(value);
        setState(() {
          _previewCard = card;
          _isValidating = false;
        });

        if (card != null) {
          _cardController.forward();
        } else {
          setState(() {
            _errorMessage = 'Card not found or invalid';
          });
        }
      } catch (e) {
        setState(() {
          _isValidating = false;
          _errorMessage = 'Error validating card';
        });
      }
    } else {
      setState(() {
        _previewCard = null;
      });
      _cardController.reverse();
    }
  }

  bool _canActivate() {
    return _previewCard != null &&
        _activationController.text.isNotEmpty &&
        CardUtils.isValidActivationCode(_activationController.text) &&
        !_isLoading;
  }

  Future<void> _activateCard() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final userId = authProvider.user?.id ?? '';

      final result = await _cardService.activateCard(
        serialNumber: _serialController.text,
        activationCode: _activationController.text,
        userId: userId,
      );

      if (result.success) {
        _showActivationSuccess(result);
      } else {
        setState(() {
          _errorMessage = result.message;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Activation failed: ${e.toString()}';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showActivationSuccess(CardActivationResult result) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[800],
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: CardUtils.getTierColor(result.card!.tier),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.diamond, size: 48, color: Colors.black),
              ),
              const SizedBox(height: 20),
              Text(
                'Congratulations!',
                style: TextStyle(
                  color: CardUtils.getTierColor(result.card!.tier),
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                'Your ${result.card!.tier.displayName} card has been activated successfully!',
                style: const TextStyle(color: Colors.white, fontSize: 16),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () async {
                  Navigator.of(context).pop(); // Close dialog

                  // Check if MFA setup is required for VIP/Premium users
                  if (result.card!.tier == CardTier.vip ||
                      result.card!.tier == CardTier.vipPremium) {
                    await _checkAndSetupMfa();
                  } else {
                    Navigator.of(context).pop(); // Go back to previous screen
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: CardUtils.getTierColor(result.card!.tier),
                  foregroundColor: Colors.black,
                ),
                child: const Text('Continue to VIP Experience'),
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _checkAndSetupMfa() async {
    try {
      // Check MFA status from backend
      final apiService = Provider.of<ApiService>(context, listen: false);
      final mfaStatus = await apiService.getMfaStatus();

      if (mfaStatus['needs_mfa_setup'] == true) {
        // Show MFA setup screen
        final setupResult = await Navigator.of(context).push<bool>(
          MaterialPageRoute(
            builder: (context) => MfaSetupScreen(
              isRequired: true,
              recommendedMethod: mfaStatus['recommended_method'],
              availableMethods: List<String>.from(
                mfaStatus['available_methods'] ?? ['totp'],
              ),
            ),
          ),
        );

        if (setupResult == true) {
          // MFA setup completed successfully
          _showMfaSetupCompleteDialog();
        } else {
          // User cancelled or failed MFA setup
          _showMfaSetupRequiredDialog();
        }
      } else {
        // MFA not required or already set up
        Navigator.of(context).pop(); // Go back to previous screen
      }
    } catch (e) {
      // If MFA check fails, still allow user to continue
      debugPrint('MFA check failed: $e');
      Navigator.of(context).pop(); // Go back to previous screen
    }
  }

  void _showMfaSetupCompleteDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[800],
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.security,
                  size: 48,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'Security Enhanced!',
                style: TextStyle(
                  color: Colors.green,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Your VIP account is now protected with Multi-Factor Authentication.',
                style: TextStyle(color: Colors.white, fontSize: 16),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pop(); // Close dialog
                  Navigator.of(context).pop(); // Go back to previous screen
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Enter VIP Dashboard'),
              ),
            ],
          ),
        );
      },
    );
  }

  void _showMfaSetupRequiredDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[800],
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.orange,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.warning, size: 48, color: Colors.white),
              ),
              const SizedBox(height: 20),
              const Text(
                'Security Setup Required',
                style: TextStyle(
                  color: Colors.orange,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Multi-Factor Authentication is required for VIP accounts. Please complete the setup to access all features.',
                style: TextStyle(color: Colors.white, fontSize: 16),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: TextButton(
                      onPressed: () {
                        Navigator.of(context).pop(); // Close dialog
                        Navigator.of(
                          context,
                        ).pop(); // Go back to previous screen
                      },
                      child: const Text(
                        'Later',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.of(context).pop(); // Close dialog
                        _checkAndSetupMfa(); // Try MFA setup again
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Setup Now'),
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
}
