import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/auth_provider.dart';
import '../../widgets/custom_text_field.dart';
import '../../widgets/custom_button.dart';
import '../../config/api_config.dart';
import 'mfa_verification_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  String _selectedUserType =
      AppConstants.userTypeClient; // Should be 'CUSTOMER'
  String _selectedTier =
      'normal'; // Default to normal, VIP requires card purchase
  String? _selectedDriverType;

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  bool _isCommonPassword(String password) {
    // List of common passwords to avoid
    const commonPasswords = [
      'password',
      '123456',
      '12345678',
      'qwerty',
      'abc123',
      'password123',
      '123456789',
      'welcome',
      'admin',
      'letmein',
      '1234567',
      'monkey',
      '123123',
      'dragon',
      'pass',
      'master',
    ];

    return commonPasswords.contains(password.toLowerCase()) ||
        password.toLowerCase().contains('password') ||
        RegExp(r'^1+$').hasMatch(password) || // all 1s
        RegExp(r'^(\d)\1+$').hasMatch(password); // repeated digits
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    final result = await authProvider.register(
      email: _emailController.text.trim(),
      password: _passwordController.text,
      firstName: _firstNameController.text.trim(),
      lastName: _lastNameController.text.trim(),
      phoneNumber: _phoneController.text.trim().isEmpty
          ? null
          : _phoneController.text.trim(),
      userType: _selectedUserType,
      tier: _selectedTier,
      driverType: _selectedDriverType,
    );

    if (!mounted) return;

    if (result.requiresMfa && result.mfaRequirement != null) {
      // Navigate to MFA verification screen for VIP/VIP Premium users
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) =>
              MfaVerificationScreen(mfaRequirement: result.mfaRequirement!),
        ),
      );
    } else if (result.isSuccess) {
      // Registration and login successful, go back to previous screen
      Navigator.of(context).pop();
    } else {
      // Show error message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            result.error ?? authProvider.error ?? 'Registration failed',
          ),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(title: const Text('Create Account'), centerTitle: true),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 20),

                  // User Type Selection
                  Text(
                    'Account Type',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: RadioListTile<String>(
                          title: const Text('Client'),
                          value: AppConstants.userTypeClient, // 'CUSTOMER'
                          groupValue: _selectedUserType,
                          onChanged: (value) {
                            setState(() {
                              _selectedUserType = value!;
                              _selectedDriverType = null;
                            });
                          },
                        ),
                      ),
                      Expanded(
                        child: RadioListTile<String>(
                          title: const Text('Driver'),
                          value: AppConstants.userTypeDriver, // 'DRIVER'
                          groupValue: _selectedUserType,
                          onChanged: (value) {
                            setState(() {
                              _selectedUserType = value!;
                              _selectedTier =
                                  'normal'; // Always start as normal
                              _selectedDriverType =
                                  AppConstants.driverTypeIndependent;
                            });
                          },
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Information about VIP upgrade
                  if (_selectedUserType == AppConstants.userTypeClient) ...[
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.blue[50],
                        border: Border.all(color: Colors.blue[200]!),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.info_outline, color: Colors.blue[700]),
                              const SizedBox(width: 8),
                              Text(
                                'Account Tier Information',
                                style: TextStyle(
                                  fontWeight: FontWeight.w600,
                                  color: Colors.blue[700],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'You\'ll start with a Regular account. To unlock VIP or VIP Premium features, you can purchase a VIP Digital Card after registration.',
                            style: TextStyle(
                              color: Colors.blue[700],
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ] else if (_selectedUserType ==
                      AppConstants.userTypeDriver) ...[
                    Text(
                      'Driver Type',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<String>(
                      initialValue: _selectedDriverType,
                      decoration: InputDecoration(
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        filled: true,
                        fillColor: Colors.grey[50],
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: AppConstants.driverTypeIndependent,
                          child: Text('Independent Driver'),
                        ),
                        DropdownMenuItem(
                          value: AppConstants.driverTypeFleetOwner,
                          child: Text('Fleet Owner'),
                        ),
                        DropdownMenuItem(
                          value: AppConstants.driverTypeFleetDriver,
                          child: Text('Fleet Driver'),
                        ),
                        DropdownMenuItem(
                          value: AppConstants.driverTypeLeased,
                          child: Text('Leased Driver'),
                        ),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedDriverType = value;
                        });
                      },
                    ),
                  ],

                  const SizedBox(height: 30),

                  // Personal Information
                  Text(
                    'Personal Information',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // First Name
                  CustomTextField(
                    controller: _firstNameController,
                    label: 'First Name',
                    prefixIcon: Icons.person_outline,
                    validator: (value) {
                      if (value?.isEmpty ?? true) {
                        return 'Please enter your first name';
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 16),

                  // Last Name
                  CustomTextField(
                    controller: _lastNameController,
                    label: 'Last Name',
                    prefixIcon: Icons.person_outline,
                    validator: (value) {
                      if (value?.isEmpty ?? true) {
                        return 'Please enter your last name';
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 16),

                  // Email
                  CustomTextField(
                    controller: _emailController,
                    label: 'Email',
                    keyboardType: TextInputType.emailAddress,
                    prefixIcon: Icons.email_outlined,
                    validator: (value) {
                      if (value?.isEmpty ?? true) {
                        return 'Please enter your email';
                      }
                      if (!RegExp(
                        r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$',
                      ).hasMatch(value!)) {
                        return 'Please enter a valid email';
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 16),

                  // Phone Number
                  CustomTextField(
                    controller: _phoneController,
                    label: 'Phone Number (Optional)',
                    keyboardType: TextInputType.phone,
                    prefixIcon: Icons.phone_outlined,
                  ),

                  const SizedBox(height: 16),

                  // Password
                  CustomTextField(
                    controller: _passwordController,
                    label: 'Password',
                    obscureText: _obscurePassword,
                    prefixIcon: Icons.lock_outline,
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword
                            ? Icons.visibility
                            : Icons.visibility_off,
                      ),
                      onPressed: () {
                        setState(() {
                          _obscurePassword = !_obscurePassword;
                        });
                      },
                    ),
                    validator: (value) {
                      if (value?.isEmpty ?? true) {
                        return 'Please enter a password';
                      }
                      if (value!.length < 8) {
                        return 'Password must be at least 8 characters';
                      }
                      // Check for common passwords
                      if (_isCommonPassword(value)) {
                        return 'Password is too common. Choose a stronger password';
                      }
                      // Check for at least one letter and one number
                      if (!RegExp(r'^(?=.*[A-Za-z])(?=.*\d)').hasMatch(value)) {
                        return 'Password must contain at least one letter and one number';
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 16),

                  // Confirm Password
                  CustomTextField(
                    controller: _confirmPasswordController,
                    label: 'Confirm Password',
                    obscureText: _obscureConfirmPassword,
                    prefixIcon: Icons.lock_outline,
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscureConfirmPassword
                            ? Icons.visibility
                            : Icons.visibility_off,
                      ),
                      onPressed: () {
                        setState(() {
                          _obscureConfirmPassword = !_obscureConfirmPassword;
                        });
                      },
                    ),
                    validator: (value) {
                      if (value?.isEmpty ?? true) {
                        return 'Please confirm your password';
                      }
                      if (value != _passwordController.text) {
                        return 'Passwords do not match';
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: 40),

                  // Register Button
                  Consumer<AuthProvider>(
                    builder: (context, authProvider, child) {
                      return CustomButton(
                        onPressed: authProvider.isLoading
                            ? null
                            : _handleRegister,
                        text: 'Create Account',
                        isLoading: authProvider.isLoading,
                      );
                    },
                  ),

                  const SizedBox(height: 20),

                  // Login Link
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Already have an account? ',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[600],
                        ),
                      ),
                      GestureDetector(
                        onTap: () {
                          Navigator.of(context).pop();
                        },
                        child: Text(
                          'Sign In',
                          style: Theme.of(context).textTheme.bodyMedium
                              ?.copyWith(
                                color: Theme.of(context).primaryColor,
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
