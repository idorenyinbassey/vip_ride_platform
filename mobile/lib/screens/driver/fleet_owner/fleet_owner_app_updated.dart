import 'package:flutter/material.dart';
import 'fleet_owner_dashboard_screen.dart';
import 'fleet_vehicle_management_screen.dart';
import 'fleet_driver_management_screen.dart';
import 'fleet_earnings_screen.dart';
import 'fleet_reports_screen.dart';

class FleetOwnerApp extends StatefulWidget {
  const FleetOwnerApp({super.key});

  @override
  State<FleetOwnerApp> createState() => _FleetOwnerAppState();
}

class _FleetOwnerAppState extends State<FleetOwnerApp> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const FleetOwnerDashboardScreen(),
    const FleetVehicleManagementScreen(),
    const FleetDriverManagementScreen(),
    const FleetEarningsScreen(),
    const FleetReportsScreen(),
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
        selectedItemColor: Colors.orange[600],
        unselectedItemColor: Colors.grey,
        backgroundColor: Colors.white,
        elevation: 8,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car),
            label: 'Vehicles',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.people), label: 'Drivers'),
          BottomNavigationBarItem(
            icon: Icon(Icons.attach_money),
            label: 'Earnings',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics),
            label: 'Reports',
          ),
        ],
      ),
    );
  }
}
