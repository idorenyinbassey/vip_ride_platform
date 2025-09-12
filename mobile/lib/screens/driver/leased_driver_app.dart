import 'package:flutter/material.dart';
import 'leased_driver/leased_driver_home_screen.dart';
import 'leased_driver/leased_driver_rides_screen.dart';
import 'leased_driver/leased_driver_earnings_screen.dart';
import 'leased_driver/leased_driver_profile_screen.dart';

class LeasedDriverApp extends StatefulWidget {
  const LeasedDriverApp({super.key});

  @override
  State<LeasedDriverApp> createState() => _LeasedDriverAppState();
}

class _LeasedDriverAppState extends State<LeasedDriverApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const LeasedDriverHomeScreen(),
    const LeasedDriverRidesScreen(),
    const LeasedDriverEarningsScreen(),
    const LeasedDriverProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _currentIndex,
        selectedItemColor: Colors.purple[600],
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
