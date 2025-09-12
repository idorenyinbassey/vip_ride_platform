import 'package:flutter/material.dart';
import 'fleet_driver_home_screen.dart';
import 'fleet_driver_rides_screen.dart';
import 'fleet_driver_earnings_screen.dart';
import 'fleet_driver_profile_screen.dart';

class FleetDriverApp extends StatefulWidget {
  const FleetDriverApp({super.key});

  @override
  State<FleetDriverApp> createState() => _FleetDriverAppState();
}

class _FleetDriverAppState extends State<FleetDriverApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const FleetDriverHomeScreen(),
    const FleetDriverRidesScreen(),
    const FleetDriverEarningsScreen(),
    const FleetDriverProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _currentIndex,
        selectedItemColor: Colors.blue[600],
        unselectedItemColor: Colors.grey[600],
        backgroundColor: Colors.white,
        elevation: 8,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car),
            label: 'Rides',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.monetization_on),
            label: 'Earnings',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
