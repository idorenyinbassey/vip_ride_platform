import 'package:flutter/material.dart';
import 'vip_dashboard_screen.dart';
import 'vip_rides_screen.dart';
import 'vip_concierge_screen.dart';
import 'vip_profile_screen.dart';

class VipClientApp extends StatefulWidget {
  const VipClientApp({super.key});

  @override
  State<VipClientApp> createState() => _VipClientAppState();
}

class _VipClientAppState extends State<VipClientApp> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _getSelectedScreen(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.grey[900],
        selectedItemColor: Colors.amber,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car),
            label: 'Rides',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.support_agent),
            label: 'Concierge',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }

  Widget _getSelectedScreen() {
    switch (_selectedIndex) {
      case 0:
        return const VipDashboardScreen();
      case 1:
        return const VipRidesScreen();
      case 2:
        return const VipConciergeScreen();
      case 3:
        return const VipProfileScreen();
      default:
        return const VipDashboardScreen();
    }
  }
}
