import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/auth_provider.dart';
import '../../services/user_service.dart';
import 'regular/regular_client_app.dart';
import 'vip/vip_client_app.dart';
import 'vip_premium/vip_premium_client_app.dart';

class UnifiedClientApp extends StatefulWidget {
  const UnifiedClientApp({super.key});

  @override
  State<UnifiedClientApp> createState() => _UnifiedClientAppState();
}

class _UnifiedClientAppState extends State<UnifiedClientApp> {
  final UserService _userService = UserService();
  String? _userTier;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _determineUserTier();
  }

  Future<void> _determineUserTier() async {
    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);

      // Force refresh user profile to get latest tier status
      await authProvider.refreshUserProfile();

      // Get fresh tier information
      final userProfile = await _userService.getCurrentUser();

      setState(() {
        _userTier =
            userProfile?.tierLevel?.toLowerCase() ??
            userProfile?.tier.toLowerCase() ??
            'regular';
        _isLoading = false;
      });

      print('🎯 User tier determined: $_userTier');
    } catch (e) {
      setState(() {
        _error = 'Failed to load user profile: $e';
        _userTier = 'regular'; // Fallback to regular
        _isLoading = false;
      });
      print('❌ Error determining user tier: $e');
    }
  }

  // Method to refresh user tier (called after card activation)
  Future<void> refreshUserTier() async {
    print('🔄 Refreshing user tier...');
    setState(() {
      _isLoading = true;
    });
    await _determineUserTier();
  }

  // Static method to refresh tier from anywhere in the app
  static Future<void> refreshTierGlobally(BuildContext context) async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    await authProvider.refreshUserTier();

    // If we're currently in UnifiedClientApp, trigger a rebuild
    final currentRoute = ModalRoute.of(context)?.settings.name;
    if (currentRoute == null) {
      // We're likely in the main app, trigger navigation refresh
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const UnifiedClientApp()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: Colors.grey[900],
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Colors.amber, Colors.orange],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.amber.withOpacity(0.3),
                      blurRadius: 15,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: const Icon(Icons.diamond, size: 48, color: Colors.white),
              ),
              const SizedBox(height: 20),
              const Text(
                'Loading VIP Experience...',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 30),
              const CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.amber),
              ),
            ],
          ),
        ),
      );
    }

    if (_error != null) {
      return Scaffold(
        backgroundColor: Colors.grey[900],
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: Colors.red[400]),
              const SizedBox(height: 20),
              Text(
                'Something went wrong',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                _error!,
                style: TextStyle(color: Colors.grey[400], fontSize: 14),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 30),
              ElevatedButton(
                onPressed: _determineUserTier,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.amber,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 30,
                    vertical: 15,
                  ),
                ),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    // Route to appropriate client app based on user tier
    return _buildClientAppForTier(_userTier!);
  }

  Widget _buildClientAppForTier(String tier) {
    switch (tier) {
      case 'vip':
        return TierTransitionWidget(
          tierName: 'VIP',
          child: const VipClientApp(),
        );
      case 'vip_premium':
      case 'premium':
        return TierTransitionWidget(
          tierName: 'VIP Premium',
          child: const VipPremiumClientApp(),
        );
      case 'regular':
      default:
        return TierTransitionWidget(
          tierName: 'Regular',
          child: const RegularClientApp(),
        );
    }
  }
}

// Helper widget for tier transition animations
class TierTransitionWidget extends StatefulWidget {
  final Widget child;
  final String tierName;

  const TierTransitionWidget({
    super.key,
    required this.child,
    required this.tierName,
  });

  @override
  State<TierTransitionWidget> createState() => _TierTransitionWidgetState();
}

class _TierTransitionWidgetState extends State<TierTransitionWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));

    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutBack));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Opacity(
          opacity: _fadeAnimation.value,
          child: Transform.scale(
            scale: _scaleAnimation.value,
            child: widget.child,
          ),
        );
      },
    );
  }
}

// Tier upgrade notification widget
class TierUpgradePrompt extends StatelessWidget {
  final String currentTier;
  final String nextTier;
  final VoidCallback onUpgrade;

  const TierUpgradePrompt({
    super.key,
    required this.currentTier,
    required this.nextTier,
    required this.onUpgrade,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.deepPurple[600]!, Colors.deepPurple[800]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.deepPurple.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.upgrade, color: Colors.white, size: 24),
              const SizedBox(width: 10),
              const Text(
                'Upgrade Available',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            'Upgrade from $currentTier to $nextTier for enhanced features',
            style: const TextStyle(color: Colors.white, fontSize: 14),
          ),
          const SizedBox(height: 15),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              TextButton(
                onPressed: () {
                  // Dismiss the prompt
                },
                child: const Text(
                  'Not Now',
                  style: TextStyle(color: Colors.white70),
                ),
              ),
              ElevatedButton(
                onPressed: onUpgrade,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.amber,
                  foregroundColor: Colors.black,
                ),
                child: const Text('Upgrade Now'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
