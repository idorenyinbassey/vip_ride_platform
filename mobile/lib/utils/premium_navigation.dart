import 'package:flutter/material.dart';
import '../screens/shared/premium_card_payment_screen.dart';
import '../screens/shared/premium_card_activation_screen.dart';
import '../screens/shared/premium_card_management_screen.dart';
import '../screens/shared/premium_upgrade_screen.dart';

class PremiumNavigationHelper {
  static const String premiumPayment = '/premium/payment';
  static const String premiumActivation = '/premium/activation';
  static const String premiumManagement = '/premium/management';
  static const String premiumUpgrade = '/premium/upgrade';

  static Map<String, WidgetBuilder> getRoutes() {
    return {
      // Note: Payment screen needs tier parameter, so it's better to use direct navigation
      premiumActivation: (context) => const PremiumCardActivationScreen(),
      premiumManagement: (context) => const PremiumCardManagementScreen(),
      premiumUpgrade: (context) => const PremiumUpgradeScreen(),
    };
  }

  static void navigateToPayment(BuildContext context, {String tier = 'vip'}) {
    // Convert tier to amount based on pricing
    double amount = tier == 'vip_premium' ? 149.99 : 99.99;

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            PremiumCardPaymentScreen(cardType: tier, amount: amount),
      ),
    );
  }

  static void navigateToActivation(
    BuildContext context, {
    String? verificationCode,
  }) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            PremiumCardActivationScreen(verificationCode: verificationCode),
      ),
    );
  }

  static void navigateToManagement(BuildContext context) {
    Navigator.pushNamed(context, premiumManagement);
  }

  static void navigateToUpgrade(BuildContext context) {
    Navigator.pushNamed(context, premiumUpgrade);
  }

  // Navigation helpers with results
  static Future<bool?> showPaymentScreen(
    BuildContext context, {
    String tier = 'vip',
  }) async {
    // Convert tier to amount based on pricing
    double amount = tier == 'vip_premium' ? 149.99 : 99.99;

    return await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) =>
            PremiumCardPaymentScreen(cardType: tier, amount: amount),
      ),
    );
  }

  static Future<bool?> showActivationScreen(
    BuildContext context, {
    String? verificationCode,
  }) async {
    return await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) =>
            PremiumCardActivationScreen(verificationCode: verificationCode),
      ),
    );
  }

  static Future<void> showUpgradeScreen(BuildContext context) async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const PremiumUpgradeScreen()),
    );
  }

  static Future<void> showManagementScreen(BuildContext context) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const PremiumCardManagementScreen(),
      ),
    );
  }

  // Modal helpers
  static Future<void> showPremiumBottomSheet(BuildContext context) async {
    await showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => const PremiumUpgradeBottomSheet(),
    );
  }
}

class PremiumUpgradeBottomSheet extends StatelessWidget {
  const PremiumUpgradeBottomSheet({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      decoration: const BoxDecoration(
        color: Colors.grey,
        borderRadius: BorderRadius.vertical(top: Radius.circular(25)),
      ),
      child: Column(
        children: [
          // Handle
          Container(
            margin: const EdgeInsets.symmetric(vertical: 10),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[600],
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // Header
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                const Icon(Icons.diamond, color: Colors.amber, size: 30),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Upgrade to Premium',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'Unlock exclusive benefits and features',
                        style: TextStyle(color: Colors.white70, fontSize: 14),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close, color: Colors.white),
                ),
              ],
            ),
          ),

          // Quick Benefits
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Column(
                children: [
                  _buildBenefitTile(
                    icon: Icons.directions_car,
                    title: 'Luxury Vehicles',
                    subtitle: 'Access to premium cars and professional drivers',
                    color: Colors.purple,
                  ),
                  _buildBenefitTile(
                    icon: Icons.hotel,
                    title: 'Hotel Partnerships',
                    subtitle: 'Book hotels with exclusive discounts',
                    color: Colors.blue,
                  ),
                  _buildBenefitTile(
                    icon: Icons.support_agent,
                    title: '24/7 Premium Support',
                    subtitle: 'Priority customer service and assistance',
                    color: Colors.green,
                  ),
                  _buildBenefitTile(
                    icon: Icons.security,
                    title: 'Enhanced Security (VIP)',
                    subtitle: 'Encrypted GPS tracking and SOS features',
                    color: Colors.amber,
                  ),
                ],
              ),
            ),
          ),

          // Action Buttons
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      PremiumNavigationHelper.navigateToUpgrade(context);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.purple[700],
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text(
                      'View All Plans',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                    PremiumNavigationHelper.navigateToActivation(context);
                  },
                  child: const Text(
                    'I have a verification code',
                    style: TextStyle(color: Colors.blue),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBenefitTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 15),
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 15),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: TextStyle(color: Colors.grey[400], fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
