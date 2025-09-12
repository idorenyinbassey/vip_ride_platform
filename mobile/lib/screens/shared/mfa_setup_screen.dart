import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:pin_code_fields/pin_code_fields.dart';
import '../../services/auth_provider.dart';
import '../../services/api_service.dart';
import '../../widgets/custom_button.dart';
import '../../config/theme.dart';

class MfaSetupScreen extends StatefulWidget {
  final bool isRequired;
  final String? recommendedMethod;
  final List<String> availableMethods;

  const MfaSetupScreen({
    super.key,
    this.isRequired = false,
    this.recommendedMethod,
    this.availableMethods = const ['totp', 'sms', 'email'],
  });

  @override
  State<MfaSetupScreen> createState() => _MfaSetupScreenState();
}

class _MfaSetupScreenState extends State<MfaSetupScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  int _currentStep = 0;
  String _selectedMethod = '';
  bool _isLoading = false;
  String _statusMessage = '';
  String _errorMessage = '';

  // TOTP specific
  String? _totpSecret;
  String? _totpQrCode;
  String _verificationCode = '';

  // SMS/Email specific
  String _contactInfo = '';
  bool _codeSent = false;

  @override
  void initState() {
    super.initState();
    _selectedMethod = widget.recommendedMethod ?? widget.availableMethods.first;
    _tabController = TabController(
      length: widget.availableMethods.length,
      vsync: this,
    );

    // Set initial tab based on recommended method
    if (widget.recommendedMethod != null) {
      final index = widget.availableMethods.indexOf(widget.recommendedMethod!);
      if (index >= 0) {
        _tabController.index = index;
      }
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _onMethodChanged() {
    setState(() {
      _selectedMethod = widget.availableMethods[_tabController.index];
      _currentStep = 0;
      _errorMessage = '';
      _statusMessage = '';
      _totpSecret = null;
      _totpQrCode = null;
      _verificationCode = '';
      _contactInfo = '';
      _codeSent = false;
    });
  }

  Future<void> _setupMfaMethod() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
      _errorMessage = '';
      _statusMessage = 'Setting up $_selectedMethod...';
    });

    try {
      final apiService = context.read<ApiService>();

      if (_selectedMethod == 'totp') {
        await _setupTotp();
      } else if (_selectedMethod == 'sms') {
        await _setupSms();
      } else if (_selectedMethod == 'email') {
        await _setupEmail();
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Setup failed: ${e.toString()}';
        _statusMessage = '';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _setupTotp() async {
    final apiService = ApiService();

    if (_currentStep == 0) {
      // Step 1: Generate TOTP secret and QR code
      final response = await apiService.setupMfa('totp');
      setState(() {
        _totpSecret = response['secret'];
        _totpQrCode = response['qr_code'];
        _currentStep = 1;
        _statusMessage = 'Scan the QR code with your authenticator app';
      });
    } else if (_currentStep == 1) {
      // Step 2: Verify TOTP code
      if (_verificationCode.length != 6) {
        setState(() {
          _errorMessage = 'Please enter a 6-digit code';
        });
        return;
      }

      final response = await apiService.confirmMfa(
        method: 'totp',
        code: _verificationCode,
        qrSecret: _totpSecret,
      );

      if (response['active'] == true) {
        await _completeMfaSetup();
      }
    }
  }

  Future<void> _setupSms() async {
    final apiService = ApiService();

    if (_currentStep == 0) {
      // Step 1: Provide phone number
      if (_contactInfo.isEmpty) {
        setState(() {
          _errorMessage = 'Please enter your phone number';
        });
        return;
      }

      final response = await apiService.setupMfa(
        'sms',
        phoneNumber: _contactInfo,
      );
      setState(() {
        _currentStep = 1;
        _codeSent = true;
        _statusMessage = 'SMS code sent to $_contactInfo';
      });
    } else if (_currentStep == 1) {
      // Step 2: Verify SMS code
      await _verifySmsCode();
    }
  }

  Future<void> _setupEmail() async {
    final apiService = ApiService();

    if (_currentStep == 0) {
      // Step 1: Send email code
      final response = await apiService.setupMfa('email');
      setState(() {
        _currentStep = 1;
        _codeSent = true;
        _statusMessage = 'Email code sent';
      });
    } else if (_currentStep == 1) {
      // Step 2: Verify email code
      await _verifyEmailCode();
    }
  }

  Future<void> _verifySmsCode() async {
    if (_verificationCode.length < 4) {
      setState(() {
        _errorMessage = 'Please enter the verification code';
      });
      return;
    }

    final apiService = ApiService();
    final response = await apiService.confirmMfa(
      method: 'sms',
      code: _verificationCode,
    );

    if (response['verified'] == true) {
      await _completeMfaSetup();
    } else {
      setState(() {
        _errorMessage = 'Invalid verification code';
      });
    }
  }

  Future<void> _verifyEmailCode() async {
    if (_verificationCode.length < 4) {
      setState(() {
        _errorMessage = 'Please enter the verification code';
      });
      return;
    }

    final apiService = ApiService();
    final response = await apiService.confirmMfa(
      method: 'email',
      code: _verificationCode,
    );

    if (response['verified'] == true) {
      await _completeMfaSetup();
    } else {
      setState(() {
        _errorMessage = 'Invalid verification code';
      });
    }
  }

  Future<void> _completeMfaSetup() async {
    final apiService = ApiService();
    await apiService.completeMfaSetup();

    setState(() {
      _statusMessage = 'MFA setup completed successfully!';
    });

    // Also call the auth provider to mark MFA setup as complete
    if (mounted) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      await authProvider.completeMfaSetup();

      // Navigate back or to next screen
      Navigator.of(context).pop(true); // Return true to indicate success
    }
  }

  Widget _buildMethodTab(String method) {
    final methodName = _getMethodDisplayName(method);

    return Tab(
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_getMethodIcon(method)),
          const SizedBox(width: 8),
          Text(methodName),
        ],
      ),
    );
  }

  Widget _buildTotpSetup() {
    if (_currentStep == 0) {
      return Column(
        children: [
          const Icon(Icons.smartphone, size: 64, color: AppTheme.primaryColor),
          const SizedBox(height: 16),
          const Text(
            'Authenticator App Setup',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          const Text(
            'We\'ll generate a QR code for you to scan with your authenticator app (Google Authenticator, Authy, etc.)',
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          CustomButton(
            text: 'Generate QR Code',
            onPressed: _setupMfaMethod,
            isLoading: _isLoading,
          ),
        ],
      );
    } else {
      return Column(
        children: [
          if (_totpQrCode != null) ...[
            const Text(
              'Scan this QR code with your authenticator app:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(color: Colors.grey.shade300, blurRadius: 8),
                ],
              ),
              child: QrImageView(
                data: _totpQrCode!,
                version: QrVersions.auto,
                size: 200.0,
              ),
            ),
            const SizedBox(height: 16),
            if (_totpSecret != null) ...[
              const Text('Or enter this code manually:'),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: SelectableText(
                  _totpSecret!,
                  style: const TextStyle(fontFamily: 'monospace'),
                ),
              ),
            ],
            const SizedBox(height: 24),
            const Text('Enter the 6-digit code from your app:'),
            const SizedBox(height: 16),
            PinCodeTextField(
              appContext: context,
              length: 6,
              onChanged: (value) {
                setState(() {
                  _verificationCode = value;
                  _errorMessage = '';
                });
              },
              onCompleted: (value) {
                setState(() {
                  _verificationCode = value;
                });
                _setupMfaMethod();
              },
              keyboardType: TextInputType.number,
              pinTheme: PinTheme(
                shape: PinCodeFieldShape.box,
                borderRadius: BorderRadius.circular(8),
                fieldHeight: 50,
                fieldWidth: 40,
                activeFillColor: Colors.white,
                inactiveFillColor: Colors.grey.shade100,
                selectedFillColor: AppTheme.primaryColor.withOpacity(0.1),
              ),
              enableActiveFill: true,
            ),
            const SizedBox(height: 16),
            CustomButton(
              text: 'Verify & Complete Setup',
              onPressed: _verificationCode.length == 6 ? _setupMfaMethod : null,
              isLoading: _isLoading,
            ),
          ],
        ],
      );
    }
  }

  Widget _buildSmsSetup() {
    if (_currentStep == 0) {
      return Column(
        children: [
          const Icon(Icons.message, size: 64, color: AppTheme.primaryColor),
          const SizedBox(height: 16),
          const Text(
            'SMS Verification Setup',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          const Text(
            'Enter your phone number to receive verification codes via SMS',
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          TextFormField(
            decoration: const InputDecoration(
              labelText: 'Phone Number',
              hintText: '+1234567890',
              prefixIcon: Icon(Icons.phone),
              border: OutlineInputBorder(),
            ),
            keyboardType: TextInputType.phone,
            onChanged: (value) {
              setState(() {
                _contactInfo = value;
                _errorMessage = '';
              });
            },
          ),
          const SizedBox(height: 24),
          CustomButton(
            text: 'Send SMS Code',
            onPressed: _contactInfo.isNotEmpty ? _setupMfaMethod : null,
            isLoading: _isLoading,
          ),
        ],
      );
    } else {
      return _buildCodeVerification('SMS code sent to $_contactInfo');
    }
  }

  Widget _buildEmailSetup() {
    if (_currentStep == 0) {
      return Column(
        children: [
          const Icon(Icons.email, size: 64, color: AppTheme.primaryColor),
          const SizedBox(height: 16),
          const Text(
            'Email Verification Setup',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          const Text(
            'We\'ll send verification codes to your registered email address',
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          CustomButton(
            text: 'Send Email Code',
            onPressed: _setupMfaMethod,
            isLoading: _isLoading,
          ),
        ],
      );
    } else {
      return _buildCodeVerification('Email code sent');
    }
  }

  Widget _buildCodeVerification(String message) {
    return Column(
      children: [
        Icon(
          _selectedMethod == 'sms' ? Icons.message : Icons.email,
          size: 64,
          color: AppTheme.primaryColor,
        ),
        const SizedBox(height: 16),
        Text(message, style: const TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 24),
        const Text('Enter the verification code:'),
        const SizedBox(height: 16),
        PinCodeTextField(
          appContext: context,
          length: 6,
          onChanged: (value) {
            setState(() {
              _verificationCode = value;
              _errorMessage = '';
            });
          },
          onCompleted: (value) {
            setState(() {
              _verificationCode = value;
            });
            _setupMfaMethod();
          },
          keyboardType: TextInputType.number,
          pinTheme: PinTheme(
            shape: PinCodeFieldShape.box,
            borderRadius: BorderRadius.circular(8),
            fieldHeight: 50,
            fieldWidth: 40,
            activeFillColor: Colors.white,
            inactiveFillColor: Colors.grey.shade100,
            selectedFillColor: AppTheme.primaryColor.withOpacity(0.1),
          ),
          enableActiveFill: true,
        ),
        const SizedBox(height: 16),
        CustomButton(
          text: 'Verify Code',
          onPressed: _verificationCode.length >= 4 ? _setupMfaMethod : null,
          isLoading: _isLoading,
        ),
        const SizedBox(height: 16),
        TextButton(
          onPressed: _isLoading
              ? null
              : () {
                  setState(() {
                    _currentStep = 0;
                    _verificationCode = '';
                    _codeSent = false;
                  });
                },
          child: const Text('Resend Code'),
        ),
      ],
    );
  }

  String _getMethodDisplayName(String method) {
    switch (method) {
      case 'totp':
        return 'Authenticator App';
      case 'sms':
        return 'SMS';
      case 'email':
        return 'Email';
      case 'backup':
        return 'Backup Codes';
      default:
        return method.toUpperCase();
    }
  }

  IconData _getMethodIcon(String method) {
    switch (method) {
      case 'totp':
        return Icons.smartphone;
      case 'sms':
        return Icons.message;
      case 'email':
        return Icons.email;
      case 'backup':
        return Icons.backup;
      default:
        return Icons.security;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('MFA Setup'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        leading: widget.isRequired
            ? null
            : IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: () => Navigator.of(context).pop(),
              ),
      ),
      body: Column(
        children: [
          if (widget.isRequired) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: Colors.orange.shade100,
              child: Row(
                children: [
                  Icon(Icons.security, color: Colors.orange.shade700),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Multi-Factor Authentication is required for your VIP account',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.orange.shade700,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
          if (widget.availableMethods.length > 1) ...[
            TabBar(
              controller: _tabController,
              onTap: (index) => _onMethodChanged(),
              tabs: widget.availableMethods.map(_buildMethodTab).toList(),
              labelColor: AppTheme.primaryColor,
              unselectedLabelColor: Colors.grey,
              indicatorColor: AppTheme.primaryColor,
            ),
          ],
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  if (_statusMessage.isNotEmpty) ...[
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(
                        color: Colors.green.shade100,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _statusMessage,
                        style: TextStyle(color: Colors.green.shade700),
                      ),
                    ),
                  ],
                  if (_errorMessage.isNotEmpty) ...[
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(
                        color: Colors.red.shade100,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _errorMessage,
                        style: TextStyle(color: Colors.red.shade700),
                      ),
                    ),
                  ],
                  Expanded(
                    child: SingleChildScrollView(
                      child: _selectedMethod == 'totp'
                          ? _buildTotpSetup()
                          : _selectedMethod == 'sms'
                          ? _buildSmsSetup()
                          : _buildEmailSetup(),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
