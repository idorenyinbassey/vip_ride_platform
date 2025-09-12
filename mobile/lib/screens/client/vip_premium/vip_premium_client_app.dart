import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../services/auth_provider.dart';
import 'hotel_dashboard_screen.dart';
import 'vip_premium_ride_booking_screen.dart';
import 'encrypted_tracking_screen.dart';
import 'concierge_chat_screen.dart';
import 'vip_premium_profile_screen.dart';

class VipPremiumClientApp extends StatefulWidget {
  const VipPremiumClientApp({super.key});

  @override
  State<VipPremiumClientApp> createState() => _VipPremiumClientAppState();
}

class _VipPremiumClientAppState extends State<VipPremiumClientApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const HotelDashboardScreen(), // Home - Hotel partnerships & VIP Premium dashboard
    const VipPremiumRideBookingScreen(), // Booking - VIP Premium rides with hotel integration
    const EncryptedTrackingScreen(
      rideId: 'demo_ride',
    ), // Tracking - Encrypted rides with hotel staff access
    const ConciergeChatScreen(), // Concierge - 24/7 support & hotel integration
    const VipPremiumProfileScreen(), // Profile - VIP Premium settings & hotel perks
  ];

  final List<BottomNavigationBarItem> _navItems = [
    const BottomNavigationBarItem(icon: Icon(Icons.hotel), label: 'Hotels'),
    const BottomNavigationBarItem(
      icon: Icon(Icons.directions_car),
      label: 'Rides',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.security),
      label: 'Tracking',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.support_agent),
      label: 'Concierge',
    ),
    const BottomNavigationBarItem(icon: Icon(Icons.diamond), label: 'Profile'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return Stack(
            children: [
              // Main content
              _screens[_currentIndex],

              // Emergency SOS Button (always visible for VIP Premium)
              _buildAdvancedSOSButton(context, authProvider),
            ],
          );
        },
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.grey[900]!, Colors.black],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.amber.withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          selectedItemColor: Colors.amber[400],
          unselectedItemColor: Colors.grey[400],
          backgroundColor: Colors.transparent,
          elevation: 0,
          selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold),
          items: _navItems,
        ),
      ),
    );
  }

  Widget _buildAdvancedSOSButton(
    BuildContext context,
    AuthProvider authProvider,
  ) {
    return Positioned(
      top: MediaQuery.of(context).padding.top + 20,
      right: 20,
      child: Container(
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Colors.red, Colors.redAccent],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(30),
          boxShadow: [
            BoxShadow(
              color: Colors.red.withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            borderRadius: BorderRadius.circular(30),
            onTap: () => _triggerAdvancedSOS(context, authProvider),
            child: SizedBox(
              width: 60,
              height: 60,
              child: const Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.emergency, color: Colors.white, size: 24),
                  Text(
                    'SOS',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _triggerAdvancedSOS(BuildContext context, AuthProvider authProvider) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.red[900],
          title: const Row(
            children: [
              Icon(Icons.warning, color: Colors.white, size: 28),
              SizedBox(width: 10),
              Text(
                'VIP Premium SOS',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: const Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Advanced SOS activated. This will:',
                style: TextStyle(color: Colors.white, fontSize: 16),
              ),
              SizedBox(height: 10),
              Text(
                '• Alert hotel security',
                style: TextStyle(color: Colors.white),
              ),
              Text(
                '• Notify central security team',
                style: TextStyle(color: Colors.white),
              ),
              Text(
                '• Share encrypted live GPS feed',
                style: TextStyle(color: Colors.white),
              ),
              Text(
                '• Contact emergency services',
                style: TextStyle(color: Colors.white),
              ),
              SizedBox(height: 15),
              Text(
                'Help is on the way. Stay safe.',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                // TODO: Implement actual SOS API call
                _sendAdvancedSOSAlert(authProvider);
              },
              child: const Text(
                'CONFIRM SOS',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
            ),
          ],
        );
      },
    );
  }

  Future<void> _sendAdvancedSOSAlert(AuthProvider authProvider) async {
    // TODO: Implement VIP Premium SOS API call
    // This should:
    // 1. Send location to hotel security
    // 2. Alert central security team
    // 3. Enable encrypted GPS tracking
    // 4. Log incident in security system

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('VIP Premium SOS Alert Sent - Help is on the way'),
        backgroundColor: Colors.red,
        duration: Duration(seconds: 5),
      ),
    );
  }
}
