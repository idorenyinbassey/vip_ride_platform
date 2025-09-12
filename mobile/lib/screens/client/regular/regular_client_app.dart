import 'package:flutter/material.dart';
import 'regular_rides_screen.dart';
import 'regular_profile_screen.dart';
import '../../ride/live_ride_booking_screen.dart';

class RegularClientApp extends StatefulWidget {
  const RegularClientApp({super.key});

  @override
  State<RegularClientApp> createState() => _RegularClientAppState();
}

class _RegularClientAppState extends State<RegularClientApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const LiveRideBookingScreen(), // Changed to live booking screen
    const RegularRidesScreen(),
    const RegularProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.white,
        selectedItemColor: Colors.blue,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Book Ride'),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car),
            label: 'My Rides',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
