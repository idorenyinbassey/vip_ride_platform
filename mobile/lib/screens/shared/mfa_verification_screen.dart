import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:pin_code_fields/pin_code_fields.dart';
import '../../services/auth_provider.dart';
import '../../models/mfa_models.dart';
import '../../widgets/custom_button.dart';
import 'mfa_setup_screen.dart';

class MfaVerificationScreen extends StatefulWidget {
  final MfaRequirement mfaRequirement;

  const MfaVerificationScreen({super.key, required this.mfaRequirement});

  @override
  State<MfaVerificationScreen> createState() => _MfaVerificationScreenState();
}

class _MfaVerificationScreenState extends State<MfaVerificationScreen> {
  String _currentCode = '';
  String _selectedMethod = '';
  bool _isLoading = false;
  String _statusMessage = '';

  @override
  void initState() {
    super.initState();
    // Select the first available method
    if (widget.mfaRequirement.mfaMethods.isNotEmpty) {
      _selectedMethod = widget.mfaRequirement.mfaMethods.first;
    }
  }

  String _getMethodDisplayName(String method) {
    switch (method) {
      case 'totp':
        return 'Authenticator App';
      case 'sms':
        return 'SMS';
      case 'email':
        return 'Email';
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
      default:
        return Icons.security;
    }
  }

  String _getInstructionText(String method) {
    switch (method) {
      case 'totp':
        return 'Enter the 6-digit code from your authenticator app';
      case 'sms':
        return 'Enter the 6-digit code sent to your phone';
      case 'email':
        return 'Enter the 6-digit code sent to your email';
      default:
        return 'Enter the verification code';
    }
  }

  Future<void> _sendCode() async {
    if (widget.mfaRequirement.tempToken == null) return;

    setState(() {
      _isLoading = true;
      _statusMessage = 'Sending code...';
    });

    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      bool success = false;

      switch (_selectedMethod) {
        case 'sms':
          success = await authProvider.sendMfaSms(
            widget.mfaRequirement.tempToken!,
          );
          break;
        case 'email':
          success = await authProvider.sendMfaEmail(
            widget.mfaRequirement.tempToken!,
          );
          break;
      }

      if (success) {
        setState(() {
          _statusMessage = 'Code sent successfully!';
        });
      } else {
        setState(() {
          _statusMessage = 'Failed to send code. Please try again.';
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = 'Error: ${e.toString()}';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });

      // Clear status message after 3 seconds
      Future.delayed(const Duration(seconds: 3), () {
        if (mounted) {
          setState(() {
            _statusMessage = '';
          });
        }
      });
    }
  }

  Future<void> _verifyCode() async {
    if (_currentCode.length != 6 || widget.mfaRequirement.tempToken == null) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final result = await authProvider.verifyMfa(
        widget.mfaRequirement.tempToken!,
        _currentCode,
        _selectedMethod,
      );

      if (mounted) {
        if (result.isSuccess) {
          if (result.requiresMfaSetup) {
            // Navigate to MFA setup screen
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (context) => const MfaSetupScreen()),
            );
          } else {
            // MFA verification successful, navigation will be handled by AuthProvider
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Authentication successful!'),
                backgroundColor: Colors.green,
              ),
            );
          }
        } else {
          setState(() {
            _statusMessage =
                result.error ?? 'Verification failed. Please try again.';
          });
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Verification failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
        // Clear the entered code
        setState(() {
          _currentCode = '';
        });
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Multi-Factor Authentication'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Colors.black,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Header
              const SizedBox(height: 20),
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: Theme.of(context).primaryColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(50),
                ),
                child: Icon(
                  Icons.security,
                  size: 50,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'Additional Security Required',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),

              // Method Selection
              if (widget.mfaRequirement.mfaMethods.length > 1) ...[
                Text(
                  'Choose verification method:',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 16),
                ...widget.mfaRequirement.mfaMethods.map((method) {
                  return RadioListTile<String>(
                    title: Row(
                      children: [
                        Icon(_getMethodIcon(method)),
                        const SizedBox(width: 12),
                        Text(_getMethodDisplayName(method)),
                      ],
                    ),
                    value: method,
                    groupValue: _selectedMethod,
                    onChanged: (value) {
                      setState(() {
                        _selectedMethod = value!;
                        _currentCode = '';
                      });
                    },
                  );
                }),
                const SizedBox(height: 20),
              ],

              // Instructions
              Text(
                _getInstructionText(_selectedMethod),
                style: Theme.of(
                  context,
                ).textTheme.bodyLarge?.copyWith(color: Colors.grey[600]),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // Send Code Button (for SMS/Email)
              if (_selectedMethod == 'sms' || _selectedMethod == 'email') ...[
                CustomButton(
                  onPressed: _isLoading ? null : _sendCode,
                  text: 'Send Code',
                  isLoading: _isLoading && _statusMessage.contains('Sending'),
                ),
                const SizedBox(height: 16),
              ],

              // Status Message
              if (_statusMessage.isNotEmpty) ...[
                Text(
                  _statusMessage,
                  style: TextStyle(
                    color:
                        _statusMessage.contains('Error') ||
                            _statusMessage.contains('Failed')
                        ? Colors.red
                        : Colors.green,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // PIN Code Input
              PinCodeTextField(
                appContext: context,
                length: 6,
                onChanged: (value) {
                  setState(() {
                    _currentCode = value;
                  });
                },
                onCompleted: (value) {
                  _verifyCode();
                },
                pinTheme: PinTheme(
                  shape: PinCodeFieldShape.box,
                  borderRadius: BorderRadius.circular(8),
                  fieldHeight: 56,
                  fieldWidth: 48,
                  activeFillColor: Colors.white,
                  selectedFillColor: Colors.white,
                  inactiveFillColor: Colors.grey[100],
                  activeColor: Theme.of(context).primaryColor,
                  selectedColor: Theme.of(context).primaryColor,
                  inactiveColor: Colors.grey[300],
                ),
                enableActiveFill: true,
                keyboardType: TextInputType.number,
                textStyle: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 32),

              // Verify Button
              CustomButton(
                onPressed: _currentCode.length == 6 && !_isLoading
                    ? _verifyCode
                    : null,
                text: 'Verify',
                isLoading: _isLoading && !_statusMessage.contains('Sending'),
              ),
              const Spacer(),

              // Help Text
              Text(
                "Having trouble? Contact support for assistance.",
                style: Theme.of(
                  context,
                ).textTheme.bodySmall?.copyWith(color: Colors.grey[500]),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
